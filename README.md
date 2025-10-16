# 📈 Secondary Market Application

Simple stock market data platform with admin user management.

Built with **FastAPI**, **PostgreSQL**, **Streamlit**, and **Docker**.

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd secondarymarket

# 2. Start all services
docker-compose up -d

# 3. Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000/docs
# PgAdmin: http://localhost:5051
```

**That's it!** The database will auto-initialize with sample data.

---

## 🔐 Test Credentials

| User ID | Password | Role | Description |
|---------|----------|------|-------------|
| **admin** | admin123 | super_admin | Full system access |
| **manager** | admin123 | admin | Can manage users |
| **user123** | password123 | user | Regular user |

**10 sample users** total are pre-loaded for testing.

---

## 📊 Features

### For Users
- 📈 Real-time stock market data
- 📋 Listed stock information
- 📰 Daily disclosure and news
- 🔐 Secure authentication

### For Admins
- 👥 **User Management** - View, search, filter all accounts
- ✅ **User Actions** - Activate, deactivate, delete users
- 📊 **Analytics** - User statistics and trends
- 📝 **Audit Logs** - Track all admin actions

---

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│  Streamlit  │─────▶│   FastAPI   │─────▶│  PostgreSQL  │
│  Frontend   │      │   Backend   │      │  +TimescaleDB│
│   :8501     │      │    :8000    │      │    :5432     │
└─────────────┘      └─────────────┘      └──────────────┘
                            │
                     ┌──────────────┐
                     │    Redis     │
                     │   Cache      │
                     │    :6379     │
                     └──────────────┘
```

---

## 📁 Project Structure

```
secondarymarket/
├── backend/                  # FastAPI Application
│   ├── main.py              # App entry point
│   ├── database.py          # DB connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── routes_auth.py       # Auth endpoints
│   └── routes_admin.py      # Admin endpoints
│
├── frontend/                 # Streamlit Application
│   ├── app.py               # Main page
│   ├── auth.py              # Auth utilities
│   ├── pages/               # Additional pages
│   │   ├── login.py
│   │   ├── signup.py
│   │   ├── stocks.py
│   │   ├── disclosure.py
│   │   ├── news.py
│   │   └── admin/           # Admin pages
│   │       ├── dashboard.py
│   │       ├── users.py
│   │       └── analytics.py
│   └── components/
│       └── header.py
│
├── database/
│   └── init.sql             # Database schema + sample data
│
├── docker-compose.yml       # Service orchestration
└── README.md                # This file
```

**Simple. Clear. Easy to navigate.**

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | POST | User login → JWT token |
| `/register` | POST | Create new account |
| `/me` | GET | Get current user info |

### Admin (`/api/admin`)

| Endpoint | Method | Description | Required Role |
|----------|--------|-------------|---------------|
| `/users` | GET | List all users (with search/filter) | admin |
| `/users/{user_id}` | GET | Get user details | admin |
| `/users/{user_id}` | PUT | Update user | admin |
| `/users/{user_id}/activate` | POST | Activate account | admin |
| `/users/{user_id}/deactivate` | POST | Deactivate account | admin |
| `/users/{user_id}` | DELETE | Delete user | admin |
| `/users/{user_id}/reset-password` | POST | Reset password | admin |
| `/audit-logs` | GET | View admin actions | admin |
| `/analytics/users` | GET | User statistics | admin |

---

## 💻 Development

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ for local development

### Local Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

**Database:**
```bash
# Connect to PostgreSQL
psql -h localhost -p 5433 -U admin -d secondarymarket

# View users
SELECT user_id, email, role, is_active FROM users;
```

---

## 🧪 Testing

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id":"admin","password":"admin123"}'
```

### Test Admin API
```bash
# Get all users (replace <TOKEN> with token from login)
curl http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer <TOKEN>"
```

### Interactive API Testing
Visit **http://localhost:8000/docs** for Swagger UI

---

## 🔐 Admin Features Guide

### How to View All User Accounts

**1. Login as Admin:**
- Go to http://localhost:8501
- Login with `admin` / `admin123`

**2. Access User Management:**
- Click user menu (👤 admin)
- Click "User Management"

**3. View & Manage Users:**
- **Search**: Find users by ID, email, or name
- **Filter**: By role (user/admin) or status (active/inactive)
- **Actions**: Activate, deactivate, reset password, delete

**4. View Analytics:**
- Click "Analytics" from admin menu
- See user statistics, registration trends, activity rates

**5. Check Audit Logs:**
- Return to dashboard
- View "Recent Activity" section
- See all admin actions with timestamps

### Permission Levels

**Super Admin (`admin`):**
- ✅ Can manage all users including admins
- ✅ Full system access

**Admin (`manager`):**
- ✅ Can manage regular users
- ❌ Cannot manage other admins

**User (`user123`):**
- ❌ No admin access
- ✅ Can view own data only

---

## 📊 Database Schema

**Main Tables:**
- `users` - User accounts with roles
- `audit_logs` - Admin action history
- `sessions` - Active user sessions
- `password_reset_tokens` - Password reset flow
- `user_profiles` - Extended user information

**Sample Query:**
```sql
-- Get admin users
SELECT user_id, name, email, last_login
FROM users
WHERE role IN ('admin', 'super_admin')
ORDER BY last_login DESC;
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit 1.28+ |
| **Backend** | FastAPI 0.104+ |
| **Database** | PostgreSQL 16 + TimescaleDB |
| **Cache** | Redis 7 |
| **Auth** | JWT + Bcrypt |
| **ORM** | SQLAlchemy 2.0 |
| **Validation** | Pydantic 2.5 |
| **Deployment** | Docker Compose |

---

## 🔧 Configuration

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
SECRET_KEY=your-super-secret-key-min-32-chars-long
DATABASE_URL=postgresql://admin:admin123@timescaledb:5432/secondarymarket

# PgAdmin
PGADMIN_EMAIL=admin@secondarymarket.com
PGADMIN_PASSWORD=admin123
```

---

## 📝 Common Tasks

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
# All
docker-compose restart

# Specific
docker-compose restart backend
```

### Stop & Clean
```bash
# Stop all
docker-compose down

# Stop & remove volumes (⚠️ deletes data!)
docker-compose down -v
```

### Database Backup
```bash
# Backup
docker exec secondarymarket_db pg_dump -U admin secondarymarket > backup.sql

# Restore
docker exec -i secondarymarket_db psql -U admin secondarymarket < backup.sql
```

---

## 🐛 Troubleshooting

### "Database connection failed"
```bash
# Check if database is running
docker-compose ps timescaledb

# Check database logs
docker-compose logs timescaledb

# Restart database
docker-compose restart timescaledb
```

### "Authentication failed"
- Verify credentials are correct (`admin` / `admin123`)
- Check if user is active in database
- Ensure token hasn't expired (60 min)

### "Admin features not visible"
- Login with admin account (`admin` or `manager`)
- Check user role in database:
  ```sql
  SELECT user_id, role FROM users WHERE user_id='your_user';
  ```

---

## 📚 Documentation

**Archived detailed docs** available in `docs/archive/`:
- API specifications
- Database schema details
- Implementation guides
- Architecture decisions

---

## 🎯 Roadmap

**Current Version: 1.0**
- ✅ User authentication
- ✅ Admin user management
- ✅ Audit logging
- ✅ Analytics dashboard

**Planned:**
- [ ] Email notifications
- [ ] Password reset flow
- [ ] User profile editing
- [ ] Export to CSV/Excel
- [ ] Advanced analytics
- [ ] Real-time stock data integration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is for educational purposes.

---

## 💬 Support

**Issues?** Open an issue on GitHub.

**Questions?** Check the archived documentation in `docs/archive/`.

---

**Last Updated:** 2025-10-16
**Version:** 1.0
**Status:** Production Ready ✅

---

Made with ❤️ using FastAPI, PostgreSQL, and Streamlit
