use std::process::Command;
use reqwest::Client;
use std::time::Duration;
use tokio::time::sleep;
use serde_json::Value;

#[tokio::test]
async fn test_api_service() {
    let cargo_bin = assert_cmd::cargo::cargo_bin("app");

    // Start the service in the background
    let mut child = Command::new(cargo_bin)
        .arg("service")
        .arg("--port")
        .arg("3001") // Use a different port to avoid conflicts
        .spawn()
        .expect("Failed to start API service");

    // Give it a moment to start
    sleep(Duration::from_millis(500)).await;

    let client = Client::new();

    // Test root endpoint
    let res = client.get("http://localhost:3001/")
        .send()
        .await
        .expect("Failed to reach API");
    assert!(res.status().is_success());
    let text = res.text().await.unwrap();
    assert_eq!(text, "Agent Harness API Server is running!");

    // Test a failure case since github API might fail or rate limit
    let res = client.get("http://localhost:3001/api/skills/non-existent-skill-12345")
        .send()
        .await
        .expect("Failed to fetch from API");

    assert!(res.status().is_success()); // axum route returns 200 with error JSON
    let json: Value = res.json().await.unwrap();
    assert_eq!(json["status"], "error");

    // Kill the service
    child.kill().expect("Failed to kill API service");
}
