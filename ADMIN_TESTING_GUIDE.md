# 🧪 Admin Dashboard Testing Guide

## How to Check All User Accounts as an Admin

Since the backend is not yet connected, here's how to test the admin dashboard with mock data.

---

## Quick Start: View All Accounts

### Step 1: Set Your User as Admin

**Option A: Modify auth.py temporarily (Recommended for Testing)**

Edit `frontend/utils/auth.py` around line 120:

```python
# Find the authenticate_with_backend function
def authenticate_with_backend(user_id: str, password: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    # ... existing code ...

    # TEMPORARY: Accept any credentials and set admin role
    if user_id and password:
        return True, {
            'user_id': user_id,
            'user_name': user_id,
            'role': 'admin',  # ← Add this line
            'access_token': 'dummy_token'
        }, None
```

Save the file and restart Streamlit.

**Option B: Create a test admin button**

I'll create a testing utility page for you (see below).

---

### Step 2: Login

1. Open http://localhost:8501
2. Click "로그인" button
3. Enter any user_id (e.g., "admin") and password
4. Click "로그인"
5. You'll be redirected to finance.py

---

### Step 3: Access User Management

**Method 1: From Header**
- Look for the user menu (👤 your_username)
- If you're an admin, you should see an "Admin Dashboard" option
- (Note: This needs to be added - see enhancement below)

**Method 2: Direct URL**
- Navigate to: `http://localhost:8501/pages/admin/dashboard.py`
- Or: `http://localhost:8501/pages/admin/users.py` (direct to user list)

**Method 3: From Finance Page**
- I'll add a button to the finance page for admins

---

### Step 4: View All User Accounts

Once on the User Management page (`pages/admin/users.py`):

1. **See all users**: By default, all sample users are displayed
2. **Search users**: Type in the search box to filter by ID, email, or name
3. **Filter by role**: Select "All", "User", "Admin", or "Super Admin"
4. **Filter by status**: Select "All", "Active", or "Inactive"
5. **View details**: Click on any user card to expand and see full information

---

## Sample User Accounts Available

The current mock data includes 3 sample users:

| User ID | Name | Email | Role | Status | Created | Last Login |
|---------|------|-------|------|--------|---------|------------|
| admin | Administrator | admin@example.com | admin | Active | 2024-01-01 | 2025-10-16 |
| user123 | John Doe | user123@example.com | user | Active | 2024-06-15 | 2025-10-15 |
| inactive_user | Jane Smith | inactive@example.com | user | Inactive | 2024-03-20 | 2024-12-01 |

---

## User Information Displayed

For each account, you can see:

- **User ID**: Unique identifier
- **Email**: Contact email
- **Name**: Full name
- **Role**: user / admin / super_admin
- **Status**: Active (✅) or Inactive (❌)
- **Registered**: Account creation date
- **Last Login**: Most recent login timestamp

---

## Admin Actions Available

For users you have permission to manage:

1. **📝 Edit Profile**: Modify user information (placeholder)
2. **✅/🚫 Activate/Deactivate**: Toggle account status
3. **🔑 Reset Password**: Send password reset email
4. **🗑️ Delete User**: Permanently remove user (requires confirmation)

**Permission Rules:**
- Regular admin can only manage regular users
- Super admin can manage everyone including admins

---

## Troubleshooting

### Issue: "Access Denied" when accessing admin pages

**Cause**: Your user doesn't have admin role

**Solution**:
1. Check that you modified `auth.py` to add `'role': 'admin'`
2. Make sure you restarted Streamlit after making changes
3. Try logging out and logging back in

### Issue: No admin dashboard option in menu

**Cause**: Admin menu items not added to header yet

**Solution**: Use direct URL navigation (see Step 3 above)

### Issue: Can't see all users

**Cause**: Filters are applied

**Solution**:
1. Clear the search box
2. Set Role filter to "All"
3. Set Status filter to "All"
4. Click "🔄 Refresh"

---

## Testing Scenarios

### Scenario 1: View All Active Users

1. Go to User Management page
2. Select "Active" from Status filter
3. Keep Role as "All"
4. Expected: See 2 active users (admin, user123)

### Scenario 2: View Only Admins

1. Go to User Management page
2. Select "Admin" from Role filter
3. Expected: See 1 admin user

### Scenario 3: Search for Specific User

1. Go to User Management page
2. Type "john" in search box
3. Expected: See user123 (John Doe)

### Scenario 4: View Inactive Accounts

1. Go to User Management page
2. Select "Inactive" from Status filter
3. Expected: See 1 inactive user (inactive_user)

---

## Current Limitations

⚠️ **Mock Data Only**
- Only 3 sample users exist
- No real database connection
- Changes don't persist after page refresh

⚠️ **Actions Don't Persist**
- Activate/deactivate shows messages but doesn't save
- Delete shows confirmation but doesn't actually delete
- Edit profile is placeholder only

⚠️ **No Pagination**
- All users load at once
- Will need pagination when connected to real database

---

## When Backend Is Ready

Once backend APIs are implemented, the user management page will:

✅ Fetch real user data from database
✅ Support pagination (10, 25, 50, 100 users per page)
✅ Persist all actions (activate, deactivate, delete)
✅ Show real-time user counts
✅ Display actual registration and login timestamps
✅ Support bulk operations
✅ Export user list to CSV/Excel

---

## Quick Reference: URL Navigation

```bash
# Main pages
http://localhost:8501                          # Home/Finance page
http://localhost:8501/pages/login.py          # Login page

# Admin pages (require admin role)
http://localhost:8501/pages/admin/dashboard.py   # Admin dashboard
http://localhost:8501/pages/admin/users.py       # User management
http://localhost:8501/pages/admin/analytics.py   # Analytics
```

---

## Next: I'll Create a Testing Utility

To make testing easier, I'll create:
1. A testing utility page that lets you switch roles
2. Add admin dashboard link to header for admins
3. Add quick admin access from finance page

This will make it much easier to test admin features without manually editing code.

---

**Created:** 2025-10-16
**Purpose:** Guide for testing admin dashboard with mock data
**Status:** For Development/Testing Only
