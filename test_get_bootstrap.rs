use reqwest::header;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct GitHubContent {
    pub name: String,
    pub path: String,
    #[serde(rename = "type")]
    pub item_type: String,
}

#[tokio::main]
async fn main() {
    let client = reqwest::Client::builder().user_agent("test").build().unwrap();
    let auth_token = std::env::var("GITHUB_TOKEN").ok();

    let list_contents = |owner: &str, repo: &str, path: &str| {
        let url = format!("https://api.github.com/repos/{}/{}/contents/{}", owner, repo, path);
        let mut req = client.get(&url).header(header::ACCEPT, "application/vnd.github.v3+json");
        if let Some(token) = &auth_token {
            req = req.header(header::AUTHORIZATION, format!("token {}", token));
        }
        async move {
            let resp = req.send().await.unwrap();
            let text = resp.text().await.unwrap();
            serde_json::from_str::<Vec<GitHubContent>>(&text).unwrap()
        }
    };

    // Simulate what we need to do
    let root_contents = list_contents("julwrites", "agent-bootstrap", "").await;

    let mut paths_to_fetch = Vec::new();
    for item in root_contents {
        if item.item_type == "file" && (item.name == ".gitignore" || item.name == ".claude") {
            paths_to_fetch.push(item.path.clone());
        } else if item.item_type == "dir" && (item.name == ".agents" || item.name == ".github") {
            let dir_contents = list_contents("julwrites", "agent-bootstrap", &item.path).await;
            for sub_item in dir_contents {
                if sub_item.item_type == "file" {
                    paths_to_fetch.push(sub_item.path.clone());
                } else if sub_item.item_type == "dir" {
                    // Filter workflows and receiver-*
                    if item.name == ".github" && sub_item.name == "workflows" {
                        continue;
                    }
                    if item.name == ".agents" && sub_item.path.starts_with(".agents/messages/receiver-") {
                        continue; // wait, path is .agents/messages/receiver-*. actually the directory is .agents/messages
                    }

                    let sub_dir_contents = list_contents("julwrites", "agent-bootstrap", &sub_item.path).await;
                    for sub_sub_item in sub_dir_contents {
                        if sub_sub_item.item_type == "file" {
                            // Filter receiver-*
                            if sub_sub_item.path.starts_with(".agents/messages/receiver-") {
                                continue;
                            }
                            paths_to_fetch.push(sub_sub_item.path.clone());
                        }
                    }
                }
            }
        }
    }
}
