#[tokio::main]
async fn main() {
    let url = "https://api.github.com/repos/julwrites/agent-bootstrap/contents/.agents/messages";
    let client = reqwest::Client::builder().user_agent("test").build().unwrap();
    let resp = client.get(url).send().await.unwrap().text().await.unwrap();
    println!("{}", resp);
}
