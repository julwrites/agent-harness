use anyhow::Result;
use std::fs;
use std::path::Path;
use dialoguer::{Confirm, theme::ColorfulTheme};
use crate::github::GitHubFetcher;

pub async fn run_init(fetcher: &GitHubFetcher, interactive: bool, force: bool) -> Result<()> {
    println!("Fetching bootstrap files from julwrites/agent-bootstrap...");
    let files = fetcher.get_bootstrap_files().await?;

    for (path, content) in &files {
        write_file_with_prompt(path, content, interactive, force)?;
    }

    println!("Fetching remote skills list to check for outdated local skills...");
    if let Ok(remote_skills) = fetcher.list_skills().await {
        if Path::new("skills").is_dir() {
            if let Ok(entries) = fs::read_dir("skills") {
                for entry in entries.flatten() {
                    if let Ok(file_type) = entry.file_type() {
                        if file_type.is_dir() {
                            let skill_name = entry.file_name().to_string_lossy().to_string();
                            if !remote_skills.contains(&skill_name) {
                                if interactive {
                                    let remove = Confirm::with_theme(&ColorfulTheme::default())
                                        .with_prompt(format!("Skill '{}' is no longer in the remote registry. Remove it?", skill_name))
                                        .default(true)
                                        .interact()?;
                                    if remove {
                                        let _ = Box::pin(run_uninstall(fetcher, &skill_name, interactive)).await;
                                    }
                                } else {
                                    println!("Headless mode: skipping removal of outdated skill '{}'.", skill_name);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    println!("Bootstrap complete.");
    Ok(())
}

pub async fn run_install(fetcher: &GitHubFetcher, skill: &str, interactive: bool, force: bool) -> Result<()> {
    println!("Fetching files for skill '{}'...", skill);
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    for (path, content) in &files {
        if path == "external_skill" { continue; }
        write_file_with_prompt(path, content, interactive, force)?;
    }

    println!("Skill '{}' installed.", skill);

    let agents = vec![
        ("claude", "claude plugin install", "claude plugin uninstall"),
        ("gemini", "gemini install extension", "gemini uninstall extension"),
        ("codex", "codex plugins install", "codex plugins uninstall"),
        ("opencode", "opencode plugins install", "opencode plugins uninstall"),
    ];

    let repo_url = files.iter()
        .find(|(p, _)| p == "external_skill")
        .map(|(_, c)| c.clone())
        .unwrap_or_else(|| format!("https://github.com/julwrites/agent-skills/tree/main/skills/{}", skill));

    for (agent, install_cmd, _) in &agents {
        if std::process::Command::new("command").arg("-v").arg(agent).output().map(|o| o.status.success()).unwrap_or(false) {
            println!("Found {} agent, installing...", agent);
            let cmd = format!("{} {}", install_cmd, repo_url);
            let _ = std::process::Command::new("bash").arg("-c").arg(&cmd).status();
        }
    }

    Ok(())
}

pub async fn run_uninstall(fetcher: &GitHubFetcher, skill: &str, interactive: bool) -> Result<()> {
    println!("Fetching files for skill '{}' to determine what to remove...", skill);
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    for (path, _content) in &files {
        if path == "external_skill" { continue; }
        let file_path = Path::new(path);
        if file_path.exists() {
            let mut remove = true;
            if interactive {
                remove = Confirm::with_theme(&ColorfulTheme::default())
                    .with_prompt(format!("Remove file '{}'?", path))
                    .default(true)
                    .interact()?;
            }
            if remove {
                fs::remove_file(file_path)?;
                println!("Removed '{}'", path);
            } else {
                println!("Skipped removing '{}'", path);
            }
        }
    }

    println!("Skill '{}' uninstalled.", skill);

    let agents = vec![
        ("claude", "claude plugin install", "claude plugin uninstall"),
        ("gemini", "gemini install extension", "gemini uninstall extension"),
        ("codex", "codex plugins install", "codex plugins uninstall"),
        ("opencode", "opencode plugins install", "opencode plugins uninstall"),
    ];

    for (agent, _, uninstall_cmd) in &agents {
        if std::process::Command::new("command").arg("-v").arg(agent).output().map(|o| o.status.success()).unwrap_or(false) {
            println!("Found {} agent, uninstalling...", agent);
            let cmd = format!("{} {}", uninstall_cmd, skill);
            let _ = std::process::Command::new("bash").arg("-c").arg(&cmd).status();
        }
    }

    Ok(())
}

fn write_file_with_prompt(path: &str, content: &str, interactive: bool, force: bool) -> Result<()> {
    let file_path = Path::new(path);

    if let Some(parent) = file_path.parent() {
        if !parent.exists() {
            fs::create_dir_all(parent)?;
        }
    }

    if file_path.exists() {
        if path == ".gitignore" {
            // Special case: merge .gitignore
            let existing_content = fs::read_to_string(file_path)?;
            let existing_lines: Vec<&str> = existing_content.lines().collect();
            let mut to_append = Vec::new();
            for line in content.lines() {
                if !existing_lines.contains(&line) {
                    to_append.push(line);
                }
            }
            if !to_append.is_empty() {
                let append_str = format!("\n\n# agent-bootstrap\n{}\n", to_append.join("\n"));
                fs::write(file_path, existing_content + &append_str)?;
                println!("Merged '{}'", path);
            } else {
                println!("No new lines to merge into '{}'", path);
            }
            return Ok(());
        }

        if interactive {
            let overwrite = Confirm::with_theme(&ColorfulTheme::default())
                .with_prompt(format!("File '{}' already exists. Overwrite?", path))
                .default(false)
                .interact()?;

            if !overwrite {
                println!("Skipping '{}'", path);
                return Ok(());
            }
        } else {
            if force {
                println!("Overwriting existing '{}' due to --force flag", path);
            } else {
                println!("Skipping existing '{}' (use --force to overwrite)", path);
                return Ok(());
            }
        }
    }

    fs::write(file_path, content)?;
    println!("Wrote '{}'", path);

    Ok(())
}
