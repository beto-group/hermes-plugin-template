# Hermes Plugin Template — `test`

A minimal, working Hermes plugin that demonstrates **two** extension layers:

1. **Agent-core layer** (`plugin.yaml` + `__init__.py`) — a tool, a hook, and a
   slash command.
2. **Web dashboard UI layer** (`dashboard/`) — a nav-rail button in the webUI
   that opens a custom tab.

Use it as a study reference or a skeleton for your own plugin.

## What's in here

| File | Layer | Purpose |
|------|-------|---------|
| `plugin.yaml` | agent-core | Required. Declares `name`, `version`, `description`, `provides_tools` / `provides_hooks`. |
| `__init__.py`  | agent-core | Required. Defines `register(ctx)`, called once at load time. |
| `dashboard/manifest.json` | webUI | Required for the web layer. Declares the nav tab (`tab.path`), label, icon, and JS entry point. |
| `dashboard/dist/index.js` | webUI | Required for the web layer. Pre-built IIFE bundle that renders the tab page (and any slots). |
| `README.md`    | — | This file. |

## What it does

### Agent-core layer
1. **Tool** `hello_world` — a callable tool the agent can invoke.
2. **Hook** `post_tool_call` — a lifecycle hook that runs after every tool call (just logs here).
3. **Slash command** `/ping` — type it in a session to get `pong 🏓`.

### Web dashboard layer
- A nav-rail button labeled **"My Plugin"** (Sparkles icon) appears at the end
  of the left sidebar in the webUI. Clicking it opens the `/test` tab, which
  renders the page from `dashboard/dist/index.js`.
- The nav button is driven entirely by the `tab` entry in `dashboard/manifest.json`.
  (A separate `sidebar` *slot* is a different mechanism — a cockpit-theme rail
  widget — and is not used by this template.)

## Editing the webUI button

### Change the tab / button
Edit `dashboard/manifest.json`:

```json
{
  "name": "test",                 // unique id, lowercase-hyphen
  "label": "My Plugin",           // nav button text
  "icon": "Sparkles",             // Lucide icon name (falls back to Puzzle)
  "version": "1.0.0",
  "tab": { "path": "/test", "position": "end" },  // nav button -> /test
  "entry": "dist/index.js"        // JS bundle location
}
```

- `tab.path` is the route the button opens.
- `tab.position`: `"end"` (default), `"after:<segment>"`, or `"before:<segment>"`.
- `icon` must be a mapped Lucide name (e.g. `Activity`, `Code`, `Database`,
  `Globe`, `Puzzle`, `Settings`, `Sparkles`, `Star`, `Terminal`, `Wrench`,
  `Zap`) or it falls back to `Puzzle`.

### Change the tab page content
Edit `dashboard/dist/index.js` and rebuild your bundle. The bundle is an IIFE
that uses the global `window.__HERMES_PLUGIN_SDK__` — **do not bundle React**;
use `SDK.React`. Register the page with:

```js
window.__HERMES_PLUGINS__.register("test", MyPage);
```

(See `dashboard/dist/index.js` for the working example in this template.)

## The contract (agent-core layer)

- A **directory plugin** = a folder containing `plugin.yaml` + `__init__.py`
  with a `register(ctx)` function.
- Inside `register(ctx)` you may call:
  - `ctx.register_tool(name, toolset, schema, handler, check_fn=None, emoji="", override=False, ...)`
  - `ctx.register_hook(hook_name, callback)`
  - `ctx.register_command(name, handler, description="", args_hint="")`
  - plus `ctx.llm`, `ctx.inject_message(...)`, and more.
- Tool handler: `fn(args: dict) -> str` (or `async def`, pass `is_async=True`).
- Slash-command handler: `fn(raw_args: str) -> str | None`.
- Override of a built-in tool name requires `allow_tool_override: true` in
  config — fail-closed by default.

> Note: this folder exercises three separate Hermes plugin systems — the
> **Python general plugin** layer (`plugin.yaml` + `__init__.py`), the
> **desktop-app UI plugin** layer (separate `desktop-plugins/` system, not
> included here), and the **web dashboard UI** layer (`dashboard/`).
