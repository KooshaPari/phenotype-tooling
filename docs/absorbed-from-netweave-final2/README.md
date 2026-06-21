# netweave-final2

**NetWeave Traffic Simulation** - A Go-based traffic simulation system with real-time visualization, featuring procedural road network generation, vehicle routing, and interactive web-based visualization.

## Overview

NetWeave is a comprehensive traffic simulation platform that generates realistic road networks and simulates vehicle movement through them. It combines a Go backend for simulation logic with an HTML5 Canvas frontend for real-time visualization, providing an interactive environment for studying traffic patterns, urban planning, and routing algorithms.

## Purpose

The system serves multiple purposes:
- **Urban Planning**: Model road network layouts and traffic flow
- **Algorithm Testing**: Evaluate routing algorithms (A*, Dijkstra)
- **Traffic Analysis**: Study congestion patterns and bottlenecks
- **Education**: Visualize graph theory and traffic concepts
- **Game Development**: Procedural city generation for games

## Key Features

### Network Generation
- **Grid Layout**: Traditional Manhattan-style grid with intersections
- **Radial Layout**: Circular/spoke pattern with ring roads
- **Organic Layout**: Natural city growth simulation
- **Random Layout**: Fully randomized network generation
- **Kush Layout**: Realistic multi-zone city (downtown, commercial, industrial, residential)

### Simulation Engine
- **Vehicle Agents**: Autonomous vehicles with destination-based routing
- **Road Types**: Highway, major, minor, and local roads with different speeds
- **Intersections**: Traffic lights and major/minor intersections
- **POI System**: Points of Interest (residential, commercial) for routing
- **Real-time Stats**: Live vehicle count, speed, and congestion metrics

### Visualization
- **Interactive Canvas**: HTML5 Canvas with zoom and pan support
- **Click Interaction**: Select vehicles and POIs for detailed info
- **Animated Traffic**: Smooth vehicle movement along roads
- **Color-coded Elements**: Different colors for road types and zones
- **Stats Panel**: Live dashboard with simulation metrics

### ML Integration
- **Graph Generation**: ML-assisted network topology creation
- **Image Processing**: Canvas rendering and export
- **Enhancement**: Visual quality improvements

## Quick Start

### Prerequisites
- Go 1.18+
- Modern web browser
- Optional: WebSocket support for real-time updates

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd netweave-final2

# Install Go dependencies
go mod download

# Or with install script
chmod +x install.sh
./install.sh
```

### Running the Server

```bash
# Run the web server
go run cmd/netweave/main.go

# Or with custom port
go run cmd/netweave/main.go -port 9090

# Server will be available at http://localhost:8080
```

### Using the Web Interface

1. Open browser to `http://localhost:8080`
2. Choose a layout type (Grid, Radial, Organic, Random, Kush)
3. Click "Generate Network" to create road network
4. Add vehicles using the control panel
5. Click "Start" to begin simulation
6. Click on vehicles or POIs for detailed information

### Key Controls

| Button | Action |
|--------|--------|
| Start | Begin simulation |
| Stop | Pause simulation |
| Reset | Clear all vehicles |
| Generate Network | Create new road layout |
| Add Vehicles | Spawn N vehicles |
| Speed Slider | Adjust simulation speed |

## Project Structure

```
netweave-final2/
├── cmd/
│   └── netweave/
│       └── main.go              # Application entry point
├── internal/
│   ├── canvas/
│   │   ├── interface.go         # Canvas drawing interface
│   │   ├── server.go            # Canvas server
│   │   └── tools.go             # Drawing utilities
│   ├── graph/
│   │   ├── edge.go              # Road/edge data structure
│   │   ├── network.go           # Network topology management
│   │   ├── node.go              # Intersection/node structure
│   │   └── poi.go               # Point of Interest
│   ├── ml/
│   │   ├── graph_generator.go   # ML-assisted generation
│   │   ├── image_enhancer.go    # Image processing
│   │   └── image_processor.go   # Canvas image processing
│   ├── render/
│   │   ├── animation_renderer.go # Animation system
│   │   ├── image2image.go       # Image transformations
│   │   ├── map_renderer.go      # Map visualization
│   │   └── visualization.go     # Visualization engine
│   ├── simulation/
│   │   ├── cellular_automata.go # Traffic CA model
│   │   ├── intersection.go      # Intersection logic
│   │   ├── random_generator.go  # Random number utilities
│   │   ├── road.go              # Road segment logic
│   │   ├── routing.go           # Pathfinding algorithms
│   │   ├── runner.go            # Simulation runner
│   │   ├── simulation.go        # Main simulation engine
│   │   └── vehicle.go           # Vehicle agent
│   └── ui/
│       └── server.go            # Web UI server
├── web/
│   └── static/
│       ├── index.html           # Main web interface
│       └── canvas.html          # Canvas-only view
├── go.mod                       # Go module definition
├── go.sum                       # Dependency checksums
└── install.sh                   # Installation script
```

## Core Components

### 1. Graph System (`internal/graph/`)

| Component | Purpose | Key Types |
|-----------|---------|-----------|
| `Node` | Intersection representation | ID, X/Y coordinates, Type |
| `Edge` | Road segment | From/To nodes, Road type |
| `Network` | Complete road network | Nodes[], Edges[] |
| `POI` | Point of Interest | X/Y, Type (residential/commercial) |

### 2. Simulation Engine (`internal/simulation/`)

| Component | Purpose | Features |
|-----------|---------|----------|
| `Vehicle` | Traffic agent | Position, speed, routing, destination |
| `Road` | Road physics | Speed limits, lanes, capacity |
| `Intersection` | Traffic control | Signals, turning rules |
| `Routing` | Pathfinding | A* algorithm, zone preferences |
| `Runner` | Simulation loop | Time stepping, updates |

### 3. Rendering System (`internal/render/`)

| Component | Purpose | Output |
|-----------|---------|--------|
| `MapRenderer` | Static map rendering | PNG images |
| `AnimationRenderer` | Traffic animation | GIF/WebM |
| `Visualization` | Real-time display | WebSocket frames |

### 4. Canvas Interface (`internal/canvas/`)

| Component | Purpose | Protocol |
|-----------|---------|----------|
| `CanvasInterface` | Drawing abstraction | Interface |
| `CanvasServer` | WebSocket server | JSON messages |
| `Tools` | Drawing utilities | 2D primitives |

### 5. ML Components (`internal/ml/`)

| Component | Purpose | Input/Output |
|-----------|---------|--------------|
| `GraphGenerator` | Network topology | Parameters → Graph |
| `ImageProcessor` | Canvas operations | Canvas → Processed |
| `ImageEnhancer` | Quality improvement | Image → Enhanced |

## Network Layouts

### Grid Layout
```
┌───┬───┬───┬───┐
│   │   │   │   │
├───┼───┼───┼───┤
│   │   │   │   │
├───┼───┼───┼───┤
│   │   │   │   │
└───┴───┴───┴───┘
```
- Manhattan-style streets
- Regular intersections
- Predictable routing

### Radial Layout
```
      ◯
     /|\
    ◯─◯─◯
     \|/
      ◯
```
- Ring roads + spokes
- Natural highway flow
- City center focus

### Organic Layout
- Simulates natural growth
- Irregular patterns
- Realistic city evolution

### Kush Layout
```
    [Res1]    [Res2]
       \      /
        ◯──◯    [Com]
       /      \  /
[Res3]──◯──◯──◯──[Ind]
         \   /
        [CBD]
```
- Multi-zone realistic city
- Downtown (CBD)
- Commercial zones
- Industrial zones
- Residential neighborhoods

## Road Types

| Type | Width | Color | Speed Limit | Lanes |
|------|-------|-------|-------------|-------|
| Highway | 12px | #353a40 | 0.015 | 3 |
| Major | 8px | #454a50 | 0.010 | 2 |
| Minor | 6px | #555a60 | 0.008 | 1 |
| Local | 4px | #656a70 | 0.005 | 1 |

## Intersection Types

| Type | Radius | Purpose |
|------|--------|---------|
| Major Intersection | 10px | High-traffic junction |
| Traffic Light | 8px | Controlled intersection |
| Standard | 6px | Normal junction |

## Vehicle Behavior

### Routing Algorithm
```
1. Select random origin POI
2. Select destination POI (different type)
3. Calculate path using A*
4. Follow edges sequentially
5. Update position based on road speed limit
6. At intersection, check next edge
```

### POI Types
| Type | Color | Icon | Purpose |
|------|-------|------|---------|
| Residential | #7ebab5 | 🏠 | Origin/Destination |
| Commercial | #f6f5f5 | 🏢 | Destination/Origin |

## API Endpoints

The web server provides:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI (index.html) |
| `/canvas` | GET | Canvas-only view |
| `/ws` | WebSocket | Real-time simulation data |

## WebSocket Protocol

### Client → Server Messages
```json
{"action": "start"}
{"action": "stop"}
{"action": "reset"}
{"action": "add_vehicles", "count": 10}
{"action": "generate", "layout": "grid"}
```

### Server → Client Messages
```json
{"type": "state", "vehicles": [...], "stats": {...}}
{"type": "network", "nodes": [...], "edges": [...]}
{"type": "pois", "pois": [...]}
```

## Configuration

### Environment Variables
```bash
NETWEAVE_PORT=8080          # Server port
NETWEAVE_STATIC=./web/static # Static files path
NETWEAVE_DEBUG=true         # Debug mode
```

### Simulation Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| Simulation Speed | 10 | 10-200 | Steps per second |
| Vehicle Count | 0 | 0-1000 | Active vehicles |
| Layout | grid | see layouts | Network type |

## Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Frame Rate | 30 FPS | Canvas rendering |
| Vehicle Updates | 1000/s | Simulation speed |
| Network Generation | < 2s | For 50 nodes |
| Memory Usage | < 100MB | Typical simulation |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| gorilla/websocket | v1.5.3 | WebSocket server |
| llgcode/draw2d | latest | 2D drawing |
| golang/freetype | latest | Font rendering |
| x/image | v0.18.0 | Image processing |

## Development

### Building
```bash
# Build binary
go build -o netweave cmd/netweave/main.go

# Run tests
go test ./...
```

### Project Layout
Follows standard Go project layout:
- `cmd/` - Application entry points
- `internal/` - Private application code
- `web/` - Static web assets

## Roadmap

| Feature | Status | Priority |
|---------|--------|----------|
| Grid layout | ✅ Complete | High |
| Radial layout | ✅ Complete | High |
| Vehicle simulation | ✅ Complete | High |
| A* routing | ✅ Complete | High |
| Kush layout | ✅ Complete | Medium |
| Traffic lights | ✅ Complete | Medium |
| POI system | ✅ Complete | Medium |
| Export to image | 🔄 Planned | Low |
| Save/load networks | 🔄 Planned | Medium |
| Multi-threading | 📅 Planned | Low |
| 3D visualization | 📅 Future | Low |

## License

MIT License

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am "Add feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

## Acknowledgments

- Go drawing libraries by llgcode
- WebSocket implementation by Gorilla
- Inspired by urban planning research

## License

MIT — see [LICENSE](./LICENSE).
