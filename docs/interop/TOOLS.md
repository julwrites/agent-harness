# Agent Tools Reference

This file is auto-generated. Do not edit manually.

| Tool | Risk | Description | Usage |
| :--- | :--- | :--- | :--- |
| task_create | **L1** | Create a new development task. | `task_create(category, title, description)` |
| task_list | **L0** | List existing tasks, optionally filtered by status or category. | `task_list(status, category, archived)` |
| task_update | **L1** | Update the status of an existing task. | `task_update(task_id, status)` |
| task_show | **L0** | Show the details of a specific task. | `task_show(task_id)` |
| task_validate | **L0** | Validate all task files for integrity and correctness. | `task_validate(format)` |
| code_index_stats | **L0** | Show codebase statistics. | `code_index_stats(format)` |
| task_context | **L0** | Show tasks that are currently in progress. | `task_context()` |
| task_archive | **L1** | Archive a completed task. | `task_archive(task_id)` |
| memory_create | **L1** | Create a new long-term memory. | `memory_create(title, content, tags)` |
| memory_list | **L0** | List existing memories, optionally filtered by tag. | `memory_list(tag, limit)` |
| memory_read | **L0** | Read a specific memory. | `memory_read(filename)` |
| index_impact | **L0** | Check impact of a file change on documentation. | `index_impact(file)` |
| index_add | **L2** | Add or update a documentation index entry. | `index_add(doc, related, depends)` |
| index_check | **L0** | Check integrity of the documentation index. | `index_check()` |
| agent_send | **L1** | Send a message to another agent or "public". | `agent_send(recipient, message)` |
| quality_verify | **L0** | Run full verification (tests and validation). | `quality_verify(format)` |
| quality_test | **L0** | Run unit tests. | `quality_test(pattern, verbose, format)` |
| quality_lint | **L0** | Run linters. | `quality_lint(files)` |
| quality_map | **L1** | Scaffold a test file for a source file. | `quality_map(src_file)` |
| agent_read | **L1** | Read messages from your inbox. | `agent_read(agent_id)` |
| agent_list | **L0** | List active agents. | `agent_list()` |
| code_index_init | **L2** | Initialize the code index by selecting source roots. | `code_index_init()` |
| code_index_refresh | **L1** | Re-index the codebase. | `code_index_refresh()` |
| code_index_list | **L0** | List indexed files. | `code_index_list(format)` |
| code_index_search | **L0** | Search for symbols in the code index (fuzzy match). | `code_index_search(query, format)` |
| code_index_lookup | **L0** | Lookup a specific symbol definition or symbols in a file. | `code_index_lookup(target, format)` |
| code_index_references | **L0** | Find text references to a symbol in the codebase. | `code_index_references(symbol, format)` |
