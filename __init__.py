"""Grex Nexus Sovereign Mothership Plugin — Hermes Agent Integration.

Provides:
  1. Dashboard UI tab: Grex Nexus Sovereign Mothership (Tiling WM + Component Store)
  2. Tools: `grex_status`, `grex_exec`
  3. Slash command: `/grex`
"""

from __future__ import annotations

import logging
import urllib.request
import json
from typing import Any, Dict

logger = logging.getLogger("hermes.plugins.grex_nexus")

GREX_STATUS_SCHEMA: Dict[str, Any] = {
    "name": "grex_status",
    "description": "Get runtime telemetry and status for Grex Nexus Sovereign Mothership, Podman containers, and sidecar daemon.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

GREX_EXEC_SCHEMA: Dict[str, Any] = {
    "name": "grex_exec",
    "description": "Execute a sovereign host command via Grex Nexus sidecar daemon.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command string to execute.",
            },
        },
        "required": ["command"],
    },
}

def _handle_grex_status(args: Dict[str, Any]) -> str:
    try:
        req = urllib.request.urlopen("http://host.containers.internal:7777/api/status", timeout=3)
        data = json.loads(req.read().decode("utf-8"))
        return f"🟢 Grex Nexus Sidecar Daemon Online:\n{json.dumps(data, indent=2)}"
    except Exception:
        try:
            req = urllib.request.urlopen("http://localhost:7777/api/status", timeout=3)
            data = json.loads(req.read().decode("utf-8"))
            return f"🟢 Grex Nexus Sidecar Daemon Online:\n{json.dumps(data, indent=2)}"
        except Exception as ex:
            return f"🔴 Grex Nexus Sidecar Daemon offline or unreachable: {ex}"

def _handle_grex_exec(args: Dict[str, Any]) -> str:
    cmd_str = args.get("command", "")
    if not cmd_str:
        return "Error: command string required."
    try:
        payload = json.dumps({"command": cmd_str}).encode("utf-8")
        url = "http://host.containers.internal:7777/api/exec"
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            return f"Exit Code: {res.get('exit_code', 0)}\nStdout:\n{res.get('stdout', '')}\nStderr:\n{res.get('stderr', '')}"
    except Exception:
        try:
            payload = json.dumps({"command": cmd_str}).encode("utf-8")
            url = "http://localhost:7777/api/exec"
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode("utf-8"))
                return f"Exit Code: {res.get('exit_code', 0)}\nStdout:\n{res.get('stdout', '')}\nStderr:\n{res.get('stderr', '')}"
        except Exception as ex:
            return f"Execution failed: {ex}"

def _cmd_grex(raw_args: str) -> str:
    return "🛰️ Grex Nexus Sovereign Mothership Host Engine — Dashboard tab active at /grex-nexus."

def _ensure_cli_bin():
    try:
        plugin_dir = Path(__file__).parent
        grex_bin = plugin_dir / "bin" / "grex"
        if grex_bin.exists():
            target_dir = Path.home() / ".local" / "bin"
            target_dir.mkdir(parents=True, exist_ok=True)
            target_bin = target_dir / "grex"
            if target_bin.exists() or target_bin.is_symlink():
                try:
                    target_bin.unlink()
                except Exception:
                    pass
            os.symlink(str(grex_bin), str(target_bin))
            os.chmod(str(grex_bin), 0o755)
    except Exception as e:
        logger.warning("Could not create grex CLI symlink: %s", e)

def register(ctx) -> None:
    """Register Grex Nexus tools, commands, and hooks."""
    _ensure_cli_bin()

    ctx.register_tool(
        name="grex_status",
        toolset="grex",
        schema=GREX_STATUS_SCHEMA,
        handler=_handle_grex_status,
        emoji="🛰️",
    )

    ctx.register_tool(
        name="grex_exec",
        toolset="grex",
        schema=GREX_EXEC_SCHEMA,
        handler=_handle_grex_exec,
        emoji="⚡",
    )

    ctx.register_command(
        name="grex",
        handler=_cmd_grex,
        description="Show Grex Nexus Sovereign Mothership status.",
        args_hint="",
    )

    logger.info("[grex-nexus] Registered tools (grex_status, grex_exec) and slash command (/grex)")
