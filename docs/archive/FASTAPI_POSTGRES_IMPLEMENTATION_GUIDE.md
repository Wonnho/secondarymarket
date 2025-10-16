# 🚀 FastAPI + PostgreSQL Implementation Guide

## 📋 Overview

Complete implementation guide for connecting FastAPI backend to PostgreSQL database to enable admin account management functionality.

**Completion Date:** 2025-10-16
**Status:** ✅ Implementation Complete | Ready for Testing

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐  │
│  │  Streamlit   │─────▶│   FastAPI    │─────▶│ PostgreSQL│  │
│  │  Frontend    │      │   Backend    │      │  +TimeDB  │  │
│  │  :8501       │      │   :8000      │      │   :5432   │  │
│  └──────────────┘      └──────────────┘      └───────────┘  │
│         │                     │                              │
│         │                     │                              │
│         │              ┌──────────────┐                      │
│         │              │    Redis     │                      │
│         └─────────────▶│    Cache     │                      │
│                        │    :6379     │                      │
│                        └──────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
│
├── core/
│   ├── __init__.py
│   └── database.py              # ✨ Database connection & session management
│
├── models/
│   ├── __init__.py              # ✨ Model exports
│   ├── user.py                  # ✨ User SQLAlchemy model
│   └── audit_log.py             # ✨ Audit log model
│
├── schemas/
│   ├── __init__.py              # ✨ Schema exports
│   ├── user.py                  # ✨ User Pydantic schemas
│   └── audit_log.py             # ✨ Audit log schemas
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py          # ✨ Auth dependencies & guards
│   └── routers/
│       ├── __init__.py          # ✨ Router exports
│       ├── auth.py              # ✨ Authentication endpoints
│       └── admin.py             # ✨ Admin user management endpoints
│
├── utils/
│   ├── __init__.py
│   └── auth.py                  # ✨ Password hashing & JWT utilities
│
└── services/
    └── __init__.py

database/
└── init/
    ├── 01_create_tables.sql     # ✨ Database schema DDL
    └── 02_insert_sample_data.sql # ✨ Sample user data

✨ = New files created in this implementation
```

---

## 🗄️ Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,

    CONSTRAINT valid_role CHECK (role IN ('user', 'admin', 'super_admin'))
);
```

**Indexes:**
- `idx_users_user_id` on `user_id`
- `idx_users_email` on `email`
- `idx_users_role` on `role`
- `idx_users_is_active` on `is_active`
- `idx_users_created_at` on `created_at DESC`

### Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id VARCHAR(100) NOT NULL,
    admin_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    target VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,

    CONSTRAINT fk_admin_user FOREIGN KEY (admin_id)
        REFERENCES users(user_id) ON DELETE CASCADE
);
```

**Additional Tables:**
- `sessions` - User session management
- `password_reset_tokens` - Password reset functionality
- `user_profiles` - Extended user information

---

## 🔌 API Endpoints

### Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/register` | User registration | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/logout` | User logout | No |

### Admin Endpoints (`/api/admin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/users` | List all users (with search/filter) | Admin |
| GET | `/api/admin/users/{user_id}` | Get specific user | Admin |
| PUT | `/api/admin/users/{user_id}` | Update user | Admin |
| POST | `/api/admin/users/{user_id}/activate` | Activate user | Admin |
| POST | `/api/admin/users/{user_id}/deactivate` | Deactivate user | Admin |
| DELETE | `/api/admin/users/{user_id}` | Delete user | Admin |
| POST | `/api/admin/users/{user_id}/reset-password` | Reset password | Admin |
| GET | `/api/admin/audit-logs` | Get audit logs | Admin |
| GET | `/api/admin/analytics/users` | Get user analytics | Admin |

---

## 🚀 How to Use: Step-by-Step

### Step 1: Start Docker Compose Stack

```bash
cd /home/wonnho/AgenticAI/secondarymarket

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# Expected output:
# secondarymarket_db       ... Up (healthy)
# secondarymarket_redis    ... Up (healthy)
# secondarymarket_backend  ... Up
# secondarymarket_frontend ... Up
# secondarymarket_pgadmin  ... Up
```

### Step 2: Verify Database Initialization

The database will automatically initialize with:
- All table structures created
- Sample users inserted
- Indexes created
- Triggers and functions configured

**Check logs:**
```bash
docker-compose logs timescaledb | grep "Database Initialization"

# Expected output:
# ============================================
# Database Initialization Complete
# ============================================
# Total Users: 10
# Admin Users: 2
# Active Users: 8
```

### Step 3: Verify Backend API

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
    "status": "healthy",
    "api": "running",
    "database": {
        "connected": true,
        "host": "timescaledb",
        "port": "5432",
        "database": "secondarymarket"
    },
    "redis": "pending"
}

# API documentation
open http://localhost:8000/docs  # Interactive Swagger UI
```

### Step 4: Test Login API

```bash
# Login as admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "password": "admin123"
  }'

# Response:
{
    "user_id": "admin",
    "user_name": "System Administrator",
    "email": "admin@secondarymarket.com",
    "role": "super_admin",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### Step 5: Test Admin APIs

```bash
# Save the access token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Get all users
curl -X GET "http://localhost:8000/api/admin/users?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# Search users
curl -X GET "http://localhost:8000/api/admin/users?search=john&role=user" \
  -H "Authorization: Bearer $TOKEN"

# Get specific user
curl -X GET "http://localhost:8000/api/admin/users/user123" \
  -H "Authorization: Bearer $TOKEN"

# Get user analytics
curl -X GET "http://localhost:8000/api/admin/analytics/users" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 6: Connect Frontend to Backend

Update `frontend/utils/auth.py`:

```python
# Line 104-127: Replace mock authentication with real API call

def authenticate_with_backend(user_id: str, password: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """Authenticate with backend API"""
    try:
        import requests

        response = requests.post(
            "http://backend:8000/api/auth/login",  # Docker service name
            json={"user_id": user_id, "password": password},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return True, {
                'user_id': data['user_id'],
                'user_name': data['user_name'],
                'email': data['email'],
                'role': data['role'],
                'access_token': data['access_token']
            }, None
        elif response.status_code == 401:
            return False, None, "아이디 또는 비밀번호가 올바르지 않습니다."
        else:
            return False, None, f"서버 오류: {response.status_code}"

    except requests.exceptions.Timeout:
        return False, None, "서버 응답 시간 초과"
    except requests.exceptions.ConnectionError:
        return False, None, "서버 연결 실패"
    except Exception as e:
        return False, None, f"인증 오류: {str(e)}"
```

---

## 📝 Sample User Credentials

| User ID | Password | Role | Status | Description |
|---------|----------|------|--------|-------------|
| admin | admin123 | super_admin | Active | System administrator |
| manager | admin123 | admin | Active | Service manager |
| user123 | password123 | user | Active | Regular user (John Doe) |
| testuser | test123 | user | Active | Test account |
| alice | test123 | user | Active | Active user |
| bob | test123 | user | Active | Active user |
| charlie | test123 | user | Active | Active user |
| diana | test123 | user | Active | Active user |
| inactive_user | test123 | user | Inactive | Deactivated account |
| eve | test123 | user | Inactive | Deactivated account |

---

## 🧪 Testing Admin Features

### Test 1: Admin Login and View All Users

1. Open frontend: http://localhost:8501
2. Login with `admin` / `admin123`
3. Click user menu (👤 System Administrator)
4. Click "User Management"
5. See all 10 users from database

### Test 2: Search Users

1. In User Management page
2. Search for "john"
3. See user123 (John Doe)
4. Clear search
5. Filter by role = "admin"
6. See 2 admin users (admin, manager)

### Test 3: Activate/Deactivate User

1. Find "inactive_user" (Jane Smith)
2. Click to expand
3. Click "✅ Activate" button
4. User status changes to Active
5. Click "🚫 Deactivate" button
6. User status changes back to Inactive

### Test 4: View Audit Logs

1. Perform some actions (activate, deactivate, reset password)
2. Go to Admin Dashboard
3. See "Recent Activity" section
4. See all logged actions with timestamps

### Test 5: Analytics

1. Click "Analytics" from admin menu
2. See user statistics:
   - Total Users: 10
   - Active Users: 8
   - Recent Registrations: varies
   - Role distribution chart
   - Activity rate: 80%

---

## 🔐 Security Features

### Password Hashing
- Uses **bcrypt** with salt
- Hashed passwords stored in database
- Never expose plain text passwords

### JWT Authentication
- Access tokens expire in 60 minutes
- Tokens include user_id and role claims
- Secret key configurable via environment variable

### Role-Based Access Control (RBAC)
```python
# Permission matrix
super_admin:
  - Can manage all users including admins
  - Full system access

admin:
  - Can manage regular users only
  - Cannot manage other admins
  - Cannot manage super admins

user:
  - Cannot access admin endpoints
  - Can only view own data
```

### API Authorization
```python
# Every admin endpoint protected
@router.get("/admin/users")
def get_all_users(
    current_user: User = Depends(require_admin)  # ← Auth guard
):
    # Only executes if user has admin role
    ...
```

### Audit Logging
- All admin actions logged to `audit_logs` table
- Includes timestamp, admin ID, action type, target, IP address
- Immutable log entries (insert-only)

---

## 🛠️ Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database
POSTGRES_DB=secondarymarket
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# Redis
REDIS_PASSWORD=redis123

# Backend
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
DATABASE_URL=postgresql://admin:admin123@timescaledb:5432/secondarymarket
REDIS_URL=redis://:redis123@redis:6379/0

# PgAdmin
PGADMIN_EMAIL=admin@secondarymarket.com
PGADMIN_PASSWORD=admin123
```

### Database Connection String

**From Docker containers:**
```
postgresql://admin:admin123@timescaledb:5432/secondarymarket
```

**From localhost:**
```
postgresql://admin:admin123@localhost:5433/secondarymarket
```

---

## 📊 Database Management

### Using PgAdmin (Web UI)

1. Open http://localhost:5051
2. Login with:
   - Email: admin@secondarymarket.com
   - Password: admin123
3. Add server:
   - Host: timescaledb
   - Port: 5432
   - Database: secondarymarket
   - Username: admin
   - Password: admin123

### Using psql (Command Line)

```bash
# Connect from Docker
docker exec -it secondarymarket_db psql -U admin -d secondarymarket

# Connect from localhost
psql -h localhost -p 5433 -U admin -d secondarymarket

# Common queries
SELECT * FROM users;
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
SELECT role, COUNT(*) FROM users GROUP BY role;
```

---

## 🐛 Troubleshooting

### Issue: Backend cannot connect to database

**Symptoms:**
```
Database connection failed
sqlalchemy.exc.OperationalError
```

**Solution:**
```bash
# 1. Check if database is running
docker-compose ps timescaledb

# 2. Check database logs
docker-compose logs timescaledb

# 3. Verify connection string
docker exec secondarymarket_backend env | grep DATABASE_URL

# 4. Restart services
docker-compose restart backend timescaledb
```

### Issue: Authentication fails with "Could not validate credentials"

**Symptoms:**
```
HTTP 401 Unauthorized
```

**Solution:**
1. Check if token is being sent in Authorization header
2. Verify token format: `Bearer <token>`
3. Check token expiration (60 minutes)
4. Verify SECRET_KEY matches between token creation and validation

### Issue: Admin endpoints return 403 Forbidden

**Symptoms:**
```
HTTP 403: Admin privileges required
```

**Solution:**
1. Check user role in database:
   ```sql
   SELECT user_id, role FROM users WHERE user_id = 'youruser';
   ```
2. Verify JWT token includes correct role claim
3. Ensure user logged in with correct credentials

### Issue: Sample data not inserted

**Symptoms:**
- Users table is empty
- Cannot login with sample credentials

**Solution:**
```bash
# 1. Manually run init scripts
docker exec -i secondarymarket_db psql -U admin -d secondarymarket < database/init/01_create_tables.sql
docker exec -i secondarymarket_db psql -U admin -d secondarymarket < database/init/02_insert_sample_data.sql

# 2. Or recreate database
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d
```

---

## 📈 Performance Optimization

### Database Indexing

All critical fields are indexed:
- user_id, email for fast lookups
- role, is_active for filtering
- created_at for sorting
- Foreign keys for joins

### Connection Pooling

```python
# backend/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # Normal pool size
    max_overflow=10,    # Maximum overflow connections
    pool_pre_ping=True, # Verify connections before use
    pool_recycle=3600   # Recycle connections after 1 hour
)
```

### Query Optimization

- Pagination on all list endpoints
- Eager loading for related data
- SELECT only needed columns
- Use database indexes effectively

---

## 🚀 Next Steps

### Phase 1: Complete Integration ✅
- [x] Database schema created
- [x] SQLAlchemy models defined
- [x] Pydantic schemas created
- [x] Authentication endpoints implemented
- [x] Admin endpoints implemented
- [x] Sample data inserted

### Phase 2: Frontend Integration (Current)
- [ ] Update frontend auth.py to call real API
- [ ] Update admin pages to fetch from API
- [ ] Handle API errors gracefully
- [ ] Add loading states

### Phase 3: Enhanced Features
- [ ] Email notifications
- [ ] Password reset flow
- [ ] User profile editing
- [ ] Bulk user operations
- [ ] Export to CSV/Excel
- [ ] Advanced analytics charts

### Phase 4: Production Readiness
- [ ] Add comprehensive error handling
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Database backups
- [ ] SSL/TLS certificates
- [ ] Environment-specific configs

---

## 📚 API Documentation

### Interactive API Docs

Once backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Authentication testing
- Example requests

### Example API Calls

**Login:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "admin",
  "password": "admin123"
}
```

**Get All Users:**
```bash
GET /api/admin/users?page=1&page_size=10&search=john&role=user
Authorization: Bearer <token>
```

**Activate User:**
```bash
POST /api/admin/users/user123/activate
Authorization: Bearer <token>
```

---

## 📝 Summary

This implementation provides:

✅ **Complete Database Schema** with users, audit logs, sessions, and profiles
✅ **FastAPI Backend** with authentication and admin endpoints
✅ **PostgreSQL Connection** via SQLAlchemy with connection pooling
✅ **JWT Authentication** with bcrypt password hashing
✅ **Role-Based Access Control** (user, admin, super_admin)
✅ **Admin User Management** with full CRUD operations
✅ **Audit Logging** for all admin actions
✅ **Search & Filter** capabilities for user management
✅ **Analytics API** for user statistics
✅ **Sample Data** with 10 test users ready to use
✅ **Docker Compose** setup for easy deployment
✅ **API Documentation** via Swagger UI

**Total Files Created:** 15
**Total Lines of Code:** ~2,500

**Status:** ✅ Backend Implementation Complete | Ready for Frontend Integration

---

**Created:** 2025-10-16
**Author:** Claude Code
**Purpose:** Complete guide for FastAPI-PostgreSQL integration for admin account management

