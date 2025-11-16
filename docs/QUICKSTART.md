# Quick Start Guide

Get GradeSchoolMathSolver-RAG up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11 or higher
- ✅ Docker and Docker Compose
- ✅ 8GB+ RAM available
- ✅ 10GB+ free disk space

Quick check:
```bash
python3 --version  # Should be 3.11+
docker --version   # Should be installed
docker-compose --version  # Should be installed
```

## Option 1: Automated Setup (Recommended)

### Step 1: Clone and Setup
```bash
git clone https://github.com/yangzq50/GradeSchoolMathSolver-RAG.git
cd GradeSchoolMathSolver-RAG
./start.sh
```

The script will:
- Create configuration files
- Start Docker services (Ollama + Elasticsearch)
- Download LLaMA 3.2 model
- Install Python dependencies
- Create default agents

### Step 2: Start the Application
```bash
source venv/bin/activate
python web_ui/app.py
```

### Step 3: Open Your Browser
Navigate to: http://localhost:5000

🎉 **You're done!** Start exploring the application.

## Option 2: Manual Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/yangzq50/GradeSchoolMathSolver-RAG.git
cd GradeSchoolMathSolver-RAG
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (default values work for local development)
```

### Step 4: Start Docker Services
```bash
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 5: Download AI Model
```bash
docker exec -it math-solver-ollama ollama pull llama3.2
```

This may take 5-10 minutes depending on your internet connection.

### Step 6: Initialize System
```bash
# Create default agents
python -c "
from services.agent_management import AgentManagementService
mgmt = AgentManagementService()
mgmt.create_default_agents()
print('Default agents created!')
"
```

### Step 7: Start Web Application
```bash
python web_ui/app.py
```

### Step 8: Access the Application
Open http://localhost:5000 in your browser.

## Option 3: Minimal Setup (No Docker)

If you can't use Docker, you can run with limited functionality:

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure for Local Mode
```bash
cp .env.example .env
# Edit .env and set:
# AI_MODEL_URL=http://localhost:11434
```

### Step 3: Install Ollama Locally
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download
```

### Step 4: Start Ollama
```bash
ollama serve
```

In another terminal:
```bash
ollama pull llama3.2
```

### Step 5: Run Application
```bash
python web_ui/app.py
```

**Note**: Without Elasticsearch, RAG features will be disabled.

## First Steps After Setup

### 1. Create a User
- Go to "Users" page
- Click "Add New User"
- Enter a username (e.g., "student1")

### 2. Take Your First Exam
- Click "Take Exam"
- Enter your username
- Select difficulty: "easy"
- Set question count: 5
- Answer the questions
- View your results!

### 3. Test a RAG Bot
- Go to "Agents" page
- Select "basic_agent"
- Click "Test Agent"
- Choose difficulty and question count
- Watch the agent solve problems!

### 4. Compare Agent Performance
Try testing different agents:
- **basic_agent**: Simple AI, no extras
- **classifier_agent**: Uses question categorization
- **rag_agent**: Uses RAG to learn from history
- **rag_correct_only**: Only learns from correct answers

## Verify Installation

Run the test suite:
```bash
python tests/test_basic.py
```

You should see:
```
✅ Passed: 6
❌ Failed: 0
📊 Total: 6
```

## Troubleshooting

### Docker Services Won't Start

Check if ports are already in use:
```bash
# Check port 11434 (Ollama)
lsof -i :11434

# Check port 9200 (Elasticsearch)
lsof -i :9200

# Check port 5000 (Web UI)
lsof -i :5000
```

Stop conflicting services or change ports in `docker-compose.yml`.

### AI Model Download Fails

If `ollama pull llama3.2` fails:
1. Check your internet connection
2. Try a smaller model: `ollama pull llama3.2:1b`
3. Check Ollama logs: `docker logs math-solver-ollama`

### Elasticsearch Won't Start

If you have less than 8GB RAM:
1. Edit `docker-compose.yml`
2. Reduce ES memory: `ES_JAVA_OPTS=-Xms256m -Xmx256m`
3. Restart: `docker-compose restart elasticsearch`

### Web UI Shows Errors

Check the console output for specific errors. Common issues:
- Database permissions: Ensure `data/` directory is writable
- Missing dependencies: Run `pip install -r requirements.txt`
- Config errors: Verify `.env` file exists and is valid

### Question Generation Is Slow

This is normal on first run. The AI model needs to warm up. Subsequent questions will be faster.

To speed up:
1. Use a smaller model: `llama3.2:1b`
2. Reduce question complexity
3. Enable GPU acceleration (if available)

## Configuration Tips

### Use GPU Acceleration

If you have an NVIDIA GPU:

Edit `docker-compose.yml`:
```yaml
ollama:
  image: ollama/ollama
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### Customize Question Difficulty

Edit `config.py` to adjust number ranges:
```python
# Make easy questions easier
def _generate_easy_equation(self):
    num1 = random.randint(1, 10)  # Was 1-20
    num2 = random.randint(1, 10)
    ...
```

### Change Web UI Port

In `.env`:
```bash
FLASK_PORT=8080  # Change from 5000
```

## Next Steps

Now that you're set up, explore:

1. **Create custom agents** - Configure your own RAG bot strategies
2. **Track progress** - Monitor user improvements over time
3. **Compare agents** - See which strategies work best
4. **Experiment** - Try different question types and difficulty levels

## Getting Help

- 📚 Read the [Architecture Documentation](docs/ARCHITECTURE.md)
- 🤖 Check [AI Model Service Guide](docs/AI_MODEL_SERVICE.md)
- 📖 Review the [README](README.md)
- 🐛 Report issues on GitHub
- 💡 Suggest features via GitHub Issues

## Updating the System

To update to the latest version:

```bash
git pull
pip install -r requirements.txt --upgrade
docker-compose pull
docker-compose up -d
```

## Stopping the System

To stop Docker services:
```bash
docker-compose down
```

To completely remove all data:
```bash
docker-compose down -v
rm -rf data/
```

## Performance Benchmarks

Typical performance on modern hardware:

| Operation | Time | Notes |
|-----------|------|-------|
| Generate 1 question | 1-3s | First request slower |
| Classify question | <0.1s | Rule-based |
| Agent solve (no RAG) | 2-5s | Depends on model |
| Agent solve (with RAG) | 3-7s | Includes search |
| Exam (5 questions) | 5-15s | For agent |
| Database query | <0.1s | SQLite local |
| RAG search | 0.1-0.5s | Elasticsearch |

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB
- OS: Linux, macOS, Windows

### Recommended
- CPU: 8 cores or GPU
- RAM: 16GB
- Disk: 20GB SSD
- OS: Linux or macOS

### Production
- CPU: 16+ cores or GPU
- RAM: 32GB+
- Disk: 100GB+ SSD
- Network: 1Gbps+

Happy Learning! 🎓📊🤖
