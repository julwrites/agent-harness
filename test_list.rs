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
    let url = "https://api.github.com/repos/julwrites/agent-bootstrap/contents/.agents/messages";
    let client = reqwest::Client::builder().user_agent("test").build().unwrap();
    let resp = client.get(url).header(header::ACCEPT, "application/vnd.github.v3+json").send().await.unwrap();
    let text = resp.text().await.unwrap();
    let contents: Vec<GitHubContent> = serde_json::from_str(&text).unwrap();
    for c in contents {
        println!("{} {} {}", c.name, c.path, c.item_type);
    }
}
