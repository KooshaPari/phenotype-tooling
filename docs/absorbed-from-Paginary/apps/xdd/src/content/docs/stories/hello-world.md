# Hello World Story

<StoryHeader
    title="Your First phenotype-xdd Operation"
    :duration="2"
    :gif="'/gifs/phenotype-xdd-hello-world.gif'"
    difficulty="beginner"
/>

## Objective

Get phenotype-xdd running with a basic operation.

## Prerequisites

- Rust/Node/Python installed
- phenotype-xdd package installed

## Implementation

```rust
use phenotype-xdd::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize client
    let client = Client::new().await?;
    
    // Execute operation
    let result = client.hello().await?;
    
    println!("Success: {}", result);
    Ok(())
}
```

## Expected Output

```
Success: Hello from phenotype-xdd!
```

## Next Steps

- [Core Integration](./core-integration)
- Read [API Reference](../reference/api)
