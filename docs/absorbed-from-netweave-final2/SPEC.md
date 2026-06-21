# netweave-final2 Specification

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NetWeave System Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Web Client Layer                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │   Browser    │  │  HTML5       │  │   WebSocket          │   │   │
│  │  │   (UI)       │  │  Canvas      │  │   Client             │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  │         │                 │                    │                 │   │
│  │         └────────────────┼────────────────────┘                 │   │
│  │                          │                                      │   │
│  │  ┌───────────────────────┴─────────────────────────────────┐  │   │
│  │  │                    JavaScript Engine                       │  │   │
│  │  │  • Network rendering    • Vehicle animation               │  │   │
│  │  │  • Interaction handling • Stats display                   │  │   │
│  │  │  • A* pathfinding     • POI management                  │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ HTTP / WebSocket                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Server Layer (Go)                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │   HTTP       │  │  WebSocket   │  │   Static File        │   │   │
│  │  │   Server     │  │  Handler     │  │   Server             │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  │         │                 │                                      │   │
│  │         └─────────────────┴────────────────┐                     │   │
│  │                                            │                     │   │
│  │  ┌─────────────────────────────────────────┼─────────────────┐   │   │
│  │  │              UI Server (internal/ui)    │                 │   │   │
│  │  │  • Route handlers                       │                 │   │   │
│  │  │  • Message routing                      │                 │   │   │
│  │  │  • Connection management                │                 │   │   │
│  │  └─────────────────────────────────────────┘                 │   │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                    │                                   │
│           ┌────────────────────────┼────────────────────────┐          │
│           │                        │                        │          │
│           ▼                        ▼                        ▼          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐    │
│  │     Graph       │     │   Simulation    │     │     Canvas      │    │
│  │    System       │     │     Engine      │     │   Interface     │    │
│  │                 │     │                 │     │                 │    │
│  │  internal/graph │     │ internal/sim    │     │  internal/canvas│    │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘    │
│           │                        │                        │          │
│           │                        │                        │          │
│           ▼                        ▼                        ▼          │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐    │
│  │   Rendering   │     │       ML        │     │   Visualization │    │
│  │    System       │     │   Components    │     │                 │    │
│  │                 │     │                 │     │                 │    │
│  │ internal/render │     │  internal/ml    │     │  (Frontend)     │    │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Graph System (`internal/graph/`)

```
┌─────────────────────────────────────────────────────────┐
│                    Graph System                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     Node     │  │     Edge     │  │     POI      │  │
│  │              │  │              │  │              │  │
│  │ - ID         │  │ - From       │  │ - X/Y        │  │
│  │ - X, Y       │  │ - To         │  │ - Type       │  │
│  │ - Type       │  │ - Type       │  │ - Icon       │  │
│  │ - Zone       │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│           │                 │                 │         │
│           └─────────────────┴─────────────────┘         │
│                         │                               │
│                         ▼                               │
│              ┌─────────────────────┐                    │
│              │      Network        │                    │
│              │  - Nodes[]          │                    │
│              │  - Edges[]          │                    │
│              │  - Adjacency List   │                    │
│              │  - Methods:         │                    │
│              │    - Connect()      │                    │
│              │    - Pathfind()     │                    │
│              │    - Validate()     │                    │
│              └─────────────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Node Types**:
| Type | Purpose | Characteristics |
|------|---------|-----------------|
| `major_intersection` | Highway junctions | Radius 10, high capacity |
| `traffic_light` | Controlled intersections | Radius 8, signal phases |
| `intersection` | Standard junctions | Radius 6, yield rules |

**Edge Types**:
| Type | Speed | Use Case |
|------|-------|----------|
| `highway` | 0.015 | Long-distance, high volume |
| `major` | 0.010 | Arterial roads |
| `minor` | 0.008 | Collector roads |
| `local` | 0.005 | Residential streets |

### 2. Simulation Engine (`internal/simulation/`)

```
┌─────────────────────────────────────────────────────────┐
│                  Simulation Engine                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌────────┐  │
│  │   Vehicle    │◄───►│     Road     │◄───►│  Inter │  │
│  │   Agent      │     │   Segment    │     │ section│  │
│  │              │     │              │     │        │  │
│  │ - Position   │     │ - Speed Limit│     │ - Signal│  │
│  │ - Velocity   │     │ - Capacity   │     │ - Queue │  │
│  │ - Path[]     │     │ - Length     │     │ - Rules │  │
│  │ - State      │     │ - Lanes      │     │        │  │
│  └──────────────┘     └──────────────┘     └────────┘  │
│           │                   │                 │     │
│           └───────────────────┴─────────────────┘     │
│                         │                             │
│                         ▼                             │
│              ┌─────────────────────┐                  │
│              │   Cellular Automata   │                  │
│              │   Traffic Model       │                  │
│              │                       │                  │
│              │ - Update rules        │                  │
│              │ - Collision detect    │                  │
│              │ - Flow calculation    │                  │
│              └─────────────────────┘                  │
│                         │                             │
│                         ▼                             │
│              ┌─────────────────────┐                  │
│              │   Simulation Runner │                  │
│              │                     │                  │
│              │ - Time step loop    │                  │
│              │ - Event scheduling  │                  │
│              │ - State snapshots   │                  │
│              └─────────────────────┘                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Vehicle State Machine**:
```
┌─────────┐
│  IDLE   │
└────┬────┘
     │ spawn()
     ▼
┌─────────┐     ┌─────────┐
│ MOVING  │────►│ARRIVED  │
└────┬────┘     └─────────┘
     │
     │ edge end
     ▼
┌─────────┐
│ROUTING  │◄──► compute next edge
└────┬────┘
     │
     └────────────────┐
                      ▼
               ┌─────────┐
               │   POI   │ (destination reached)
               └─────────┘
```

### 3. Routing System (`internal/simulation/routing.go`)

**A* Algorithm Implementation**:
```
function AStar(start, goal, zonePreference):
    openSet = {start}
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, goal)}
    
    while openSet not empty:
        current = node in openSet with lowest fScore
        
        if current == goal:
            return reconstruct_path(cameFrom, current)
        
        openSet.remove(current)
        
        for neighbor in neighbors(current):
            tentative_g = gScore[current] + distance(current, neighbor)
            
            # Zone preference bonus/penalty
            if neighbor.zone == zonePreference:
                tentative_g *= 0.8  # Prefer this zone
            
            if tentative_g < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tentative_g
                fScore[neighbor] = tentative_g + heuristic(neighbor, goal)
                
                if neighbor not in openSet:
                    openSet.add(neighbor)
    
    return failure
```

### 4. Rendering System (`internal/render/`)

```
┌─────────────────────────────────────────────────────────┐
│                   Rendering Pipeline                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: Network + Vehicles + POIs                       │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Layer 1    │    │   Layer 2    │    │ Layer 3  │  │
│  │              │    │              │    │          │  │
│  │ Background   │───►│  Roads       │───►│ Vehicles │  │
│  │ - Parks      │    │  - Edges       │    │ - Cars   │  │
│  │ - Water      │    │  - Intersections│   │ - POIs   │  │
│  │ - Buildings  │    │              │    │          │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│                                                         │
│  Output: Canvas / PNG / GIF                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5. Canvas Interface (`internal/canvas/`)

**WebSocket Message Protocol**:

| Direction | Type | Payload | Purpose |
|-----------|------|---------|---------|
| C→S | `command` | `{action: "start"}` | Control simulation |
| C→S | `config` | `{layout: "grid"}` | Set parameters |
| S→C | `state` | `{vehicles, stats}` | Full state update |
| S→C | `delta` | `{vehicle_updates}` | Incremental update |
| S→C | `network` | `{nodes, edges}` | Network definition |

### 6. ML Components (`internal/ml/`)

**Graph Generation ML**:
```python
# Pseudocode for ML-assisted generation
input: zone_types, density, connectivity_target
output: optimized graph topology

1. Generate initial random layout
2. Evaluate metrics:
   - Average shortest path
   - Betweenness centrality
   - Flow capacity
3. Apply genetic algorithm / neural optimization
4. Return optimized node/edge placement
```

## Data Models

### Network JSON Schema
```json
{
  "nodes": [
    {
      "id": 0,
      "x": 400.5,
      "y": 300.2,
      "type": "major_intersection",
      "zone": "downtown"
    }
  ],
  "edges": [
    {
      "from": 0,
      "to": 1,
      "type": "highway"
    }
  ],
  "pois": [
    {
      "id": 0,
      "x": 450.0,
      "y": 350.0,
      "type": "residential",
      "nodeId": 5
    }
  ]
}
```

### Vehicle State
```go
type Vehicle struct {
    ID          int
    Type        string          // car, truck, bus
    X, Y        float64         // Current position
    Speed       float64         // Current speed
    MaxSpeed    float64         // Speed limit
    EdgeIndex   int             // Current road
    Position    float64         // 0.0 to 1.0 along edge
    Path        []int           // Future edge indices
    State       VehicleState    // IDLE, MOVING, ARRIVED
    StartPOI    int             // Origin POI
    DestPOI     int             // Destination POI
    History     []POIVisit      // Past stops
}
```

### Simulation Config
```go
type SimulationConfig struct {
    Speed           int     // Steps per second (10-200)
    LayoutType      string  // grid, radial, organic, random, kush
    NodeCount       int     // Number of intersections
    VehicleCount    int     // Initial vehicles
    RoadTypes       []RoadType
    ZoneDefinitions []Zone
}
```

## Layout Generation Algorithms

### Grid Layout Algorithm
```
procedure generateGrid(nodeCount):
    gridSize = ceil(sqrt(nodeCount))
    cellWidth = canvas.width / gridSize
    cellHeight = canvas.height / gridSize
    
    for row in 0..gridSize:
        for col in 0..gridSize:
            x = col * cellWidth + jitter()
            y = row * cellHeight + jitter()
            node = createNode(x, y, determineType(row, col))
            addNode(node)
    
    # Connect horizontal
    for row in 0..gridSize:
        for col in 0..gridSize-1:
            connect(node[row][col], node[row][col+1])
    
    # Connect vertical
    for row in 0..gridSize-1:
        for col in 0..gridSize:
            connect(node[row][col], node[row+1][col])
```

### Radial Layout Algorithm
```
procedure generateRadial(nodeCount):
    center = (canvas.width/2, canvas.height/2)
    addNode(center, "major_intersection")
    
    rings = 3
    nodesPerRing = (nodeCount - 1) / rings
    numSpokes = 8
    
    for spoke in 0..numSpokes:
        angle = 2π * spoke / numSpokes
        
        for ring in 1..rings:
            radius = minDimension * ring / (rings + 0.5)
            x = center.x + radius * cos(angle)
            y = center.y + radius * sin(angle)
            
            addNode(x, y, determineType(ring, spoke))
            connectToPreviousRing()
        
        # Connect ring segments
        for ring in 1..rings:
            connectRingNodes(ring)
```

### Kush Layout (Multi-Zone City)
```
procedure generateKush(nodeCount):
    center = (canvas.width/2, canvas.height/2)
    
    # Define zones
    zones = {
        downtown: {x: center.x, y: center.y, radius: r*0.15},
        commercial: {x: cx, y: cy, radius: r*0.2},
        industrial: {x: ix, y: iy, radius: r*0.2},
        residential1-3: {...}
    }
    
    # Generate downtown grid
    generateDowntownGrid(zones.downtown)
    
    # Generate ring road or highway
    if random() < 0.5:
        generateRingRoad()
    else:
        generateHighwaySpokes()
    
    # Generate commercial zone
    generateCommercialGrid(zones.commercial)
    
    # Generate industrial zone
    generateIndustrialGrid(zones.industrial)
    
    # Generate residential zones
    for each residential zone:
        generateArterialNetwork(zone)
        connectToHighway(zone)
    
    # Connect zones
    connectZoneCenters()
    
    ensureConnectivity()
```

## Performance Specifications

| Component | Metric | Target |
|-----------|--------|--------|
| Network Generation | Time | < 2s for 100 nodes |
| Pathfinding | A* | < 1ms per query |
| Simulation Step | Update | < 16ms (60 FPS) |
| WebSocket | Latency | < 50ms |
| Canvas Render | FPS | 30+ |
| Memory | Per vehicle | < 1KB |

## Scaling Limits

| Resource | Soft Limit | Hard Limit |
|----------|------------|------------|
| Nodes | 200 | 1000 |
| Edges | 500 | 2000 |
| Vehicles | 500 | 2000 |
| POIs | 100 | 500 |
| Simultaneous clients | 10 | 100 |

## Error Handling

| Error Case | Handling |
|------------|----------|
| Disconnected node | DFS connectivity check + auto-repair |
| Vehicle stuck | Timeout detection + rerouting |
| Division by zero | Guard clauses in distance calc |
| Invalid edge index | Bounds checking + skip |
| WebSocket disconnect | Cleanup + allow reconnect |

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Resource exhaustion | Rate limiting on vehicle spawn |
| File traversal | Path validation for static files |
| DoS | Connection timeouts + max clients |
| XSS | Output encoding in JSON |
