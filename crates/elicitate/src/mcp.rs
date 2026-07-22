//! MCP server module — wraps the library in a single `elicitate_mcp` tool.

pub mod router;
pub mod shutdown;

pub use router::ElicitateMcp;