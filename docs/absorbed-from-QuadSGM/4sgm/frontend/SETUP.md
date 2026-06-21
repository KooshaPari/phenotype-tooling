# Frontend Setup Guide - 4SGM Chatbot

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy the example env file
cp .env.example .env.local

# Edit .env.local and set:
BACKEND_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Architecture

### Components
- **ChatWidget** (`components/chat-widget.tsx`) - Main chat interface
- **Page** (`app/page.tsx`) - Homepage with product showcase

### API Route
- **Chat Proxy** (`app/api/chat/route.ts`) - Forwards requests to Python backend at `/chat` endpoint

## How It Works

1. User types message in chat widget
2. Frontend sends message to `/api/chat` route
3. Route transforms message and forwards to backend at `http://localhost:8000/chat`
4. Backend returns RAG response with citations and confidence score
5. Frontend displays response with:
   - Main message content
   - Source citations (if available)
   - Confidence indicator
   - Escalation warning (if confidence < 0.6)

## Configuration

### Backend Connection
The frontend connects to the backend via the `/api/chat` route, which proxies to the backend API. Ensure the backend is running before using the chat widget.

**Default backend URL**: `http://localhost:8000`

To change this, update `BACKEND_URL` in `.env.local`

## Features

### Chat Widget
- Collapsible chat interface (bottom-right corner)
- Quick suggestion buttons for common questions
- Message history
- Loading indicators
- Error handling with fallback messages
- Source citations from knowledge base
- Confidence scoring with visual indicators
- Escalation detection for uncertain responses

### Quick Suggestions
1. **Shipping Policies** - Information about shipping zones and timelines
2. **Returns & Refunds** - Return policy and refund procedures
3. **Payment Methods** - Accepted payment options

## Development

### Build
```bash
npm run build
```

### Type Check
```bash
npm run type-check
```

### Lint
```bash
npm run lint
```

### Test
```bash
npm run test          # Unit tests
npm run test:e2e      # E2E tests
```

## Troubleshooting

### Chat not connecting
1. Check backend is running: `http://localhost:8000/health`
2. Verify `BACKEND_URL` in `.env.local`
3. Check browser console for error messages

### Messages not sending
1. Ensure backend API is accessible
2. Check network tab in developer tools
3. Verify message content is not empty

### Styling issues
1. Run `npm run build` to ensure Tailwind classes are generated
2. Clear `.next` cache: `rm -rf .next`
3. Restart dev server

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Backend API URL |

## Production Deployment

1. Build the application: `npm run build`
2. Deploy to Vercel or similar platform
3. Set `BACKEND_URL` environment variable to production backend URL
4. Ensure CORS is properly configured on backend

## Notes

- The frontend uses Next.js 15 with TypeScript
- Styling uses Tailwind CSS + shadcn/ui components
- Chat state is managed with React hooks (no external state management needed)
- API calls are handled through the Next.js API route for better security
