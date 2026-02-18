# AI Tactician — Prototype

A standalone web app demonstrating the AI Tactician's core intelligence loop:

**User enters marketing intent → Tactician gathers account context → Segments audience by value → Generates cohort-differentiated strategy → Creates draft campaign + automation specs**

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env with your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Start the server
python main.py
# → Runs on http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → Runs on http://localhost:5173
```

### 3. Try it

Open `http://localhost:5173` and type a marketing intent:

| Prompt | What happens |
|--------|-------------|
| "Launch a campaign for our new wireless earbuds" | Full flow: context → segmentation → 3-cohort strategy with campaign+automation combos |
| "How did my campaigns do last month?" | Performance Q&A with metrics |
| "Set up a win-back automation for inactive customers" | Automation-focused flow |
| "Send a flash sale — 30% off everything for 24 hours" | Urgent campaign strategy |

## Architecture

```
React Frontend (Vite + Tailwind)
  ↓ useChat() via Vercel AI SDK
FastAPI Backend
  ↓ Claude API (claude-sonnet-4-5-20250929)
Mock API Layer (JSON data → swappable for real Brevo APIs)
```

### Three-Panel Layout
- **Left**: Brief navigation (conversation switching)
- **Center**: Chat with inline strategy blocks, campaign/automation cards
- **Right**: Account context view + artifact detail views (campaign, automation, segment)

## Project Structure

```
tactician-prototype/
├── backend/
│   ├── main.py              # FastAPI app + streaming endpoint
│   ├── agent.py             # Claude agent with tool-calling loop
│   ├── tools.py             # Tool definitions + dispatch
│   ├── mock_api.py          # Mock data layer
│   ├── models.py            # Pydantic models
│   ├── mock_data/           # JSON fixtures
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # 3-panel layout
│   │   ├── components/
│   │   │   ├── chat/        # TacticianChat
│   │   │   ├── layout/      # NavPanel, DetailPanel, ContextView
│   │   │   └── artifacts/   # Strategy/Campaign/Automation cards + details
│   │   ├── hooks/           # useDetailPanel, useBriefs
│   │   └── lib/             # message-parser
│   └── package.json
├── .env.example
└── README.md
```

## Key Features

- **Cohort-differentiated strategies**: High-value → premium multi-channel + automation; Standard → cost-efficient email-only
- **Campaign + Automation combos**: Agent creates both campaigns and automations for higher-value cohorts where ROI justifies it
- **Streaming responses**: Real-time streamed text with inline strategy blocks
- **Artifact system**: Clickable cards in chat → full detail views in right panel
- **Approval flow**: Approve/Adjust buttons → agent creates drafts
- **Brief management**: Multiple conversations, switch between them

## Mock Data

The mock layer simulates a fictional e-commerce account ("TechGear Store") with:
- 48,500 email contacts, 12,300 SMS, 8,900 WhatsApp
- Shopify integration, professional plan
- Recent campaign history with performance data
- Pre-computed segmentation (high/mid/standard value tiers)
