//! Stream channel configuration for the `pt upgrade` subsystem.
//!
//! Each release stream (introduced by WP-25) can be tracked on one of three
//! release channels:
//!
//! - `stable`   — only releases with at least 1 week of soak time on `beta`
//! - `beta`     — releases with at least 24h of soak time on `nightly`
//! - `nightly`  — every release immediately upon tag
//!
//! Channels are tracked per-stream so each release group can have its own
//! promotion cadence. Configuration is loaded from
//! `$PHENOTYPE_HOME/channels.toml` (default `~/.config/phenotype/channels.toml`).

use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use clap::Args;

/// Channel a release can be promoted through.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Channel {
    /// Releases with >= 1 week soak on beta.
    Stable,
    /// Releases with >= 24h soak on nightly.
    Beta,
    /// Every release immediately on tag.
    Nightly,
}

impl Default for Channel {
    fn default() -> Self {
        Self::Stable
    }
}

impl Channel {
    /// Returns the minimum soak time in hours before this channel is eligible
    /// for promotion to the next channel up.
    pub fn min_soak_hours(&self) -> u64 {
        match self {
            Channel::Nightly => 0,
            Channel::Beta => 24,
            Channel::Stable => 24 * 7,
        }
    }

    /// Returns the rank (0 = highest = stable, 2 = lowest = nightly).
    pub fn rank(&self) -> u8 {
        match self {
            Channel::Stable => 0,
            Channel::Beta => 1,
            Channel::Nightly => 2,
        }
    }

    /// Returns true if `self` is more restrictive (higher rank) than `other`.
    pub fn is_stricter_than(&self, other: Channel) -> bool {
        self.rank() < other.rank()
    }
}

impl std::fmt::Display for Channel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Channel::Stable => write!(f, "stable"),
            Channel::Beta => write!(f, "beta"),
            Channel::Nightly => write!(f, "nightly"),
        }
    }
}

impl std::str::FromStr for Channel {
    type Err = String;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_ascii_lowercase().as_str() {
            "stable" => Ok(Channel::Stable),
            "beta" => Ok(Channel::Beta),
            "nightly" => Ok(Channel::Nightly),
            other => Err(format!("invalid channel '{other}' (expected stable|beta|nightly)")),
        }
    }
}

/// Per-stream channel subscription.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct StreamSubscription {
    /// Stream name (e.g. `core-stream`, `cli-stream`, `ops-stream`).
    pub stream: String,
    /// Current channel the user is tracking.
    pub channel: Channel,
    /// Last version pinned on the current channel.
    pub pinned_version: String,
    /// Unix timestamp of the last successful upgrade check.
    pub last_checked_at: u64,
}

/// Top-level channels config file.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ChannelsConfig {
    /// Map of stream name -> subscription.
    pub subscriptions: BTreeMap<String, StreamSubscription>,
    /// Default channel for new streams not yet subscribed.
    #[serde(default = "default_channel")]
    pub default_channel: Channel,
}

fn default_channel() -> Channel {
    Channel::Stable
}

impl ChannelsConfig {
    /// Returns the default config path: `$PHENOTYPE_HOME/channels.toml` or
    /// `~/.config/phenotype/channels.toml` if the env var is unset.
    pub fn default_path() -> PathBuf {
        if let Ok(p) = std::env::var("PHENOTYPE_HOME") {
            PathBuf::from(p).join("channels.toml")
        } else {
            let home = std::env::var("USERPROFILE")
                .or_else(|_| std::env::var("HOME"))
                .unwrap_or_else(|_| ".".to_string());
            PathBuf::from(home).join(".config").join("phenotype").join("channels.toml")
        }
    }

    /// Loads the config from `path`. Returns a default config if the file
    /// doesn't exist yet.
    pub fn load_or_default(path: &Path) -> std::io::Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let raw = std::fs::read_to_string(path)?;
        toml::from_str(&raw)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))
    }

    /// Saves the config to `path`. Creates parent directories as needed.
    pub fn save(&self, path: &Path) -> std::io::Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let raw = toml::to_string_pretty(self)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
        std::fs::write(path, raw)
    }

    /// Returns the subscription for `stream`, or inserts a default one
    /// using `default_channel` + version `0.0.0` if absent.
    pub fn get_or_default_mut(&mut self, stream: &str) -> &mut StreamSubscription {
        self.subscriptions.entry(stream.to_string()).or_insert_with(|| StreamSubscription {
            stream: stream.to_string(),
            channel: self.default_channel,
            pinned_version: "0.0.0".to_string(),
            last_checked_at: 0,
        })
    }
}

/// Arguments for `pt upgrade`.
#[derive(Debug, Args)]
pub struct UpgradeArgs {
    /// Channel to select for the default stream policy.
    #[arg(value_parser = parse_channel)]
    pub channel: Option<Channel>,
    /// Optional stream to update instead of the default policy.
    #[arg(long)]
    pub stream: Option<String>,
    /// Override the channel configuration path.
    #[arg(long)]
    pub config: Option<PathBuf>,
}

fn parse_channel(value: &str) -> Result<Channel, String> {
    value.parse()
}

/// Persist the selected channel policy and report the resulting subscription.
pub fn run(args: UpgradeArgs, _verbosity: u8) -> i32 {
    let path = args.config.unwrap_or_else(ChannelsConfig::default_path);
    let mut config = match ChannelsConfig::load_or_default(&path) {
        Ok(config) => config,
        Err(error) => {
            eprintln!("pt upgrade: cannot load {}: {error}", path.display());
            return crate::exit_code::CONFIG;
        }
    };
    if let Some(channel) = args.channel {
        config.default_channel = channel;
    }
    if let Some(stream) = args.stream {
        let channel = config.default_channel;
        let subscription = config.get_or_default_mut(&stream);
        subscription.channel = channel;
        println!("{stream}: {channel}");
    } else {
        println!("default: {}", config.default_channel);
    }
    match config.save(&path) {
        Ok(()) => crate::exit_code::OK,
        Err(error) => {
            eprintln!("pt upgrade: cannot save {}: {error}", path.display());
            crate::exit_code::CONFIG
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn channel_soak_hours_match_phase6_plan() {
        assert_eq!(Channel::Nightly.min_soak_hours(), 0);
        assert_eq!(Channel::Beta.min_soak_hours(), 24);
        assert_eq!(Channel::Stable.min_soak_hours(), 24 * 7);
    }

    #[test]
    fn channel_rank_ordering() {
        assert!(Channel::Stable.rank() < Channel::Beta.rank());
        assert!(Channel::Beta.rank() < Channel::Nightly.rank());
        assert!(Channel::Stable.is_stricter_than(Channel::Nightly));
    }

    #[test]
    fn channel_from_str_round_trip() {
        for c in [Channel::Stable, Channel::Beta, Channel::Nightly] {
            let s = c.to_string();
            let parsed: Channel = s.parse().expect("round-trip");
            assert_eq!(parsed, c);
        }
    }

    #[test]
    fn default_config_round_trip() {
        let cfg = ChannelsConfig::default();
        let raw = toml::to_string(&cfg).expect("serialize");
        let parsed: ChannelsConfig = toml::from_str(&raw).expect("deserialize");
        assert_eq!(parsed, cfg);
    }

    #[test]
    fn get_or_default_inserts_default() {
        let mut cfg = ChannelsConfig::default();
        let sub = cfg.get_or_default_mut("cli-stream");
        assert_eq!(sub.stream, "cli-stream");
        assert_eq!(sub.channel, Channel::Stable);
        assert_eq!(sub.pinned_version, "0.0.0");
    }
}
