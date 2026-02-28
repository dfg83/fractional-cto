#!/usr/bin/env python3
"""
Conversation Discovery: Preview recent Claude Code conversations across all projects.

Lists conversations with enough context to decide which are worth turning into blog posts.
Includes blog-worthiness heuristics to help prioritize.

Usage:
  python3 preview-conversations.py          # Last 10 conversations
  python3 preview-conversations.py 20       # Last 20 conversations
  python3 preview-conversations.py --json   # JSON output for programmatic use
"""

import glob
import json
import os
import sys
from datetime import datetime


def extract_text(content) -> str:
    """Extract user-visible text from a message content field."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    return text
    return ""


def is_noise(text: str) -> bool:
    """Skip system-generated messages that aren't real user input."""
    if not text:
        return True
    noise_markers = ["<local-command", "<command-name>", "[Request interrupted"]
    return any(m in text for m in noise_markers)


def blog_worthiness_hints(preview: dict) -> list[str]:
    """Return heuristic hints about whether this conversation might make a good blog post."""
    hints = []
    score = 0

    if preview["user_msgs"] < 5:
        hints.append("Few user messages — likely too brief for a story")
    elif preview["user_msgs"] >= 15:
        hints.append("Substantial user engagement")
        score += 1

    if preview["subagent_files"] > 0:
        hints.append(f"{preview['subagent_files']} subagent(s) — suggests parallel research")
        score += 2

    if preview["sessions"] > 1:
        hints.append(f"Spans {preview['sessions']} sessions — longer arc")
        score += 1

    if preview["has_continuation"]:
        hints.append("Context continued — multi-window conversation")
        score += 1

    if preview["size_mb"] > 5.0:
        hints.append(f"Large ({preview['size_mb']:.1f} MB) — substantial work")
        score += 1
    elif preview["size_mb"] < 0.1:
        hints.append("Very small — probably a quick task")

    diverse_tools = set(preview["tools"]) - {"Read", "Edit", "Bash", "Write", "Glob", "Grep"}
    if diverse_tools:
        hints.append(f"Diverse tools: {', '.join(sorted(diverse_tools)[:4])}")
        score += 1

    if set(preview["tools"]) <= {"Edit", "Bash", "Read", "Write"}:
        hints.append("Mostly coding tools — may lack narrative arc")

    preview["blog_score"] = score
    return hints


def preview_conversation(filepath: str) -> dict | None:
    """Extract a preview summary from a conversation JSONL file."""
    try:
        size_mb = os.path.getsize(filepath) / 1024 / 1024
    except OSError:
        return None

    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    uuid = os.path.basename(filepath).replace(".jsonl", "")
    project_dir = os.path.basename(os.path.dirname(filepath))

    user_count = 0
    assistant_count = 0
    first_user = ""
    last_user = ""
    sessions = set()
    tools_used = set()
    has_continuation = False

    try:
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
                sid = obj.get("sessionId")
                if sid:
                    sessions.add(sid)

                if t == "user":
                    text = extract_text(obj.get("message", {}).get("content", ""))
                    if is_noise(text):
                        continue
                    if "continued from a previous conversation" in text.lower():
                        has_continuation = True
                        continue
                    user_count += 1
                    if not first_user:
                        first_user = text
                    last_user = text

                elif t == "assistant":
                    assistant_count += 1
                    content = obj.get("message", {}).get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                name = block.get("name", "")
                                if name:
                                    tools_used.add(name)
    except OSError:
        return None

    # Check for subagent files
    subagent_dir = os.path.join(
        os.path.dirname(filepath),
        uuid,
        "subagents",
    )
    subagent_files = []
    if os.path.isdir(subagent_dir):
        subagent_files = [
            f for f in glob.glob(os.path.join(subagent_dir, "*.jsonl"))
            if not os.path.basename(f).startswith("agent-acompact-")
        ]

    if user_count == 0:
        return None

    return {
        "uuid": uuid,
        "project_encoded": project_dir,
        "date": mtime.strftime("%Y-%m-%d %H:%M"),
        "size_mb": round(size_mb, 1),
        "user_msgs": user_count,
        "assistant_msgs": assistant_count,
        "sessions": len(sessions),
        "subagent_files": len(subagent_files),
        "tools": sorted(tools_used),
        "has_continuation": has_continuation,
        "first_user": first_user[:150].replace("\n", " "),
        "last_user": last_user[:150].replace("\n", " "),
    }


def main():
    n = 10
    json_output = False

    args = sys.argv[1:]
    for arg in args:
        if arg == "--json":
            json_output = True
        elif arg.isdigit():
            n = int(arg)

    base = os.path.expanduser("~/.claude/projects")
    if not os.path.isdir(base):
        print(f"Error: Claude projects directory not found: {base}", file=sys.stderr)
        sys.exit(1)

    files = glob.glob(os.path.join(base, "*", "*.jsonl"))
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

    previews = []
    for f in files[:n * 2]:  # scan extra in case some are empty
        p = preview_conversation(f)
        if p:
            hints = blog_worthiness_hints(p)
            p["blog_hints"] = hints
            previews.append(p)
        if len(previews) >= n:
            break

    # Sort by blog_score descending, then date
    previews.sort(key=lambda p: (-p.get("blog_score", 0), p["date"]), reverse=False)
    previews.sort(key=lambda p: p.get("blog_score", 0), reverse=True)

    if json_output:
        print(json.dumps(previews, indent=2, ensure_ascii=False))
        return

    if not previews:
        print("No conversations found.")
        return

    for p in previews:
        score = p.get("blog_score", 0)
        score_indicator = "*" * min(score, 5)
        print(f"{'─' * 78}")
        print(f"  {p['date']}  |  {p['size_mb']:.1f} MB  |  {p['uuid'][:8]}...  |  Blog: {score_indicator or '-'}")
        print(f"  Project: {p['project_encoded']}")
        print(f"  {p['user_msgs']} user / {p['assistant_msgs']} assistant"
              f"  |  {p['sessions']} session(s)"
              f"  |  {p['subagent_files']} subagent(s)"
              + ("  |  continued" if p["has_continuation"] else ""))
        if p["tools"]:
            short_tools = [t.replace("mcp__playwright__", "pw:") for t in p["tools"][:8]]
            if len(p["tools"]) > 8:
                short_tools.append(f"+{len(p['tools']) - 8} more")
            print(f"  Tools: {', '.join(short_tools)}")
        print(f"  Start: {p['first_user'][:100]}")
        if p["last_user"] != p["first_user"]:
            print(f"  End:   {p['last_user'][:100]}")
        if p.get("blog_hints"):
            print(f"  Hints: {'; '.join(p['blog_hints'][:3])}")
    print(f"{'─' * 78}")
    print(f"\n  {len(previews)} conversations shown. Use UUID with /retell to start the pipeline.")


if __name__ == "__main__":
    main()
