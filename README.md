# DreamSight AI 🌙

AI-powered dream interpretation using LangChain, ChromaDB, and image generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Setup

1. **Clone and configure:**
   ```bash
   cd DreamSight_AI
   copy .env.example backend\.env
   # Edit backend\.env with your API keys
   ```

2. **Install dependencies:**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

3. **Start both servers:**
   ```bash
   # From project root
   start.bat    # Windows
   ./run.sh     # Unix/Mac
   ```

4. **Open the app:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for LLM interpretation |
| `HF_API_TOKEN` | ❌ | Hugging Face token for image generation |
| `HF_IMAGE_MODEL` | ❌ | HF model (default: FLUX.1-schnell) |

## 📁 Project Structure

```
DreamSight_AI/
├── backend/                 # FastAPI backend
│   ├── main.py             # Entry point
│   ├── config.py           # Settings (pydantic-settings)
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── models/             # Pydantic schemas
│   └── utils/              # ChromaDB loader
├── frontend/               # Next.js 14 frontend
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── lib/                # API client
│   └── types/              # TypeScript types
├── start.bat               # Windows startup script
├── run.sh                  # Unix startup script
└── dream_knowledge_db.zip  # Dream knowledge database
```

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/dreams/analyze` | Analyze dream with RAG + LLM |
| POST | `/api/dreams/interpret` | Simple dream interpretation |
| POST | `/api/dreams/search` | Search dream symbols |
| GET | `/api/dreams/symbols/common` | Get common symbols |
| GET | `/api/health` | Health check |

## 🎨 Features

- **Mystical UI**: Dark theme with glassmorphism and neon accents
- **RAG-powered**: ChromaDB vector search for context-aware interpretation
- **Dual Mode**: Psychological (Jungian) or Mystical analysis
- **Image Generation**: Surrealist Dalí-style dream visualization
- **Typewriter Effect**: Animated text reveal for interpretations

---

Built with ❤️ using FastAPI, LangChain, ChromaDB, Next.js 14, and Tailwind CSS
