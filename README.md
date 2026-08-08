# Hermes Plugin Template — `test`

This folder is a **minimal, working** Hermes plugin that demonstrates **both**
extension layers at once:

1. **Agent-core layer** (`plugin.yaml` + `__init__.py`) — adds a tool, a hook,
   and a slash command to the Hermes agent.
2. **Web dashboard UI layer** (`dashboard/`) — adds a **nav-rail button** to the
   webUI (`hermes dashboard`) that opens a custom tab.

You can study it while learning Hermes plugin development, or use it as a
starting skeleton for your own plugin. Drop it into your user plugin directory,
enable it, and the whole pipeline works end to end.

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
  of the left sidebar in `hermes dashboard`. Clicking it opens the `/test` tab,
  which renders the page from `dashboard/dist/index.js`.
- The nav button is driven entirely by the `tab` entry in `dashboard/manifest.json`.
  (A separate `sidebar` *slot* is a different mechanism — a cockpit-theme rail
  widget — and is not used by this template.)

## Install / enable (agent-core layer)

1. Copy this folder into your user plugin directory (the on-disk folder name can
   differ; the plugin `name:` in `plugin.yaml` is the id):
   ```bash
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
3. Start a new `hermes` session (or run `hermes doctor`).
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

## Install / enable (web dashboard layer)

The webUI plugin lives at `<plugin>/dashboard/manifest.json`. As long as the
plugin folder is under `~/.hermes/plugins/`, `hermes dashboard` discovers it
automatically — **no extra enable flag** is needed for the web layer.

1. Make sure the plugin folder is present (copy or symlink) at
   `~/.hermes/plugins/test/dashboard/manifest.json`.
2. Start / restart the dashboard:
   ```bash
   hermes dashboard
   ```
3. Open the webUI and look for the **"My Plugin"** button at the bottom of the
   left sidebar. Click it to open the `/test` tab.

### ⚠️ Dashboard discovery is cached per-process

The web server reads `dashboard/manifest.json` **once at startup**. Editing the
manifest or the JS bundle will **not** show up until you restart the dashboard.
A browser refresh alone is not enough.

Restart command (the dashboard traps `SIGTERM`, but the systemd unit handles
the kill correctly — this is the only command you need):

```bash
systemctl --user restart hermes-dashboard.service
```

Then reload the webUI in your browser.

### Development convenience: symlink the folder

If you keep the source in a separate repo (e.g. this folder at
`~/dev/.../plugins/test`) but Hermes loads from `~/.hermes/plugins/test`, the two
are separate physical copies and your edits won't take effect. Symlink the dev
folder onto the install location so every edit lands instantly:

```bash
ln -sfn /path/to/your/repo/plugins/test ~/.hermes/plugins/test
```

After that, the only step after an edit is `systemctl --user restart
hermes-dashboard.service`.

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
> to build. The `dashboard/` subfolder documented above is the **third** system:
> the **web dashboard UI** plugin layer.
