use std::process::{Command, Stdio};

fn main() -> std::io::Result<()> {
    let out = Command::new("python")
        .arg("gen.py")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()?;
    println!("{}", String::from_utf8(out.stdout).unwrap());
    eprintln!("{}", String::from_utf8(out.stderr).unwrap());
    assert!(out.status.success(), "Python returned a non-zero status code");
    Ok(())
}
