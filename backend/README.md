# LocalAI Leads Platform - Backend

## Database Setup

This backend uses **Neon PostgreSQL** as the database with **SQLAlchemy** ORM and **Alembic** for migrations.

### Prerequisites

1. Python 3.10+
2. Neon PostgreSQL account and database
3. Virtual environment (recommended)

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the `backend` directory:
```env
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech:5432/localai_leads?sslmode=require
```

### Database Schema

The database is designed in **Boyce-Codd Normal Form (BCNF)** with the following tables:

#### Core Tables
- **users**: Base authentication table for all user types
- **freelancers**: Freelancer-specific profile data
- **business_owners**: Business owner profile data
- **admins**: Admin/founder profile data
- **businesses**: Business entities for lead discovery

#### Lead Management
- **leads**: Lead tracking (alias/view of businesses)
- **lead_contacts**: Freelancer-business contact tracking
- **outreach_messages**: SMS/Email/WhatsApp outreach tracking

#### Demo & Deals
- **demo_websites**: Generated demo websites with analytics
- **deals**: Projects between freelancers and businesses
- **milestones**: Project milestones for payment tracking

#### Payments
- **payments**: Payment records with Razorpay integration
- **transactions**: Transaction audit trail

#### Communication
- **conversations**: Chat conversations between parties
- **messages**: Individual messages in conversations

#### Analytics
- **analytics_events**: Event tracking for platform metrics
- **freelancer_roi**: Freelancer ROI calculations
- **conversion_intelligence**: Data moat for conversion insights

### Running Migrations

1. Initialize Alembic (already done):
```bash
alembic init alembic
```

2. Run migrations:
```bash
alembic upgrade head
```

3. Create new migration (after model changes):
```bash
alembic revision --autogenerate -m "description of changes"
```

4. Rollback migration:
```bash
alembic downgrade -1
```

### Database Indexes

The schema includes comprehensive indexes for performance:

- **Business queries**: city, category, digital_score, status
- **Lead allocation**: exclusivity_expires_at, freelancer_id
- **Payment tracking**: deal_id, milestone_id, status
- **Analytics**: event_type, timestamp, user_id
- **Composite index**: businesses(city, category, digital_score, status)

### Foreign Key Constraints

All foreign keys have proper cascading rules:

- **CASCADE**: Delete related records (e.g., user deletion cascades to freelancer profile)
- **SET NULL**: Set to NULL on parent deletion (e.g., business_owner.business_id)
- **RESTRICT**: Prevent deletion if references exist (default for critical relationships)

### Referential Integrity

The database ensures:
1. No orphaned records (CASCADE deletes)
2. Consistent state transitions (status enums)
3. Proper relationship tracking (foreign keys)
4. Data consistency (CHECK constraints via enums)

### Testing

Run database tests:
```bash
pytest tests/unit/models/
pytest tests/integration/database/
```

### Schema Diagram

```
users (1) ─── (1) freelancers
              │
              └─── (N) lead_contacts ─── (1) businesses
              │
              └─── (N) deals ─── (N) milestones
                                 │
                                 └─── (N) payments

users (1) ─── (1) business_owners ─── (1) businesses
              │
              └─── (N) deals

businesses (1) ─── (N) demo_websites
           │
           └─── (N) lead_contacts
```

### Environment Variables

Required environment variables:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (for authentication)
- `RAZORPAY_KEY_ID`: Razorpay API key
- `RAZORPAY_KEY_SECRET`: Razorpay API secret

### Notes

- All monetary amounts are stored in **paise** (₹1 = 100 paise) as integers
- All timestamps use **timezone-aware** DateTime (UTC)
- JSON fields use PostgreSQL's native JSON type
- Enum types are created at the database level for type safety
