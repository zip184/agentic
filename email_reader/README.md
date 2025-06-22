# Autonomous Agent Starter with ChromaDB Memory

A powerful autonomous agent framework with persistent vector-based memory using ChromaDB.

## Features

- 🤖 **Autonomous Agent**: Basic agent with goal-oriented decision making
- 🧠 **Memory System**: Persistent vector-based memory using ChromaDB
- 🔍 **Semantic Search**: Find relevant memories using embeddings
- 📊 **Memory Types**: Support for observations, actions, goals, reflections, and learnings
- 🌐 **REST API**: Full API for interacting with the agent and memory system
- 📈 **Memory Analytics**: Statistics and insights about stored memories

## Memory System Overview

The memory system uses ChromaDB to store vector embeddings of memories, enabling semantic search and retrieval. Each memory entry includes:

- **Content**: The actual memory text
- **Type**: Classification (observation, action, goal, reflection, learning, context)
- **Importance Score**: How important this memory is (0-1)
- **Metadata**: Additional contextual information
- **Timestamp**: When the memory was created
- **Embedding**: Vector representation for semantic search

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- An OpenAI API key

### Installation and Running the Application

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd autonomous_agent_starter
    ```

2.  **Set up your environment:**
    Create a `.env` file in the project root and add your OpenAI API key:

    ```
    OPENAI_API_KEY="your_openai_api_key"
    ```

3.  **Run with Docker Compose:**
    This is the recommended way to run the application. It starts the FastAPI application and a ChromaDB instance in separate containers.

    ```bash
    docker-compose up --build
    ```

    The application will be available at `http://localhost:8000`.

## Usage

### Basic Agent (No Memory)

```python
from agents.agent import run_agent

result = run_agent("Your goal here")
print(result)
```

### Memory-Aware Agent

```python
from agents.memory_agent import MemoryAwareAgent

# Initialize the agent
agent = MemoryAwareAgent()

# Run with memory-enhanced decision making
response = agent.run_agent(
    goal="Design a user interface",
    current_context="For elderly users",
    memory_search_limit=5
)
```

### Adding Memories

```python
# Add different types of memories
agent.add_observation("Users prefer simple interfaces", importance_score=0.8)
agent.add_learning("Breaking tasks into steps improves success", importance_score=0.9)
agent.add_reflection("Always consider user perspective", importance_score=0.7)

# Add with metadata
agent.add_observation(
    "Database queries are slow without indexes",
    importance_score=0.9,
    metadata={"domain": "performance", "source": "monitoring"}
)
```

### Searching Memories

```python
# Search for relevant memories
memories = agent.search_memories("performance optimization", limit=5)

# Get memories by type
learnings = agent.get_memories_by_type(MemoryType.LEARNING, limit=10)

# Get memory statistics
stats = agent.get_memory_stats()
```

## API Endpoints

The API documentation is available at `http://localhost:8000/docs` when the application is running.

- `POST /run-agent`: Run the basic agent with a goal.
- `POST /run-with-memory`: Run the memory-aware agent.
- `POST /memory/add`: Add a memory to the database.
- `POST /memory/search`: Search for memories.
- `GET /memory/stats`: Get statistics about the memory database.
- `POST /memory/clear`: Clear all memories from the database.

## Development Workflow

This project uses `make` to simplify Docker Compose commands. For a list of all available commands, run:

```bash
make help
```

### Primary Commands

| Action           | Command        | Description                                       |
| ---------------- | -------------- | ------------------------------------------------- |
| **Start**        | `make up`      | Starts all services in the background.            |
| **Stop**         | `make down`    | Stops all services and removes containers.        |
| **Rebuild**      | `make rebuild` | Rebuilds the app image and restarts all services. |
| **View Logs**    | `make logs`    | Follows the logs for the `app` service.           |
| **Check Status** | `make status`  | Shows the status of the running services.         |

### Raw `docker-compose` commands

If you prefer not to use `make`, you can use the standard `docker-compose` commands.

#### Command Quick Reference

| Action           | Command                      | Description                                   |
| ---------------- | ---------------------------- | --------------------------------------------- |
| **Start**        | `docker-compose up -d`       | Starts services in the background.            |
| **Stop**         | `docker-compose down`        | Stops and removes containers, networks.       |
| **View Logs**    | `docker-compose logs -f app` | Follows the logs for the `app` service.       |
| **Check Status** | `docker-compose ps`          | Lists the running containers for the project. |

## Memory Types

- **observation**: Things the agent has observed
- **action**: Actions the agent has taken
- **goal**: Goals the agent has pursued
- **reflection**: Agent's reflections and insights
- **learning**: Lessons learned from experiences
- **context**: Contextual information

## Configuration

The memory system can be configured by modifying the `ChromaMemoryManager` initialization:

```python
from memory import ChromaMemoryManager

# Custom configuration
memory_manager = ChromaMemoryManager(
    persist_directory="./custom_chroma_db",
    collection_name="my_agent_memories"
)
```

## File Structure

```
autonomous_agent_starter/
├── agents/
│   ├── agent.py              # Basic agent
│   └── memory_agent.py       # Memory-aware agent
├── memory/
│   ├── __init__.py           # Package initialization
│   ├── memory_types.py       # Memory type definitions
│   └── chroma_memory.py      # ChromaDB memory manager
├── app/
│   └── main.py               # FastAPI application
├── examples/
│   └── memory_example.py     # Usage examples
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Dependencies

- `chromadb` - Vector database for memory storage
- `langchain-openai` - OpenAI integration
- `fastapi` - Web API framework
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License
