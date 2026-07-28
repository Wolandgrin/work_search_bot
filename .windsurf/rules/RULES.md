---
trigger: always_on
description:
globs:
---

# Critical Rules for Working with Cascade

## MANDATORY RULES:

1. **DON'T WASTE TOKENS** - don't do what the user can do themselves (git commit, simple verification commands)

2. **DON'T ADD EMPTY LINES** between code blocks (especially with trailing whitespaces) - this breaks flake8

3. **IMPORTS ALWAYS AT THE TOP** of the file, never inside functions. `logger = logging.getLogger(__name__)` is NOT an import — place it AFTER all imports, before the first class/function. Never put it between import groups.

4. **PROPOSE IDEAS FIRST, USER WILL CHOOSE** - don't implement immediately, suggest solution options

5. **WORK THOUGHTFULLY, CONCISELY** - no fluff, unnecessary explanations, or unsolicited actions

6. **ACCOUNT FOR UNCERTAINTY < 0.1** - always honestly assess solution success probability with justification

7. **COMMANDS IN ONE LINE** - when giving a command, always give it as a single line

8. **ALWAYS READ RULES.md** before starting any task (this file: `.windsurf/rules/RULES.md`)

9. **ALWAYS UPDATE tasks.md** on the fly: `.windsurf/rules/tasks.md`

10. **FLAKE8/PYLINT ERRORS WITHOUT EXPLICIT REQUEST** — never fix on your own:
    - If import is actually used in code → say "this is a linter glitch, used on line X"
    - If unclear → ask what to do
    - Never fix without being asked

11. **NO INVASIVE CHANGES IN FILES** not related to the current task — even if they have errors

12. **GIT OPERATIONS** (commit, push, reset, checkout, cherry-pick, merge, rebase) — only on explicit user request

13. **NO EMOJIS** unless explicitly requested

14. **ALWAYS USE Architecture.md** to understand project structure before starting a task

15. **KEEP RULES.md AND MEMORY IN SYNC** — when adding/changing any rule, update both `.windsurf/rules/RULES.md` AND the memory record simultaneously

16. **tasks.md ARCHIVED TASKS** — when a task is completed (merged/fixed/closed), immediately move it to `archived_tasks.md` (`.windsurf/rules/archived_tasks.md`). Active Tasks and Backlog in `tasks.md` contain only in-progress or pending work.

17. **NO `time.sleep()`, raw HTTP calls, hardcoded timeouts** — use framework abstractions

18. **DOMAIN GATE** — determine domain → load matching standards → then code

19. **EXPLAIN STEPS** — always provide clear explanations before executing commands, describing what will be done and why

---

## References

- **Global Tasks:** `.windsurf/rules/tasks.md`
- **MCP Tools Reference:** `.windsurf/rules/mcp_servers.md`

---

**ALWAYS follow these rules in all interactions.**
