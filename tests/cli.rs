use assert_cmd::Command;
use predicates::prelude::*;

#[test]
fn test_cli_help() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("--help");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("Usage: app"));
}

#[test]
fn test_cli_version() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("--version");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("app"));
}

#[test]
fn test_cli_invalid_command() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("invalid-command");
    cmd.assert()
        .failure()
        .stderr(predicate::str::contains("unrecognized subcommand"));
}

#[test]
fn test_headless_no_command() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("--headless");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("No command provided in headless mode."));
}

#[test]
fn test_cli_init_complex() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("--headless").arg("--complex").arg("init");

    // We expect it to run. Due to network failures it might return non-zero code.
    // Let's assert it produces an output or fails gracefully.
    let output = cmd.output().unwrap();

    if output.status.success() {
        assert!(output.stdout.len() > 0 || output.stderr.len() > 0);
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(stderr.contains("GitHub API error") || stderr.contains("Failed to send request") || stderr.contains("rate limit"), "stderr was: {}", stderr);
    }
}

#[test]
fn test_cli_install_skill() {
    let mut cmd = Command::cargo_bin("app").unwrap();
    cmd.arg("--headless").arg("install").arg("test-skill");

    let output = cmd.output().unwrap();

    if output.status.success() {
        assert!(output.stdout.len() > 0 || output.stderr.len() > 0);
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(stderr.contains("Skill 'test-skill' not found") || stderr.contains("GitHub API error") || stderr.contains("Failed to send request") || stderr.contains("rate limit"), "stderr was: {}", stderr);
    }
}
