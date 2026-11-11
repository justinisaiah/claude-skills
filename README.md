# claude-skills

Custom [Agent Skills](https://code.claude.com/docs/en/skills) for Claude.

Each directory is one skill. A skill is a folder containing a `SKILL.md` with YAML
frontmatter (`name` and `description`) plus markdown instructions, and optionally
`references/`, `scripts/`, and `assets/` subdirectories.

## Skills

| Skill | What it does |
|---|---|
| [`bogleheads-wiki`](./bogleheads-wiki) | Answers investing and personal-finance questions by looking up and citing pages on the Bogleheads wiki, and by reasoning inside the Boglehead framework. |
| [`security-audit`](./security-audit) | Fork of [Cloudflare's security-audit skill](https://github.com/cloudflare/security-audit-skill) (MIT). Security guidance and multi-phase, independently verified vulnerability audits of codebases. See [`UPSTREAM.md`](./security-audit/UPSTREAM.md). |

## Installing

**Claude apps (web, desktop, mobile)**

1. Settings → Capabilities → enable **Code execution and file creation**. Without this
   the Skills menu is greyed out.
2. Zip the skill folder (the folder itself, not its contents):
   ```bash
   cd claude-skills && zip -r bogleheads-wiki.zip bogleheads-wiki/
   ```
3. Customize → Skills → **+** → Create skill → upload the zip.
4. Toggle it on. Uploaded is not the same as enabled.

**Claude Code**

Copy the folder into a skills directory — `~/.claude/skills/` for personal use, or
`.claude/skills/` inside a repo to share it with that project:

```bash
cp -r bogleheads-wiki ~/.claude/skills/
```

## Notes on writing these

- The `description` is the entire triggering mechanism. It's the only part Claude sees
  before deciding whether to load the skill, so it needs to say both what the skill does
  and when to use it. Skills tend to under-trigger; when one doesn't fire, the
  description is the first thing to look at.
- Keep `SKILL.md` under ~500 lines. Push detail into `references/` and point at those
  files from the body, so they load only when needed.
- Prefer explaining *why* something matters over stacking imperatives.

## License

MIT — see [LICENSE](./LICENSE). Forked skills keep their upstream license and copyright
notice in their own folder (e.g. [`security-audit/LICENSE`](./security-audit/LICENSE)).
