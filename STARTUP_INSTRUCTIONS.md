# 🚀 Startup Instructions for Centralized Autonomous Agent Swarm

## 📋 **Prerequisites**

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Dependencies**: Install required packages (see requirements.txt)
3. **Node.js**: Required for MCP tools (Canvas, etc.)

## 🔧 **Setup Steps**

### 1. **Environment Setup**
```bash
# Navigate to the project directory
cd new/

# Install Python dependencies
pip install -r requirements.txt

# Source Node.js environment (for MCP tools)
source /Users/kooshapari/.zprofile
```

### 2. **Database Initialization**
The centralized agent manager will automatically create the SQLite database on first run.

### 3. **Launch the Centralized Swarm**
```bash
# Start the centralized autonomous agent swarm
python launch_centralized_autonomous_swarm.py
```

## 🎯 **What Happens During Startup**

### **Phase 1: Central Services**
1. **Central MCP Server** starts on port 3100
2. **Central Router** starts on port 3200 (if available)
3. **Unified Database** is initialized

### **Phase 2: Agent Creation**
1. **Alice-Centralized** (Project Manager) - Port 8006+
2. **Bob-Centralized** (Senior Developer) - Port 8007+
3. **Carol-Centralized** (UX Designer) - Port 8008+

### **Phase 3: Autonomous Communication**
1. Agents start autonomous message checking loops
2. Initial message sent from Alice to Bob
3. Autonomous responses generated based on agent roles

## 📊 **Monitoring the Swarm**

### **Console Output**
The startup script provides detailed logging:
- ✅ Agent creation status
- 🔍 Health check results
- 💬 Communication events
- 📋 Agent registry status

### **Agent Terminals**
Each agent runs in its own terminal window showing:
- Agent process output
- Autonomous message processing
- Tool execution logs

### **Health Monitoring**
The system performs periodic health checks every 30 seconds:
- Process status verification
- Heartbeat monitoring
- Automatic cleanup of dead processes

## 🛠️ **Key Features Demonstrated**

### **✅ Centralized Architecture**
- Single database for all agents
- Unified process management
- Central MCP server coordination

### **✅ Autonomous Communication**
- Agents respond automatically to messages
- Role-based response generation
- Cross-agent collaboration

### **✅ Process Management**
- Database records linked to running processes
- Health monitoring and cleanup
- Graceful shutdown handling

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Port Conflicts**
   - The system automatically finds available ports
   - Check for other services using ports 8006-8020

2. **Node.js Path Issues**
   - Ensure Node.js is in PATH: `source /Users/kooshapari/.zprofile`
   - Verify with: `node --version`

3. **Database Permissions**
   - Ensure write permissions in the project directory
   - Database file: `new/agents.db`

4. **Process Cleanup**
   - Use Ctrl+C to gracefully shutdown
   - Manual cleanup: `pkill -f "python.*agent"`

### **Verification Steps**

1. **Check Agent Status**
   ```python
   from src.services.centralized_agent_manager import centralized_agent_manager
   agents = centralized_agent_manager.list_agents()
   print(f"Active agents: {len(agents)}")
   ```

2. **Test Communication**
   ```python
   from src.services.agent_communication import send_message_to_agent
   await send_message_to_agent(
       sender_id="agent-alice",
       recipient_id="agent-bob",
       content="Test message"
   )
   ```

3. **Health Check**
   ```python
   health = await centralized_agent_manager.health_check("agent-alice")
   print(f"Alice health: {health['status']}")
   ```

## 🎉 **Success Indicators**

You'll know the system is working when you see:

1. **✅ All 3 agents created successfully**
2. **✅ Health checks show "healthy" status**
3. **✅ Autonomous message sent from Alice to Bob**
4. **✅ Agent terminals show autonomous responses**
5. **✅ Periodic health monitoring active**

## 🛑 **Shutdown**

To properly shutdown the swarm:

1. **Press Ctrl+C** in the main terminal
2. **Wait for cleanup** - agents will be terminated gracefully
3. **Verify cleanup** - all agent processes should stop

The system will automatically:
- Terminate all agent processes
- Update database status
- Clean up resources
- Display shutdown confirmation

## 📚 **Next Steps**

After successful startup, you can:

1. **Interact with agents** via MCP tools
2. **Send custom messages** between agents
3. **Monitor agent health** and performance
4. **Scale the swarm** by creating additional agents
5. **Implement custom workflows** using the centralized architecture

The centralized autonomous agent swarm is now ready for development and testing! 🎯
