# LangGraph Learnings

A hands-on collection of [LangGraph](https://langchain-ai.github.io/langgraph/) workflow patterns, plus a full **persistent chatbot** app built with Streamlit + LangGraph + SQLite.

## Contents

### 📓 Workflow notebooks
Each notebook demonstrates a core LangGraph graph pattern:

| Notebook | Pattern |
|---|---|
| [`langgraph-sequential-workflows.ipynb`](langgraph-sequential-workflows.ipynb) | Linear graph — nodes run one after another |
| [`langgraph-conditional-workflows.ipynb`](langgraph-conditional-workflows.ipynb) | Conditional edges — route based on state |
| [`langgraph-parallel-worflows.ipynb`](langgraph-parallel-worflows.ipynb) | Fan-out / fan-in — nodes run in parallel |
| [`langgraph-iterative-workflow.ipynb`](langgraph-iterative-workflow.ipynb) | Loops — generate → evaluate → optimize until a condition is met |

### 💬 Chatbot app (`chatbot/`)
A multi-conversation chatbot with persistent history and ChatGPT-style chat titles.

```
chatbot/
├── backend/
│   └── langgraph_backend.py   # LangGraph graph, SQLite checkpointer, thread/title storage
├── frontend/
│   └── frontend.py            # Streamlit UI (sidebar, streaming chat)
└── utils.py                   # thread-id generation, chat reset, LLM title generation
```

**Features**
- Streaming responses (token-by-token via `st.write_stream`)
- Persistent conversations — chat history survives restarts (SQLite checkpointer)
- Multiple conversations with a sidebar, each switchable
- Auto-generated meaningful titles per chat (stored in SQLite alongside the history)
- "New Chat" to start a fresh thread

**Architecture: two stores**

| Store | Where | Survives restart? | Role |
|---|---|---|---|
| `st.session_state` | RAM | ❌ | In-memory display cache (re-rendered each rerun) |
| SQLite (`chatbot.db`) | Disk | ✅ | Source of truth: messages (checkpointer) + `thread_titles` table |

On restart the UI starts blank; clicking a thread rehydrates `message_history` from the checkpointer via `chatbot.get_state(...)`.

## Setup

This project uses [uv](https://docs.astral.sh/uv/).

```bash
# install dependencies (creates .venv from pyproject.toml + uv.lock)
uv sync
```

Create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=sk-...
```

## Running

### Notebooks
Open any `.ipynb` in VS Code / Jupyter and select the `.venv` kernel, then **Restart Kernel → Run All**.

### Chatbot
Run from the `chatbot/` directory so the local `utils` and `backend` packages resolve:

```bash
cd chatbot
uv run streamlit run frontend/frontend.py
```

> **Note:** The SQLite database (`chatbot.db`) is created relative to where Streamlit is launched. If you delete it, also clear the in-memory session (restart) to keep threads and titles in sync.

## Requirements

- Python ≥ 3.12
- `langgraph`, `langchain`, `langchain-openai`, `langgraph-checkpoint-sqlite`, `streamlit`, `python-dotenv` (see [`pyproject.toml`](pyproject.toml))

## Tips learned the hard way

- **Module imports are case-sensitive:** `from langgraph.graph import StateGraph` (lowercase `graph`).
- **Annotate node params with your state schema** (e.g. `state: ChatState`), *not* `StateGraph` — LangGraph uses the annotation as the node's input schema.
- **The `add_messages` reducer expects a list:** return `{'messages': [response]}`, not a bare message or a nested list.
- **Streamlit caches imported modules:** after editing `backend/` or `utils.py`, fully restart the server (a "Rerun" isn't enough).
- **Generate the `thread_id` once per session** and store it in `st.session_state`, or you'll lose conversation memory on every rerun.
