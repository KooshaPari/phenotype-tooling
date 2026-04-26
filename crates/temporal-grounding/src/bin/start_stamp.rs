use anyhow::Result;
use chrono::Utc;
use temporal_grounding::{active_agents_path, AgentEntry};

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let id = args.next().unwrap_or_else(gen_id);
    let label = args.next();

    let entry = AgentEntry {
        id: id.clone(),
        started_at: Utc::now().to_rfc3339(),
        label,
    };

    let path = active_agents_path();
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let text = if path.exists() {
        std::fs::read_to_string(&path).ok()
    } else {
        None
    };
    let mut entries: Vec<AgentEntry> = text
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_default();
    entries.push(entry);
    std::fs::write(&path, serde_json::to_string_pretty(&entries)?)?;
    println!("{id}");
    Ok(())
}

fn gen_id() -> String {
    // TODO: replace with uuid v4 for collision-free IDs
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.subsec_nanos())
        .unwrap_or(0);
    format!("agent-{nanos:08x}")
}
