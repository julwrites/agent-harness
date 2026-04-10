use anyhow::Result;
use std::fs;
use std::path::Path;
use dialoguer::{Confirm, theme::ColorfulTheme};
use crate::github::GitHubFetcher;

pub async fn run_init(fetcher: &GitHubFetcher, interactive: bool) -> Result<()> {
    println!("Fetching bootstrap files from julwrites/agent-bootstrap...");
    let files = fetcher.get_bootstrap_files().await?;

    for (path, content) in files {
        write_file_with_prompt(&path, &content, interactive)?;
    }

    println!("Bootstrap complete.");
    Ok(())
}

pub async fn run_install(fetcher: &GitHubFetcher, skill: &str, interactive: bool) -> Result<()> {
    println!("Fetching files for skill '{}'...", skill);
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    for (path, content) in files {
        write_file_with_prompt(&path, &content, interactive)?;
    }

    println!("Skill '{}' installed.", skill);
    Ok(())
}

pub async fn run_uninstall(fetcher: &GitHubFetcher, skill: &str, interactive: bool) -> Result<()> {
    println!("Fetching files for skill '{}' to determine what to remove...", skill);
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    for (path, _content) in files {
        let file_path = Path::new(&path);
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
    Ok(())
}

fn write_file_with_prompt(path: &str, content: &str, interactive: bool) -> Result<()> {
    let file_path = Path::new(path);

    if let Some(parent) = file_path.parent() {
        if !parent.exists() {
            fs::create_dir_all(parent)?;
        }
    }

    if file_path.exists() {
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
            // in non-interactive headless, we just overwrite by default
            // (or we could assume skip, let's assume overwrite for harness updates)
            println!("Overwriting existing '{}'", path);
        }
    }

    fs::write(file_path, content)?;
    println!("Wrote '{}'", path);

    Ok(())
}
