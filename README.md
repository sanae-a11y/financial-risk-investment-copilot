# Financial Risk & Investment Copilot

Agentic AI portfolio decision-support platform built to demonstrate skills required for AI Engineer roles:

- LangGraph agentic workflow
- FastAPI backend
- Next.js + TypeScript frontend
- Yahoo Finance market data
- Structured outputs
- ESG-aware scoring
- Human-in-the-loop gate
- OpenRouter LLM summary with safe fallback

## Local run

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
FRONTEND_ORIGIN=*
```

Run:

```bash
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run:

```bash
npm run dev
```

Open: http://localhost:3000

## Disclaimer

Educational and research use only. Not financial advice.
