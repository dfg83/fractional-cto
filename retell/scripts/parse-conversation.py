#!/usr/bin/env python3
"""
Stage 1 Parser: Transform raw Claude Code JSONL conversations into clean event streams.

Deterministic, zero-token processing. Extracts signal from noise:
  - 15 MB raw → ~338 KB signal (typical)
  - Drops tool_result blocks, progress entries, file snapshots, queue ops
  - Preserves user text, assistant text, thinking blocks, tool names
  - Detects session boundaries and context continuations
  - Inventories subagents without inlining their content

Usage:
  python3 parse-conversation.py <uuid-or-path> [--output-dir DIR] [--include-subagents]
  python3 parse-conversation.py 8c439a20 --output-dir ./artifacts
  python3 parse-conversation.py ~/.claude/projects/-Users-foo/8c439a20-f830-465b-bc74-270ca9991867.jsonl

Output:
  events.json    — ordered array of signal events
  manifest.json  — conversation metadata and token estimates
"""

import argparse
import base64
import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# --- Noise detection ---

NOISE_MARKERS = [
    "<local-command-",
    "<command-name>",
    "[Request interrupted",
]

SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),           # OpenAI / Anthropic keys
    re.compile(r"ghp_[a-zA-Z0-9]{36,}"),           # GitHub PATs
    re.compile(r"AKIA[A-Z0-9]{16}"),               # AWS access keys
    re.compile(r"Bearer\s+[a-zA-Z0-9\-._~+/]+=*"), # Bearer tokens
    re.compile(r"password\s*=\s*['\"][^'\"]+['\"]"), # password= assignments
]


def is_noise_text(text: str) -> bool:
    """Return True if text is system-generated noise, not real user input."""
    if not text or not text.strip():
        return True
    return any(marker in text for marker in NOISE_MARKERS)


def clean_text(text: str) -> str:
    """Strip system-reminder tags from text."""
    return SYSTEM_REMINDER_RE.sub("", text).strip()


def scan_secrets(text: str) -> list[str]:
    """Scan text for common secret patterns. Returns list of warnings."""
    warnings = []
    for pattern in SECRET_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            preview = match[:20] + "..." if len(match) > 20 else match
            warnings.append(f"Possible secret: {preview}")
    return warnings


def extract_user_text(content) -> str:
    """Extract user-visible text from a message content field."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    texts.append(text)
        return "\n".join(texts)
    return ""


def extract_images(content, event_index: int, assets_dir: str) -> list[dict]:
    """Extract base64 images from tool_result blocks. Save to assets/."""
    images = []
    if not isinstance(content, list):
        return images
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result":
            inner = block.get("content", [])
            if isinstance(inner, list):
                for item in inner:
                    if isinstance(item, dict) and item.get("type") == "image":
                        source = item.get("source", {})
                        if source.get("type") == "base64":
                            img_data = source.get("data", "")
                            media_type = source.get("media_type", "image/png")
                            ext = "png" if "png" in media_type else "jpeg"
                            idx = len(images)
                            filename = f"screenshot-{event_index:03d}-{idx}.{ext}"
                            filepath = os.path.join(assets_dir, filename)
                            try:
                                with open(filepath, "wb") as f:
                                    f.write(base64.b64decode(img_data))
                                images.append({
                                    "filename": filename,
                                    "media_type": media_type,
                                    "event_index": event_index,
                                })
                            except Exception:
                                pass
    return images


def extract_agent_id_from_tool_result(content) -> tuple[str | None, dict | None]:
    """Extract agentId and usage stats from a tool_result containing Agent output."""
    if not isinstance(content, list):
        return None, None
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result":
            result_content = block.get("content", "")
            if isinstance(result_content, list):
                for item in result_content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        result_content = item.get("text", "")
                        break
                else:
                    continue
            if not isinstance(result_content, str):
                continue
            agent_match = re.search(r"agentId:\s*([a-f0-9]+)", result_content)
            if agent_match:
                agent_id = agent_match.group(1)
                usage = {}
                token_match = re.search(r"total_tokens:\s*(\d+)", result_content)
                if token_match:
                    usage["total_tokens"] = int(token_match.group(1))
                duration_match = re.search(r"duration_ms:\s*(\d+)", result_content)
                if duration_match:
                    usage["duration_ms"] = int(duration_match.group(1))
                tool_uses_match = re.search(r"tool_uses:\s*(\d+)", result_content)
                if tool_uses_match:
                    usage["tool_uses"] = int(tool_uses_match.group(1))
                return agent_id, usage
    return None, None


def is_continuation_message(text: str) -> bool:
    """Check if a user message is a context continuation summary."""
    return "continued from a previous conversation" in text.lower()


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 bytes per token for English text."""
    return len(text.encode("utf-8")) // 4


# --- Main parsing ---

def find_conversation_file(identifier: str) -> str:
    """Resolve a UUID or path to a .jsonl file path."""
    if os.path.isfile(identifier):
        return identifier

    base = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(base):
        print(f"Error: Claude projects directory not found: {base}", file=sys.stderr)
        sys.exit(1)

    # Search by UUID prefix
    pattern = os.path.join(base, "*", f"{identifier}*.jsonl")
    matches = glob.glob(pattern)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple matches for '{identifier}':", file=sys.stderr)
        for m in matches:
            print(f"  {m}", file=sys.stderr)
        print("Provide a longer UUID prefix or full path.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"No conversation found matching '{identifier}'", file=sys.stderr)
        sys.exit(1)


def find_subagent_files(conversation_path: str) -> list[str]:
    """Find subagent JSONL files for a conversation."""
    uuid = os.path.basename(conversation_path).replace(".jsonl", "")
    subagent_dir = os.path.join(os.path.dirname(conversation_path), uuid, "subagents")
    if not os.path.isdir(subagent_dir):
        return []
    files = glob.glob(os.path.join(subagent_dir, "*.jsonl"))
    # Skip compact summaries
    return [f for f in files if not os.path.basename(f).startswith("agent-acompact-")]


def parse_subagent_signal(filepath: str) -> dict:
    """Parse a subagent file and return summary metadata."""
    basename = os.path.basename(filepath)
    agent_id = basename.replace("agent-", "").replace(".jsonl", "")
    signal_bytes = 0
    first_description = ""

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            t = obj.get("type")
            if t == "assistant":
                content = obj.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            if block.get("type") == "text":
                                signal_bytes += len(block.get("text", "").encode("utf-8"))
                            elif block.get("type") == "thinking":
                                signal_bytes += len(block.get("thinking", "").encode("utf-8"))
            elif t == "user":
                text = extract_user_text(obj.get("message", {}).get("content", ""))
                if text and not is_noise_text(text) and not first_description:
                    first_description = text[:200]

    return {
        "id": agent_id,
        "file": filepath,
        "description": first_description,
        "signal_bytes": signal_bytes,
        "signal_tokens_estimate": signal_bytes // 4,
    }


def parse_conversation(filepath: str, output_dir: str, include_subagents: bool = False) -> None:
    """Parse a conversation JSONL into events.json and manifest.json."""
    os.makedirs(output_dir, exist_ok=True)
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    events = []
    sessions = set()
    prev_session_id = None
    signal_bytes = 0
    all_images = []
    pii_warnings = []
    pending_agent_calls = {}  # tool_use_id -> {description, prompt}
    subagent_refs_by_event = {}  # event_index -> [subagent_ref]
    duration_for_next = None

    uuid = os.path.basename(filepath).replace(".jsonl", "")
    project_dir = os.path.basename(os.path.dirname(filepath))

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = obj.get("type")
            session_id = obj.get("sessionId")

            # Track sessions
            if session_id:
                sessions.add(session_id)

            # --- system entries: keep only turn_duration ---
            if entry_type == "system":
                if obj.get("subtype") == "turn_duration":
                    duration_for_next = obj.get("durationMs")
                continue

            # --- skip noise types ---
            if entry_type in ("progress", "file-history-snapshot", "queue-operation"):
                continue

            # --- user entries ---
            if entry_type == "user":
                content = obj.get("message", {}).get("content", "")
                text = extract_user_text(content)

                # Check for images in tool_results
                images = extract_images(content, len(events), assets_dir)
                all_images.extend(images)

                # Check for agent results in tool_results
                agent_id, agent_usage = extract_agent_id_from_tool_result(content)
                if agent_id:
                    # Link back to the Agent tool_use event
                    for eidx, refs in list(subagent_refs_by_event.items()):
                        for ref in refs:
                            if ref.get("_pending"):
                                ref["id"] = agent_id
                                ref.pop("_pending", None)
                                if agent_usage:
                                    ref.update(agent_usage)

                # Drop if content is only tool_results (no text)
                if not text:
                    continue

                # Drop noise
                if is_noise_text(text):
                    continue

                # Detect continuation
                is_continuation = is_continuation_message(text)

                # Clean text
                text = clean_text(text)
                if not text:
                    continue

                # Detect session break
                session_break = False
                if prev_session_id is not None and session_id != prev_session_id:
                    session_break = True
                if session_id:
                    prev_session_id = session_id

                # Scan for PII
                secrets = scan_secrets(text)
                if secrets:
                    for s in secrets:
                        pii_warnings.append(f"Event {len(events)}: {s}")

                event = {
                    "index": len(events),
                    "timestamp": obj.get("timestamp", ""),
                    "role": "user",
                    "says": text,
                    "session_break": session_break,
                    "continuation_summary": text if is_continuation else "",
                }

                if images:
                    event["screenshots"] = [
                        {"filename": img["filename"], "description": f"Screenshot taken near event {img['event_index']}"}
                        for img in images
                    ]

                if duration_for_next is not None:
                    event["duration_ms"] = duration_for_next
                    duration_for_next = None

                signal_bytes += len(text.encode("utf-8"))
                events.append(event)

            # --- assistant entries ---
            elif entry_type == "assistant":
                content = obj.get("message", {}).get("content", [])

                says = ""
                thinks = ""
                tools = []
                subagent_refs = []

                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        block_type = block.get("type")

                        if block_type == "text":
                            text = block.get("text", "").strip()
                            if text:
                                says = (says + "\n" + text).strip() if says else text

                        elif block_type == "thinking":
                            thinking = block.get("thinking", "").strip()
                            if thinking:
                                thinks = (thinks + "\n" + thinking).strip() if thinks else thinking

                        elif block_type == "tool_use":
                            tool_name = block.get("name", "")
                            if tool_name:
                                tools.append(tool_name)
                            # Track Agent calls for subagent linking
                            if tool_name == "Agent":
                                tool_input = block.get("input", {})
                                ref = {
                                    "_pending": True,
                                    "description": tool_input.get("description", ""),
                                    "prompt": (tool_input.get("prompt", ""))[:300],
                                    "signal_tokens_estimate": 0,
                                }
                                subagent_refs.append(ref)

                # Skip if nothing of value
                if not says and not thinks and not tools:
                    continue

                # Detect session break
                session_break = False
                if prev_session_id is not None and session_id != prev_session_id:
                    session_break = True
                if session_id:
                    prev_session_id = session_id

                # Scan for PII
                for text_field in [says, thinks]:
                    secrets = scan_secrets(text_field)
                    if secrets:
                        for s in secrets:
                            pii_warnings.append(f"Event {len(events)}: {s}")

                event = {
                    "index": len(events),
                    "timestamp": obj.get("timestamp", ""),
                    "role": "assistant",
                    "says": says,
                }

                if thinks:
                    event["thinks"] = thinks
                if tools:
                    event["tools"] = tools
                if session_break:
                    event["session_break"] = True
                if subagent_refs:
                    event["subagent_refs"] = subagent_refs
                    subagent_refs_by_event[event["index"]] = subagent_refs

                if duration_for_next is not None:
                    event["duration_ms"] = duration_for_next
                    duration_for_next = None

                signal_bytes += len(says.encode("utf-8"))
                signal_bytes += len(thinks.encode("utf-8"))
                events.append(event)

    # --- Subagent inventory ---
    subagent_files = find_subagent_files(filepath)
    subagents = []
    for sf in subagent_files:
        meta = parse_subagent_signal(sf)
        subagents.append(meta)

    # Enrich subagent_refs in events with token estimates
    subagent_lookup = {s["id"]: s for s in subagents}
    for refs in subagent_refs_by_event.values():
        for ref in refs:
            agent_id = ref.get("id", "")
            if agent_id in subagent_lookup:
                ref["signal_tokens_estimate"] = subagent_lookup[agent_id]["signal_tokens_estimate"]

    # Clean up internal markers
    for refs in subagent_refs_by_event.values():
        for ref in refs:
            ref.pop("_pending", None)

    # --- Optionally parse and inline subagent content ---
    if include_subagents:
        for subagent in subagents:
            sub_events = parse_subagent_events(subagent["file"])
            subagent["events"] = sub_events

    # --- Build manifest ---
    total_subagent_tokens = sum(s["signal_tokens_estimate"] for s in subagents)

    manifest = {
        "conversation_id": uuid,
        "project_encoded": project_dir,
        "sessions": len(sessions),
        "total_events": len(events),
        "main_signal_bytes": signal_bytes,
        "main_signal_tokens_estimate": signal_bytes // 4,
        "estimation_method": "4-bytes-per-token heuristic",
        "subagents": [
            {
                "id": s["id"],
                "description": s["description"],
                "signal_tokens_estimate": s["signal_tokens_estimate"],
            }
            for s in subagents
        ],
        "total_signal_tokens_if_all_subagents": (signal_bytes // 4) + total_subagent_tokens,
        "screenshots_extracted": len(all_images),
        "pii_warnings": pii_warnings,
        "parsed_at": datetime.now().isoformat(),
    }

    # --- Write output ---
    events_path = os.path.join(output_dir, "events.json")
    manifest_path = os.path.join(output_dir, "manifest.json")

    with open(events_path, "w") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Parsed: {uuid}")
    print(f"  Events:     {len(events)}")
    print(f"  Signal:     {signal_bytes:,} bytes (~{signal_bytes // 4:,} tokens)")
    print(f"  Sessions:   {len(sessions)}")
    print(f"  Subagents:  {len(subagents)}")
    print(f"  Screenshots:{len(all_images)}")
    if pii_warnings:
        print(f"  PII warnings: {len(pii_warnings)}")
    print(f"  Output:     {output_dir}/")


def parse_subagent_events(filepath: str) -> list[dict]:
    """Parse a subagent JSONL into a list of signal events (same format as main)."""
    events = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = obj.get("type")
            if entry_type in ("progress", "file-history-snapshot", "queue-operation", "system"):
                continue

            if entry_type == "user":
                text = extract_user_text(obj.get("message", {}).get("content", ""))
                if not text or is_noise_text(text):
                    continue
                text = clean_text(text)
                if not text:
                    continue
                events.append({
                    "index": len(events),
                    "timestamp": obj.get("timestamp", ""),
                    "role": "user",
                    "says": text,
                })

            elif entry_type == "assistant":
                content = obj.get("message", {}).get("content", [])
                says = ""
                thinks = ""
                tools = []
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        bt = block.get("type")
                        if bt == "text":
                            t = block.get("text", "").strip()
                            if t:
                                says = (says + "\n" + t).strip() if says else t
                        elif bt == "thinking":
                            t = block.get("thinking", "").strip()
                            if t:
                                thinks = (thinks + "\n" + t).strip() if thinks else t
                        elif bt == "tool_use":
                            name = block.get("name", "")
                            if name:
                                tools.append(name)

                if not says and not thinks and not tools:
                    continue
                event = {
                    "index": len(events),
                    "timestamp": obj.get("timestamp", ""),
                    "role": "assistant",
                    "says": says,
                }
                if thinks:
                    event["thinks"] = thinks
                if tools:
                    event["tools"] = tools
                events.append(event)

    return events


def main():
    parser = argparse.ArgumentParser(
        description="Parse Claude Code conversation JSONL into clean event stream"
    )
    parser.add_argument("identifier", help="Conversation UUID (prefix) or full .jsonl path")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: /tmp/retell-<uuid>)")
    parser.add_argument("--include-subagents", action="store_true",
                        help="Also parse and inline subagent events")
    args = parser.parse_args()

    filepath = find_conversation_file(args.identifier)
    uuid = os.path.basename(filepath).replace(".jsonl", "")

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = f"/tmp/retell-{uuid[:8]}"

    parse_conversation(filepath, output_dir, include_subagents=args.include_subagents)


if __name__ == "__main__":
    main()
