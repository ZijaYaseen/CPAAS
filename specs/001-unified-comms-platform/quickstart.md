# Quick Start Guide: Unified Communication Platform

**Feature**: 001-unified-comms-platform
**Last Updated**: 2026-06-21

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker Desktop**: Latest version
- **Git**: Any recent version

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd CPAAS
git checkout 001-unified-comms-platform
```

### 2. Environment Configuration

Create `.env` file in repository root:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ucaas_dev
DATABASE_TEST_URL=postgresql://postgres:postgres@localhost:5432/ucaas_test

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
SESSION_SECRET=your-secret-key-change-in-production
SESSION_TTL_DAYS=7

# OpenAI (for AI agents)
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Channel Integrations (Optional for initial development)
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
SENDGRID_API_KEY=your-sendgrid-api-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Infrastructure (Docker Compose)

```bash
# Start PostgreSQL + Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps
```

**Docker Compose File** (`docker-compose.yml`):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ucaas_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI backend
uvicorn src.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API Docs: http://localhost:8000/docs (Swagger UI)

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js dev server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 6. Start Celery Workers (Optional for MVP)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Start worker
celery -A src.celery worker --loglevel=info --queues=default,ai,broadcast
```

**Worker Queues**:
- `default`: General background tasks
- `ai`: AI agent execution
- `broadcast`: Campaign message sending

### 7. Start Flower (Worker Monitoring - Optional)

```bash
celery -A src.celery flower --port=5555
```

Flower dashboard: http://localhost:5555

---

## Database Migrations

### Create New Migration

```bash
cd backend
alembic revision --autogenerate -m "Add tickets table"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1  # Rollback 1 migration
```

---

## Testing the Unified Inbox

### 1. Create Test User & Organization

```bash
# Using Python shell
cd backend
python

>>> from src.modules.auth.service import create_user
>>> from src.core.database import get_db
>>>
>>> # Create test organization and user
>>> user = create_user(
...     email="admin@test.com",
...     password="test123",
...     full_name="Test Admin",
...     organization_name="Test Org"
... )
>>> print(f"User ID: {user.id}, Tenant ID: {user.tenant_id}")
```

### 2. Login via Frontend

1. Navigate to http://localhost:3000
2. Click "Sign In"
3. Enter credentials: `admin@test.com` / `test123`
4. You should be redirected to the inbox

### 3. Connect a Test Channel

**Option A: WhatsApp Test (Requires WhatsApp Business API)**

1. Go to "Settings" → "Channels"
2. Click "Connect WhatsApp"
3. Enter Phone Number ID and Access Token (from Meta Developer Console)
4. Save

**Option B: Email Test (Using SMTP)**

1. Go to "Settings" → "Channels"
2. Click "Connect Email"
3. Enter SMTP credentials (e.g., Gmail App Password)
4. Save

**Option C: Web Chat Widget (Easiest for testing)**

1. Go to "Settings" → "Channels"
2. Click "Connect Web Chat"
3. Copy embed code
4. Paste into a test HTML file and open in browser
5. Send a test message

### 4. Send Test Message

**Via API** (using Swagger UI at http://localhost:8000/docs):

1. Navigate to `/inbox/messages/send` endpoint
2. Click "Try it out"
3. Enter JSON:
   ```json
   {
     "conversation_id": "<conversation-uuid>",
     "content": "Hello, this is a test message!"
   }
   ```
4. Execute request

**Via Frontend**:

1. Open inbox at http://localhost:3000/inbox
2. Select a conversation
3. Type message in composer
4. Press Enter or click Send

### 5. Verify Real-Time Updates

1. Open inbox in two browser windows
2. Send a message from one window
3. Verify it appears instantly in both windows (WebSocket working)

---

## Testing AI Agents (After Implementation)

### 1. Configure AI Agent

```bash
# Using Python shell
cd backend
python

>>> from src.modules.ai.service import configure_ai_agent
>>>
>>> configure_ai_agent(
...     tenant_id="<your-tenant-id>",
...     agent_type="support",
...     is_enabled=True,
...     system_prompt="You are a helpful customer support agent."
... )
```

### 2. Upload Knowledge Base Document

1. Go to "Settings" → "Knowledge Base"
2. Click "Upload Document"
3. Select a PDF or text file (e.g., product FAQ)
4. Wait for processing (chunking + embedding generation)

### 3. Send Test Message to Trigger AI

1. Create a new conversation (or use existing)
2. Send a message that matches knowledge base content
3. AI agent should auto-respond within 5 seconds
4. Check "AI Runs" in settings to view audit log

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

**Error**: `alembic.util.exc.CommandError: Can't locate revision identified by 'xyz'`

**Solution**:
```bash
# Reset database (development only!)
dropdb ucaas_dev
createdb ucaas_dev
alembic upgrade head
```

### Frontend Won't Start

**Error**: `Error: Cannot find module 'next'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket Not Working

**Symptom**: Real-time updates not appearing

**Solution**:
1. Check browser console for WebSocket errors
2. Verify backend WebSocket endpoint: `ws://localhost:8000/ws`
3. Ensure Redis is running: `docker-compose ps redis`
4. Check CORS configuration in `backend/src/main.py`

### Database Connection Failed

**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Verify connection
psql -h localhost -U postgres -d ucaas_dev
```

### Celery Worker Not Processing Tasks

**Symptom**: Tasks stay in "pending" state

**Solution**:
1. Check if worker is running: `ps aux | grep celery`
2. Check if Redis is accessible: `redis-cli ping`
3. Restart worker with verbose logging: `celery -A src.celery worker --loglevel=debug`
4. Check Flower dashboard for errors: http://localhost:5555

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/integration/test_inbox.py

# Run with coverage
pytest --cov=src tests/

# Run only unit tests
pytest tests/unit/
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

---

## Next Steps

1. **Implement Phase 1 (Foundation)**: Follow `tasks.md` for detailed task breakdown
2. **Set up CI/CD**: GitHub Actions for automated testing
3. **Deploy to Staging**: Use Docker Compose or Kubernetes
4. **Connect Real Channels**: WhatsApp Business API, Twilio, SendGrid

---

**Need Help?** Check the main documentation in `specs/001-unified-comms-platform/plan.md`
