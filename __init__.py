"""Hermes Plugin Template — `/test`

A minimal-but-complete Hermes plugin you can read, copy, and extend while
learning the plugin system. It registers:

  1. a TOOL   (`hello_world`)     — callable by the agent like any built-in tool
  2. a HOOK   (`post_tool_call`)  — runs after every tool the agent calls
  3. a SLASH COMMAND (`/ping`)    — an in-session command the user can type

How a plugin is loaded (verified against hermes-agent
`hermes_cli/plugins.py`):

  * The loader scans ~/.hermes/plugins/<name>/ (user plugins), plus bundled /
    project / pip sources.
  * Each directory plugin must have a `plugin.yaml` manifest and an
    `__init__.py` that defines `register(ctx)`.
  * The loader calls `register(ctx)` once. You use `ctx.register_tool(...)`,
    `ctx.register_hook(...)`, `ctx.register_command(...)` to contribute
    behavior. `ctx` is the PluginContext.

Enable this plugin in ~/.hermes/config.yaml:

    plugins:
      enabled:
        - test

Then reload: `hermes doctor` or just start a new `hermes` session.
Debug loading with: `HERMES_PLUGINS_DEBUG=1 hermes chat -q hi`
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("hermes.plugins.test")

HERMES_HOME = Path(
    __import__("os").environ.get("HERMES_HOME", Path.home() / ".hermes")
)


# ---------------------------------------------------------------------------
# 1. TOOL
# ---------------------------------------------------------------------------
# A tool schema is a standard function-calling schema (name + JSON-Schema
# `parameters`). The handler receives the parsed args dict and returns a
# string (the tool result the model sees).

HELLO_SCHEMA: Dict[str, Any] = {
    "name": "hello_world",
    "description": (
        "Template tool. Greets the user by name and reports the Hermes home "
        "directory. Use this to confirm the test plugin is loaded and callable."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Who to greet (default: 'world').",
            },
        },
        "required": [],
    },
}


def _handle_hello(args: Dict[str, Any]) -> str:
    """Handler signature: fn(args: dict) -> str."""
    who = (args.get("name") or "world").strip() or "world"
    return (
        f"Hello, {who}! 👋\n"
        f"This is the `test` plugin tool running.\n"
        f"Hermes home: {HERMES_HOME}"
    )


# ---------------------------------------------------------------------------
# 2. HOOK
# ---------------------------------------------------------------------------
# Lifecycle hooks the core invokes at fixed points. Valid names (subset):
#   pre_tool_call, post_tool_call, transform_terminal_output,
#   transform_tool_result, ...
# A post_tool_call callback receives kwargs like:
#   tool_name, args, result, success, ...

def _on_post_tool_call(**kwargs: Any) -> None:
    tool_name = kwargs.get("tool_name")
    success = kwargs.get("success")
    logger.debug("[test plugin] tool %s finished (success=%s)", tool_name, success)


# ---------------------------------------------------------------------------
# 3. SLASH COMMAND
# ---------------------------------------------------------------------------
# Slash-command handler signature: fn(raw_args: str) -> str | None
# It may also be async. Returned string is shown to the user.

def _cmd_ping(raw_args: str) -> str:
    return "pong 🏓 (from the `test` plugin)"


# ---------------------------------------------------------------------------
# register() — the single entry point the loader calls.
# ---------------------------------------------------------------------------

def register(ctx) -> None:
    """Called once by the plugin loader. Contribute tools/hooks/commands here."""

    # Tool. `toolset` groups your tools in `hermes tools` output.
    # `emoji` is cosmetic. `check_fn` (optional) gates dispatch at call time.
    ctx.register_tool(
        name="hello_world",
        toolset="test",
        schema=HELLO_SCHEMA,
        handler=_handle_hello,
        emoji="👋",
    )

    # Lifecycle hook.
    ctx.register_hook("post_tool_call", _on_post_tool_call)

    # In-session slash command: type `/ping` during a conversation.
    ctx.register_command(
        name="ping",
        handler=_cmd_ping,
        description="Template slash command from the test plugin.",
        args_hint="",
    )

    logger.info("[test plugin] registered tool=hello_world, command=/ping, hook=post_tool_call")
