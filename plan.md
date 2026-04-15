1. **Update `Cli` to support `--force`**:
   - Add a global `--force` flag in `src/cli/mod.rs` (`pub force: bool`).
2. **Update functions to thread `force`**:
   - Update `simple::run_init(fetcher, force, interactive)` and thread it.
   - Update `simple::run_install(fetcher, skill, force, interactive)` and thread it.
   - Update `write_file_with_prompt(path, content, interactive, force)` to:
     - Check `.gitignore` merging! Wait, `write_file_with_prompt` doesn't know it's `.gitignore`. We should handle `.gitignore` uniquely.
3. **Unique `.gitignore` handling**:
   - In `simple::run_init` or `write_file_with_prompt`:
     - If `path == ".gitignore"` and it already exists, merge the contents: append a section like `# agent-bootstrap` and then append any new lines from the new `.gitignore` that don't already exist in the user's `.gitignore`.
     - Skip the overwrite prompt/logic and write the merged content directly.
4. **Update `get_bootstrap_files`**:
   - In `src/github/mod.rs`:
     - Explicitly skip `.github/workflows/`.
     - Filter out `.agents/messages/` subdirectories (like `receiver-*/`).
     - Fetch `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `.claude-plugin/` recursively from `julwrites/agent-skills` into the bootstrap files list. Wait, these files are in `agent-skills`, not `agent-bootstrap`! The prompt states: "Does not fetch CLAUDE.md, AGENTS.md, GEMINI.md, or the .claude-plugin/ config from agent-skills — init is hardcoded to pull from agent-bootstrap only." So during `app init`, we should also fetch these from `agent-skills`.
5. **Pre-commit checks**:
   - Run `pre_commit_instructions` and make sure it compiles and passes tests.
