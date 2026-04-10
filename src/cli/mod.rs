use clap::{Parser, Subcommand};

#[derive(Parser, Debug)]
#[command(author, version, about = "Agent harness utility for bootstrapping and managing AI agent skills", long_about = None)]
pub struct Cli {
    /// Skip the TUI and run in headless CLI mode
    #[arg(long, global = true)]
    pub headless: bool,

    /// Generate an AI agent prompt instead of directly modifying files
    #[arg(long, global = true)]
    pub complex: bool,

    /// Optional output file for complex mode prompts (defaults to stdout)
    #[arg(long, global = true)]
    pub output: Option<String>,

    #[command(subcommand)]
    pub command: Option<Commands>,
}

#[derive(Subcommand, Debug, Clone)]
pub enum Commands {
    /// Initialize agent bootstrap files in the repository
    Init,
    /// Update existing agent configurations
    Update,
    /// Install a specific agent skill
    Install {
        /// Name of the skill to install
        skill: String,
    },
    /// Uninstall a specific agent skill
    Uninstall {
        /// Name of the skill to uninstall
        skill: String,
    },
    /// Run as a hosted API service
    Service {
        /// Port to run the service on
        #[arg(short, long, default_value = "3000")]
        port: u16,
    },
}
