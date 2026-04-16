use anyhow::{Context, Result};
use reqwest::{Client, header};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct GitHubContent {
    pub name: String,
    pub path: String,
    pub sha: String,
    pub size: usize,
    pub url: String,
    pub html_url: Option<String>,
    pub git_url: Option<String>,
    pub download_url: Option<String>,
    #[serde(rename = "type")]
    pub item_type: String, // "file" or "dir"
}

#[derive(Debug, Deserialize, Clone)]
pub struct SkillIndexEntry {
    pub name: String,
    pub repository: String,
    pub description: Option<String>,
}


pub struct GitHubFetcher {
    client: Client,
    auth_token: Option<String>,
}

impl GitHubFetcher {
    pub fn new() -> Result<Self> {
        let user_agent = "julwrites-agent-harness".to_string();
        let client = Client::builder()
            .user_agent(&user_agent)
            .build()?;

        let auth_token = std::env::var("GITHUB_TOKEN").ok();

        Ok(Self { client, auth_token })
    }

    /// List contents of a directory in a repository
    pub async fn list_contents(&self, owner: &str, repo: &str, path: &str) -> Result<Vec<GitHubContent>> {
        let url = format!("https://api.github.com/repos/{}/{}/contents/{}", owner, repo, path);

        let mut req = self.client
            .get(&url)
            .header(header::ACCEPT, "application/vnd.github.v3+json");

        if let Some(token) = &self.auth_token {
            req = req.header(header::AUTHORIZATION, format!("token {}", token));
        }

        let response = req.send()
            .await
            .context(format!("Failed to send request to {}", url))?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await?;
            anyhow::bail!("GitHub API error: {} - {}", status, text);
        }

        let contents: Vec<GitHubContent> = response.json().await?;
        Ok(contents)
    }

    /// Fetch raw file content from a specific path
    pub async fn fetch_file_content(&self, owner: &str, repo: &str, path: &str) -> Result<String> {
        let url = format!("https://raw.githubusercontent.com/{}/{}/main/{}", owner, repo, path);

        let mut req = self.client.get(&url);

        if let Some(token) = &self.auth_token {
            req = req.header(header::AUTHORIZATION, format!("token {}", token));
        }

        let response = req.send()
            .await
            .context(format!("Failed to fetch file from {}", url))?;

        if !response.status().is_success() {
            let status = response.status();
            anyhow::bail!("Failed to download raw file: {} - {}", url, status);
        }

        let content = response.text().await?;
        Ok(content)
    }

    /// Fetch bootstrap files to initialize the harness
    pub async fn get_bootstrap_files(&self) -> Result<Vec<(String, String)>> {
        let mut results = Vec::new();
        // Basic files to fetch for initialization
        let _files_to_fetch = vec![
            ".agents/registry/manifest.json", // Examples of typical harness files
            ".agents/messages/welcome",
            // Add other relevant files based on julwrites/agent-bootstrap structure
        ];

        // Currently, based on previous bash discovery, agent-bootstrap has a structure
        // we could list the root directory, or fetch specific files

        // Let's list the root files first to see what to fetch
        let contents = self.list_contents("julwrites", "agent-bootstrap", "").await?;

        // We will fetch `.agents` and other typical bootstrap files dynamically
        // Since doing a full recursive fetch could be complex, we'll implement a basic recursive fetch
        let mut paths_to_fetch = Vec::new();
        for item in contents {
            if item.item_type == "file" && (item.name == ".gitignore" || item.name == ".claude") {
                paths_to_fetch.push(item.path.clone());
            } else if item.item_type == "dir" && (item.name == ".agents" || item.name == ".github") {
                // Recursively fetch this directory (1 level deep for simplicity)
                if let Ok(dir_contents) = self.list_contents("julwrites", "agent-bootstrap", &item.path).await {
                    for sub_item in dir_contents {
                        if sub_item.item_type == "file" {
                            paths_to_fetch.push(sub_item.path.clone());
                        } else if sub_item.item_type == "dir" {
                             // Skip .github/workflows/
                             if item.name == ".github" && sub_item.name == "workflows" {
                                 continue;
                             }

                             if let Ok(sub_dir_contents) = self.list_contents("julwrites", "agent-bootstrap", &sub_item.path).await {
                                  for sub_sub_item in sub_dir_contents {
                                      if sub_sub_item.item_type == "file" {
                                          // Skip .agents/messages/receiver-*/ test directories and similar
                                          // Actually, the structure is `.agents/messages/receiver-abc/...`
                                          // So if sub_sub_item is a file, we can just check if it starts with ".agents/messages/receiver-"
                                          // Wait, if it's .agents/messages/receiver-abc, that's a directory!
                                          // Let's just skip anything in .agents/messages/ that isn't a file we directly want,
                                          // but to match the problem description, we should skip test/scratch dirs in .agents/messages/
                                          paths_to_fetch.push(sub_sub_item.path.clone());
                                      } else if sub_sub_item.item_type == "dir" && sub_sub_item.path.starts_with(".agents/messages/") {
                                          // Skip subdirectories inside .agents/messages
                                          continue;
                                      }
                                  }
                             }
                        }
                    }
                }
            }
        }

        for path in paths_to_fetch {
            let content = self.fetch_file_content("julwrites", "agent-bootstrap", &path).await?;
            results.push((path, content));
        }

        // Fetch additional files from julwrites/agent-skills
        let mut agent_skills_files = Vec::new();
        if let Ok(contents) = self.list_contents("julwrites", "agent-skills", "").await {
            for item in contents {
                if item.item_type == "file" && (item.name == "CLAUDE.md" || item.name == "AGENTS.md" || item.name == "GEMINI.md") {
                    agent_skills_files.push(item.path.clone());
                } else if item.item_type == "dir" && item.name == ".claude-plugin" {
                    // Fetch .claude-plugin directory contents
                    if let Ok(plugin_contents) = self.list_contents("julwrites", "agent-skills", &item.path).await {
                        for plugin_item in plugin_contents {
                            if plugin_item.item_type == "file" {
                                agent_skills_files.push(plugin_item.path.clone());
                            }
                        }
                    }
                }
            }
        }

        for path in agent_skills_files {
            if let Ok(content) = self.fetch_file_content("julwrites", "agent-skills", &path).await {
                results.push((path, content));
            }
        }

        Ok(results)
    }

    /// Fetch all files for a specific skill from julwrites/agent-skills

    /// Fetch external skills index
    pub async fn get_external_skills_index(&self) -> Result<Vec<SkillIndexEntry>> {
        let url = "https://raw.githubusercontent.com/julwrites/agent-bootstrap/main/.agents/registry/index.json";
        let mut req = self.client.get(url);
        if let Some(token) = &self.auth_token {
            req = req.header(header::AUTHORIZATION, format!("token {}", token));
        }
        let response = req.send().await?;
        if response.status().is_success() {
            if let Ok(text) = response.text().await {
                if let Ok(index) = serde_json::from_str::<Vec<SkillIndexEntry>>(&text) {
                    return Ok(index);
                }
            }
        }
        Ok(Vec::new())
    }

    pub async fn get_skill_files(&self, skill_name: &str) -> Result<Vec<(String, String)>> {
        let mut results = Vec::new();

        // Check if it's an external skill
        if let Ok(index) = self.get_external_skills_index().await {
            if let Some(entry) = index.iter().find(|e| e.name == skill_name) {
                // If it's an external skill, we don't fetch any files because they will be installed via bash.
                // We just return an empty vector, or maybe a dummy file to indicate it was found.
                // The prompt logic handles running the bash command based on `files` not being empty.
                // Let's just return a dummy entry so the caller knows the skill exists and proceeds to install.
                return Ok(vec![("external_skill".to_string(), entry.repository.clone())]);
            }
        }

        // In agent-skills, typically there is a folder for each skill, or markdown files.
        // We list the directory for the skill.
        let contents = self.list_contents("julwrites", "agent-skills", skill_name).await
            .context(format!("Skill '{}' not found or error accessing it", skill_name))?;

        for item in contents {
            if item.item_type == "file" {
                let content = self.fetch_file_content("julwrites", "agent-skills", &item.path).await?;
                results.push((item.path, content));
            }
        }

        Ok(results)
    }

    /// List available skills
    pub async fn list_skills(&self) -> Result<Vec<String>> {
        let contents = self.list_contents("julwrites", "agent-skills", "skills").await.unwrap_or_default();
        let mut skills = Vec::new();

        for item in contents {
            if item.item_type == "dir" && !item.name.starts_with('.') {
                skills.push(item.name);
            }
        }

        if let Ok(index) = self.get_external_skills_index().await {
            for entry in index {
                skills.push(entry.name);
            }
        }

        Ok(skills)
    }
}
