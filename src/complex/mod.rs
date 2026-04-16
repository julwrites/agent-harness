use anyhow::Result;
use std::fs;
use crate::github::GitHubFetcher;

pub async fn run_init(fetcher: &GitHubFetcher, output_file: Option<&str>) -> Result<()> {
    let files = fetcher.get_bootstrap_files().await?;

    let mut prompt = String::new();
    prompt.push_str("I would like to initialize this repository with an AI agent harness. Please create the following files with the specified contents:\n\n");

    for (path, content) in files {
        prompt.push_str(&format!("### File: `{}`\n", path));
        prompt.push_str("```\n");
        prompt.push_str(&content);
        if !content.ends_with('\n') {
            prompt.push('\n');
        }
        prompt.push_str("```\n\n");
    }

    prompt.push_str("Please review the existing files in the repository and update or create these files carefully, ensuring no important existing configuration is lost.\n");
    prompt.push_str("\nAdditionally, please compare the local directories inside `skills/` against the updated agent-bootstrap index.json and prompt me to remove any outdated skills that no longer exist in the remote registry.\n");

    output_prompt(&prompt, output_file)?;

    Ok(())
}

pub async fn run_uninstall(fetcher: &GitHubFetcher, skill: &str, output_file: Option<&str>) -> Result<()> {
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    let mut prompt = String::new();
    prompt.push_str(&format!("I would like to uninstall the '{}' skill from the AI agent harness in this repository. Please remove or revert changes related to the following files:\n\n", skill));

    for (path, _content) in files {
        prompt.push_str(&format!("- `{}`\n", path));
    }

    prompt.push_str("\nPlease ensure that removing these files or their references does not break the rest of the harness.\n");
    prompt.push_str("\nAlso, run the appropriate bash uninstallation commands if their CLI tools are available (e.g. `claude plugin uninstall`, `gemini extensions uninstall`, `codex plugins uninstall`, `opencode plugins uninstall`).\n");

    output_prompt(&prompt, output_file)?;

    Ok(())
}

pub async fn run_install(fetcher: &GitHubFetcher, skill: &str, output_file: Option<&str>) -> Result<()> {
    let files = fetcher.get_skill_files(skill).await?;

    if files.is_empty() {
        println!("No files found for skill '{}'", skill);
        return Ok(());
    }

    let mut prompt = String::new();
    prompt.push_str(&format!("I would like to install the '{}' skill for the AI agent harness in this repository. Please create or update the following files:\n\n", skill));

    for (path, content) in files {
        prompt.push_str(&format!("### File: `{}`\n", path));
        prompt.push_str("```\n");
        prompt.push_str(&content);
        if !content.ends_with('\n') {
            prompt.push('\n');
        }
        prompt.push_str("```\n\n");
    }

    prompt.push_str("Please adapt the configuration as necessary to fit this specific repository's structure and existing configuration.\n");
    prompt.push_str("\nAlso, run the appropriate bash installation commands if their CLI tools are available (e.g. `claude plugin install`, `gemini install extension`, `codex plugins install`, `opencode plugins install`).\n");

    output_prompt(&prompt, output_file)?;

    Ok(())
}

fn output_prompt(prompt: &str, output_file: Option<&str>) -> Result<()> {
    if let Some(file_path) = output_file {
        fs::write(file_path, prompt)?;
        println!("Agent prompt written to {}", file_path);
    } else {
        println!("================ AGENT PROMPT ================\n");
        println!("{}", prompt);
        println!("==============================================");
    }
    Ok(())
}
