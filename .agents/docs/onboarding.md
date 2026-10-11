# Agent setup

How AI coding agents are wired in this repo. All agents share one set of instructions; agent-specific files only point to it.

## Layout

- `AGENTS.md`: canonical entry file. Holds only the project one-liner, commands, structural constraints, docs index and plans convention. Keep it lean.
- `CLAUDE.md`: contains `@AGENTS.md`, because Claude Code reads `CLAUDE.md`, not `AGENTS.md`. Claude-only lines may follow the import.
- `.agents/docs/`: governing docs, loaded on demand. Add each new doc to the AGENTS.md docs index as a plain markdown link with a one-line "read when…" hook. Never reference docs with `@` imports: some agents load imports at launch, which defeats on-demand loading.
- `.agents/skills/<name>/`: shared project skills. Each skill also gets a committed relative symlink `.claude/skills/<name>` pointing to it.
- `.agents/plans/`: agent plans. Gitignored, personal.

## Hooking up an agent

- Cursor: reads `AGENTS.md` natively. Nothing to do.
- Claude Code: reads `CLAUDE.md`, which imports `AGENTS.md`. Nothing to do.
- Any other agent: point its entry-file mechanism at `AGENTS.md` (include syntax if supported, else a copy kept in sync), or re-run `/agentify-project` to research and wire it.

## Windows symlinks

Skill symlinks need `git config core.symlinks true` and Windows Developer Mode (or admin rights) before clone or checkout. Without them git checks symlinks out as plain text files.
