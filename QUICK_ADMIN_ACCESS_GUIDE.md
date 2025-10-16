# 🚀 Quick Guide: View All User Accounts as Admin

## Method 1: Using Admin Test Setup Page (Easiest)

### Step 1: Login
1. Go to http://localhost:8501
2. Click "로그인" button
3. Enter any credentials (e.g., `test` / `test123`)
4. Click "로그인"

### Step 2: Set Admin Role
1. Click on your username menu (👤) in top right
2. Click "🧪 Testing Setup"
3. Click the **"🛡️ Set as Admin"** button
4. Page will refresh with admin permissions

### Step 3: Access User Management
1. Click your username menu again (👤)
2. You should now see **"🛡️ Admin"** section
3. Click **"User Management"**
4. You'll see all 10 sample users!

---

## Method 2: Direct URL Access

1. Login first (any credentials)
2. Go to: http://localhost:8501/pages/admin_test_setup.py
3. Click "🛡️ Set as Admin"
4. Go to: http://localhost:8501/pages/admin/users.py
5. See all users!

---

## Method 3: Modify Auth File (For Testing)

Edit `frontend/utils/auth.py` line 120:

**Before:**
```python
if user_id and password:
    return True, {
        'user_id': user_id,
        'user_name': user_id,
        'access_token': 'dummy_token'
    }, None
```

**After:**
```python
if user_id and password:
    return True, {
        'user_id': user_id,
        'user_name': user_id,
        'role': 'admin',  # ← Add this line
        'access_token': 'dummy_token'
    }, None
```

Now every login will have admin role automatically.

---

## What You Should See

### User Management Page Features:

**Search & Filter:**
- 🔍 Search box (find by ID, email, name)
- Role dropdown (All, User, Admin, Super Admin)
- Status dropdown (All, Active, Inactive)
- 🔄 Refresh button

**User List (10 sample users):**
1. ✅ admin - Administrator (super_admin)
2. ✅ manager - Service Manager (admin)
3. ✅ user123 - John Doe (user)
4. ✅ testuser - Test User (user)
5. ✅ alice - Alice Johnson (user)
6. ✅ bob - Bob Williams (user)
7. ✅ charlie - Charlie Brown (user)
8. ✅ diana - Diana Prince (user)
9. ❌ inactive_user - Jane Smith (user, inactive)
10. ❌ eve - Eve Adams (user, inactive)

**Each user card shows:**
- User ID
- Email
- Full Name
- Role
- Status (Active/Inactive)
- Registration date
- Last login time

**Admin Actions:**
- 📝 Edit Profile
- ✅/🚫 Activate/Deactivate
- 🔑 Reset Password
- 🗑️ Delete User

---

## Troubleshooting

### "Can't see Admin section in menu"

**Solution:**
1. Make sure you clicked "Set as Admin" button
2. Check page refreshed (look for "✅ Admin - Can manage users")
3. Click your username menu again

### "User Management button is disabled"

**Cause:** Role not set to admin

**Solution:**
1. Go back to Admin Test Setup
2. Click "Set as Admin" again
3. Wait for page to refresh

### "Still showing as regular user"

**Solution:**
1. Logout completely
2. Login again
3. Go to Admin Test Setup
4. Click "Set as Admin"

---

## Quick Test Commands

```bash
# 1. Start services
docker-compose up -d

# 2. Check if services are running
docker-compose ps

# 3. Check backend health
curl http://localhost:8000/health

# 4. Open frontend
open http://localhost:8501
```

---

## Video Guide (Text Version)

**Step-by-Step:**
```
1. Login → Enter "test" / "test123" → Click Login
2. Click 👤 menu → Click "Testing Setup"
3. See current role: "Regular User"
4. Click "🛡️ Set as Admin" button
5. Page refreshes
6. See current role: "Admin"
7. Click 👤 menu again
8. See "🛡️ Admin" section (NEW!)
9. Click "User Management"
10. SEE ALL 10 USERS! ✅
```

---

## Expected Result

After following the steps, you should see:

```
📊 Found 10 user(s)

✅ Administrator (@admin) - SUPER_ADMIN
✅ Service Manager (@manager) - ADMIN
✅ John Doe (@user123) - USER
✅ Test User (@testuser) - USER
✅ Alice Johnson (@alice) - USER
✅ Bob Williams (@bob) - USER
✅ Charlie Brown (@charlie) - USER
✅ Diana Prince (@diana) - USER
❌ Jane Smith (@inactive_user) - USER
❌ Eve Adams (@eve) - USER
```

---

**Created:** 2025-10-16
**Purpose:** Quick guide to access admin user management
**Status:** For testing/development only
