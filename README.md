# LocalAI Leads Platform

A marketplace connecting freelancers with local businesses that need digital services.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL database (Neon recommended)
- Razorpay account (for payments)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start backend server:
```bash
python run_production.py
```

Backend runs on: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with backend URL
```

4. Start development server:
```bash
npm start
```

Frontend runs on: http://localhost:3000

## 📚 Documentation

- Backend API: http://localhost:8000/docs
- Database Schema: See `backend/README.md`

## 🔑 Key Features

- Lead discovery from Google Places API
- AI-powered business intelligence (Ollama/ChatGPT)
- Milestone-based escrow payments
- Real-time notifications
- Analytics dashboard
- KYC verification
- Dispute resolution

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL (Neon)
- SQLAlchemy ORM
- Alembic migrations
- Razorpay payments

**Frontend:**
- React.js
- Zustand (state management)
- Axios (API calls)
- React Router

## 📦 Deployment

See deployment guides in `.kiro/` directory for platform-specific instructions.

## 🔒 Security

- JWT authentication
- Password hashing (bcrypt)
- Rate limiting
- CORS protection
- SQL injection prevention
- XSS protection

## 📄 License

Proprietary - All rights reserved
