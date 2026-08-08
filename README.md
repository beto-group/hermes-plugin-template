# Hermes Plugin Template — `test`

This folder is a **minimal, working** Hermes plugin you can study while
learning Hermes plugin development. Drop it into your user plugin directory
and enable it to confirm the whole pipeline works end to end.

## What's in here

| File | Purpose |
|------|---------|
| `plugin.yaml` | The manifest. Required. Declares `name`, `version`, `description`, and (optionally) `provides_tools` / `provides_hooks`. |
| `__init__.py`  | The code. Required. Must define `register(ctx)`, which is called once at load time. |
| `README.md`    | This file. |

## What it does

1. **Tool** `hello_world` — a callable tool the agent can invoke.
2. **Hook** `post_tool_call` — a lifecycle hook that runs after every tool call (just logs here).
3. **Slash command** `/ping` — type it in a session to get `pong 🏓`.

## Install / enable

1. Copy this folder into your user plugin directory:
   ```bash
   # The folder name on disk can differ; the plugin `name:` in plugin.yaml is the id.
   cp -r test ~/.hermes/plugins/test
   ```
2. Enable it in `~/.hermes/config.yaml`:
   ```yaml
   plugins:
     enabled:
       - test
   ```
   (Only needed if you keep plugins behind an allow-list. To let a plugin
   override a built-in tool, opt in under `plugins.entries.<name>.allow_tool_override: true`.)
3. Reload — start a new `hermes` session (or `hermes doctor`).
4. Verify:
   ```bash
   hermes plugins list          # should list `test`
   hermes chat -q "use the hello_world tool"
   # or inside a session: /ping
   ```
5. If it doesn't show up, debug discovery:
   ```bash
   HERMES_PLUGINS_DEBUG=1 hermes chat -q hi
   ```

## The contract (verified against `hermes_cli/plugins.py`)

- A **directory plugin** = a folder containing `plugin.yaml` + `__init__.py`
  with a `register(ctx)` function.
- The loader scans `~/.hermes/plugins/<name>/` (user), bundled `plugins/`,
  project `./.hermes/plugins/` (opt-in), and pip entry-points.
- Inside `register(ctx)` you may call:
  - `ctx.register_tool(name, toolset, schema, handler, check_fn=None, emoji="", override=False, ...)`
  - `ctx.register_hook(hook_name, callback)`
  - `ctx.register_command(name, handler, description="", args_hint="")`
  - plus `ctx.llm`, `ctx.inject_message(...)`, and more.
- Tool handler: `fn(args: dict) -> str` (or `async def`, pass `is_async=True`).
- Slash-command handler: `fn(raw_args: str) -> str | None`.
- Override of a built-in tool name requires `allow_tool_override: true` in
  config — fail-closed by default.

> Note: this is the **Python general plugin** system (`~/.hermes/plugins/`),
> which adds tools/hooks/commands to the agent core. It is separate from the
> **desktop-app UI plugin** system (`~/.hermes/desktop-plugins/`, plain JS
> `plugin.js` for panes/statusbar/chips). Pick the one matching what you want
> to build.
