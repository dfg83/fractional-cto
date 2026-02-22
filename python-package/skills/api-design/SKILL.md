---
name: api-design
description: "This skill should be used when the user is designing a library's public API surface, defining __all__, organizing imports, creating an exception hierarchy, implementing async/sync dual APIs, adding plugin architecture (pluggy, entry points, protocols), applying progressive disclosure, choosing return types, naming methods, or reviewing backward compatibility. Covers __all__, underscore-prefixed modules, exception trees, httpx _BaseClient pattern, pluggy, entry points, Protocols, dependency injection, configuration patterns."
version: 1.0.0
---

# Define Your Public API Surface and Defend It

The public API is the contract between your library and every downstream user. Once a symbol is public, removing or changing it is a breaking change. Getting the boundary right -- what is exported, what is private, how errors are communicated, how complexity is layered -- is the most consequential design decision in a Python library. Get it wrong and you end up like Pydantic v1: an unintentionally wide API surface that required a full rewrite to fix.

httpx is the gold standard. Every public symbol is re-exported from `__init__.py`. Every implementation module is underscore-prefixed (`_client.py`, `_config.py`). The exception hierarchy is a carefully designed tree. Sync and async clients share all non-I/O logic in a `_BaseClient`. Study httpx before designing your own API.

## Public API Surface: `__all__` and Underscore Modules

Every module that exports symbols must define `__all__`. This documents intent, controls `from module import *`, and tells tools (mypy, pyright, mkdocstrings) what is public.

| Rule | Rationale |
|------|-----------|
| Define `__all__` in every public module | Documents the contract; tools rely on it |
| Re-export everything from `__init__.py` | Users write `from mylib import Client`, never `from mylib._client import Client` |
| Prefix all implementation modules with `_` | `_client.py`, `_config.py`, `_exceptions.py` make the private boundary unambiguous |
| Sort `__all__` alphabetically | Easy to review in diffs, easy to check for completeness |
| Include type aliases and protocols in `__all__` | Users need them for type-checking; easy to forget |

| Bad | Good |
|-----|------|
| `from mylib.client import Client` | `from mylib import Client` |
| No `__all__`, everything implicitly public | Explicit `__all__` listing every public name |
| `utils.py` with mixed public/private helpers | `_utils.py` for internal, re-export public helpers from `__init__.py` |

**Expose less than you think you need.** You can always make something public later; you cannot easily make it private. If it is in `__all__`, it is a contract. If it starts with an underscore, you can change it freely.

## Progressive Disclosure

Design APIs that serve beginners and experts simultaneously. Simple things should be simple; complex things should be possible.

```python
# Layer 1: Module-level convenience (simplest)
response = httpx.get("https://api.example.com/users")

# Layer 2: Configured client (intermediate)
client = httpx.Client(base_url="https://api.example.com", timeout=30.0)
response = client.get("/users")

# Layer 3: Full customization (advanced)
transport = httpx.HTTPTransport(retries=3)
client = httpx.Client(transport=transport, timeout=httpx.Timeout(5.0, connect=10.0))
```

Rules for progressive disclosure:

1. **The simplest call requires the fewest arguments.** Use sensible defaults for everything.
2. **Complexity is opt-in, not opt-out.** A user who needs no auth should never see auth parameters.
3. **Use keyword-only arguments** (`*` in the signature) to prevent positional footguns as signatures grow.
4. **Module-level functions for the common case, classes for the configured case.** This is the httpx/requests pattern.
5. **Config objects instead of dozens of kwargs.** `httpx.Timeout(5.0, connect=10.0)` is more discoverable than `timeout=5.0, connect_timeout=10.0`.

## Exception Hierarchy

A well-designed exception hierarchy lets users catch errors at exactly the right granularity. It is part of `__all__` and must be as carefully designed as your classes.

```python
class MyLibError(Exception):
    """Base exception. `except MyLibError` catches everything."""

class ConfigurationError(MyLibError):
    """Raised when configuration is invalid."""

class ConnectionError(MyLibError):
    """Raised when a connection fails."""

class TimeoutError(ConnectionError):
    """Subclasses ConnectionError -- timeout is a type of connection failure."""

class AuthenticationError(MyLibError):
    """Raised when authentication fails."""

class ValidationError(MyLibError):
    """Carries structured error data, not just a string."""
    def __init__(self, errors: list[dict[str, Any]]) -> None:
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s)")
```

| Rule | Example |
|------|---------|
| Always provide a base exception class | `except MyLibError` as catch-all |
| Carry structured data, not just strings | httpx's `HTTPStatusError.response`, Pydantic's `.errors()` |
| Use inheritance to group related errors | `except TransportError` catches all network issues |
| Never raise bare `Exception` or `ValueError` | Users cannot distinguish your errors from others |
| Name exceptions as nouns | `TimeoutError`, not `TimedOut` |
| Document which methods raise which exceptions | Part of the API contract |

## Async/Sync Dual API

Follow httpx's `_BaseClient` pattern: share all non-I/O logic in a base class, implement genuinely separate sync and async I/O paths.

```python
class _BaseClient:
    """Shared logic: URL merging, headers, cookies, auth -- no I/O."""
    def _build_request(self, method: str, url: str, **kwargs) -> Request:
        ...

class Client(_BaseClient):
    """Synchronous client with blocking transport."""
    def send(self, request: Request) -> Response:
        return self._transport.handle_request(request)

class AsyncClient(_BaseClient):
    """Asynchronous client with async transport."""
    async def send(self, request: Request) -> Response:
        return await self._transport.handle_async_request(request)
```

| Bad | Good |
|-----|------|
| Wrap async with `asyncio.run()` in sync methods | Separate sync/async transport implementations |
| Duplicate all non-I/O logic in both clients | Share logic in `_BaseClient` |
| Only provide async API | Always provide sync; add async if doing I/O |

**Never use `asyncio.run()` as a sync wrapper.** It fails if an event loop is already running (Jupyter, async frameworks) and prevents connection pooling.

## Plugin Architecture

Choose the right extensibility pattern based on your scale.

| Pattern | Complexity | When to Use | Exemplar |
|---------|-----------|-------------|----------|
| **pluggy** | High | Full plugin ecosystem with hooks | pytest, tox |
| **Entry points** | Medium | Installed packages register themselves | pytest plugin discovery |
| **Protocols** | Low | Third-party opt-in without importing your lib | Rich (`__rich_repr__`) |
| **Decorator registry** | Low | Internal extensibility within your package | Click, Flask |

For protocols, use dunder names (`__mylib_serialize__`), make them `@runtime_checkable`, keep them to one method, and always provide a fallback for objects that do not implement the protocol. The key insight from Rich: objects do not need to import or subclass anything from your library to participate.

For entry points, define them in `pyproject.toml`:

```toml
[project.entry-points."mylib.plugins"]
my_plugin = "my_plugin_package:MyPlugin"
```

Discover them at runtime with `importlib.metadata.entry_points(group="mylib.plugins")`.

## Method Naming and Signatures

Use consistent verb-noun naming across the entire API. Pydantic v2 learned from v1's inconsistency by adopting a uniform `model_` prefix.

| Verb | Meaning | Example |
|------|---------|---------|
| `get` | Retrieve (may raise if missing) | `client.get()` |
| `create` | Make a new resource | `Session.create()` |
| `build` | Construct from parts | `Request.build()` |
| `validate` | Check and convert | `model_validate()` |
| `dump` | Serialize to format | `model_dump()`, `model_dump_json()` |
| `load` | Deserialize from format | `json.load()` |

Force keyword-only arguments after the first positional with `*` in the signature. Use sensible, secure defaults (`verify=True`, `follow_redirects=False`). Return rich objects for complex operations (httpx's `Response` carries status, headers, content, and `raise_for_status()`), primitives for simple queries, and `self` for builder/configuration methods.

## Configuration Patterns

Use frozen dataclasses for configuration objects. Validate in `__post_init__`. Provide a `from_env()` classmethod for environment variable integration without requiring it.

```python
@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ConfigurationError("timeout must be positive")

    @classmethod
    def from_env(cls, prefix: str = "MYLIB_") -> "ClientConfig":
        return cls(
            base_url=os.environ.get(f"{prefix}BASE_URL", ""),
            timeout=float(os.environ.get(f"{prefix}TIMEOUT", cls.timeout)),
        )
```

## Review Checklist

When reviewing code for API design:

- [ ] `__all__` is defined in every public module, sorted alphabetically, and includes all public symbols (classes, functions, exceptions, type aliases)
- [ ] All implementation modules are underscore-prefixed (`_client.py`, `_config.py`) and users never import from them directly
- [ ] Public symbols are re-exported from the top-level `__init__.py`
- [ ] The API supports progressive disclosure: module-level functions for simple use, configurable classes for advanced use
- [ ] All parameters beyond the first positional are keyword-only (use `*` separator)
- [ ] A base exception class exists and all library exceptions inherit from it
- [ ] Exceptions carry structured data (not just string messages) and are included in `__all__`
- [ ] No bare `Exception`, `ValueError`, or `TypeError` is raised from library code
- [ ] Async and sync clients share non-I/O logic in a base class with separate transport implementations
- [ ] No `asyncio.run()` wrappers are used to bridge async to sync
- [ ] Plugin extension points use the appropriate pattern (pluggy for full ecosystems, Protocols for third-party opt-in, entry points for auto-discovery)
- [ ] Method naming follows a consistent verb-noun pattern across the entire API surface
- [ ] Mutable default arguments are avoided (use `None` sentinel + factory)
- [ ] Importing the library produces no side effects (no network calls, no logging config, no global state mutation)
- [ ] Internal state is not exposed through public attributes; use read-only properties that return values, not mutable objects
