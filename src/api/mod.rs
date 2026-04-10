use anyhow::Result;
use axum::{
    routing::get,
    Router,
    Json,
    extract::Path,
};
use std::sync::Arc;
use serde::Serialize;

use crate::github::GitHubFetcher;

// We use Arc to share the fetcher across requests
struct AppState {
    fetcher: GitHubFetcher,
}

#[derive(Serialize)]
struct ApiFile {
    path: String,
    content: String,
}

#[derive(Serialize)]
struct ApiResponse {
    status: String,
    files: Option<Vec<ApiFile>>,
    message: Option<String>,
}

pub async fn run_service(port: u16) -> Result<()> {
    let fetcher = GitHubFetcher::new()?;
    let shared_state = Arc::new(AppState { fetcher });

    // build our application with a route
    let app = Router::new()
        .route("/", get(|| async { "Agent Harness API Server is running!" }))
        .route("/api/init", get(init_handler))
        .route("/api/skills", get(list_skills_handler))
        .route("/api/skills/{skill}", get(get_skill_handler))
        .with_state(shared_state);

    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", port)).await?;
    println!("API Server running on http://0.0.0.0:{}", port);

    axum::serve(listener, app).await?;

    Ok(())
}

async fn init_handler(axum::extract::State(state): axum::extract::State<Arc<AppState>>) -> Json<ApiResponse> {
    match state.fetcher.get_bootstrap_files().await {
        Ok(files) => {
            let api_files = files.into_iter().map(|(path, content)| ApiFile { path, content }).collect();
            Json(ApiResponse {
                status: "success".to_string(),
                files: Some(api_files),
                message: None,
            })
        }
        Err(e) => {
            Json(ApiResponse {
                status: "error".to_string(),
                files: None,
                message: Some(e.to_string()),
            })
        }
    }
}

async fn list_skills_handler(axum::extract::State(state): axum::extract::State<Arc<AppState>>) -> Json<ApiResponse> {
    match state.fetcher.list_skills().await {
        Ok(skills) => {
            // we re-purpose ApiResponse for simplicity
            Json(ApiResponse {
                status: "success".to_string(),
                files: None,
                message: Some(skills.join(",")),
            })
        }
        Err(e) => {
            Json(ApiResponse {
                status: "error".to_string(),
                files: None,
                message: Some(e.to_string()),
            })
        }
    }
}

async fn get_skill_handler(
    Path(skill): Path<String>,
    axum::extract::State(state): axum::extract::State<Arc<AppState>>,
) -> Json<ApiResponse> {
    match state.fetcher.get_skill_files(&skill).await {
        Ok(files) => {
            let api_files = files.into_iter().map(|(path, content)| ApiFile { path, content }).collect();
            Json(ApiResponse {
                status: "success".to_string(),
                files: Some(api_files),
                message: None,
            })
        }
        Err(e) => {
            Json(ApiResponse {
                status: "error".to_string(),
                files: None,
                message: Some(e.to_string()),
            })
        }
    }
}
