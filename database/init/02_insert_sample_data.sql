-- 02_insert_sample_data.sql
-- Sample data for development and testing

-- ==========================================
-- Sample Users
-- ==========================================

-- Note: Passwords are bcrypt hashed. Plain text passwords for reference:
-- admin: admin123
-- user123: password123
-- testuser: test123

-- Insert Super Admin
INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES (
    'admin',
    'admin@secondarymarket.com',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYW7nJxE4HO', -- admin123
    'super_admin',
    TRUE,
    '2024-01-01 10:00:00',
    CURRENT_TIMESTAMP
) ON CONFLICT (user_id) DO NOTHING;

-- Insert Admin User
INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES (
    'manager',
    'manager@secondarymarket.com',
    'Service Manager',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYW7nJxE4HO', -- admin123
    'admin',
    TRUE,
    '2024-02-15 14:30:00',
    CURRENT_TIMESTAMP - INTERVAL '2 hours'
) ON CONFLICT (user_id) DO NOTHING;

-- Insert Regular Users
INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES (
    'user123',
    'user123@example.com',
    'John Doe',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- password123
    'user',
    TRUE,
    '2024-06-15 14:20:00',
    CURRENT_TIMESTAMP - INTERVAL '1 day'
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES (
    'testuser',
    'test@example.com',
    'Test User',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- test123
    'user',
    TRUE,
    '2024-08-20 09:15:00',
    CURRENT_TIMESTAMP - INTERVAL '3 hours'
) ON CONFLICT (user_id) DO NOTHING;

INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES (
    'inactive_user',
    'inactive@example.com',
    'Jane Smith',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- test123
    'user',
    FALSE,
    '2024-03-20 09:15:00',
    '2024-12-01 16:20:00'
) ON CONFLICT (user_id) DO NOTHING;

-- Additional test users
INSERT INTO users (user_id, email, name, password_hash, role, is_active, created_at, last_login)
VALUES
    ('alice', 'alice@example.com', 'Alice Johnson', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', TRUE, '2024-07-10 11:00:00', CURRENT_TIMESTAMP - INTERVAL '5 hours'),
    ('bob', 'bob@example.com', 'Bob Williams', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', TRUE, '2024-07-15 13:30:00', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('charlie', 'charlie@example.com', 'Charlie Brown', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', TRUE, '2024-08-01 16:45:00', CURRENT_TIMESTAMP - INTERVAL '1 week'),
    ('diana', 'diana@example.com', 'Diana Prince', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', TRUE, '2024-08-15 10:20:00', CURRENT_TIMESTAMP - INTERVAL '4 hours'),
    ('eve', 'eve@example.com', 'Eve Adams', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'user', FALSE, '2024-05-20 14:00:00', '2024-11-15 09:30:00')
ON CONFLICT (user_id) DO NOTHING;

-- ==========================================
-- Sample User Profiles
-- ==========================================

INSERT INTO user_profiles (user_id, phone, city, country, bio)
VALUES
    ('admin', '+82-10-1234-5678', 'Seoul', 'South Korea', 'System administrator'),
    ('manager', '+82-10-2345-6789', 'Seoul', 'South Korea', 'Service manager'),
    ('user123', '+82-10-3456-7890', 'Busan', 'South Korea', 'Regular user'),
    ('testuser', '+82-10-4567-8901', 'Incheon', 'South Korea', 'Test account'),
    ('alice', '+82-10-5678-9012', 'Seoul', 'South Korea', 'Active user'),
    ('bob', '+82-10-6789-0123', 'Daegu', 'South Korea', 'Active user'),
    ('charlie', '+82-10-7890-1234', 'Gwangju', 'South Korea', 'Active user'),
    ('diana', '+82-10-8901-2345', 'Daejeon', 'South Korea', 'Active user')
ON CONFLICT (user_id) DO NOTHING;

-- ==========================================
-- Sample Audit Logs
-- ==========================================

INSERT INTO audit_logs (timestamp, admin_id, admin_name, action, target, details, ip_address)
VALUES
    (CURRENT_TIMESTAMP - INTERVAL '1 hour', 'admin', 'System Administrator', 'create_user', 'testuser', 'Created new test user account', '127.0.0.1'),
    (CURRENT_TIMESTAMP - INTERVAL '2 hours', 'admin', 'System Administrator', 'deactivate_user', 'inactive_user', 'Deactivated user account', '127.0.0.1'),
    (CURRENT_TIMESTAMP - INTERVAL '3 hours', 'manager', 'Service Manager', 'reset_password', 'user123', 'Password reset requested', '127.0.0.1'),
    (CURRENT_TIMESTAMP - INTERVAL '1 day', 'admin', 'System Administrator', 'activate_user', 'user123', 'Activated user account', '127.0.0.1'),
    (CURRENT_TIMESTAMP - INTERVAL '2 days', 'manager', 'Service Manager', 'view_user', 'alice', 'Viewed user profile', '127.0.0.1');

-- ==========================================
-- Display Summary
-- ==========================================

DO $$
DECLARE
    user_count INTEGER;
    admin_count INTEGER;
    active_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO admin_count FROM users WHERE role IN ('admin', 'super_admin');
    SELECT COUNT(*) INTO active_count FROM users WHERE is_active = TRUE;

    RAISE NOTICE '';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Database Initialization Complete';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Total Users: %', user_count;
    RAISE NOTICE 'Admin Users: %', admin_count;
    RAISE NOTICE 'Active Users: %', active_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Sample Credentials:';
    RAISE NOTICE '  - admin / admin123 (super_admin)';
    RAISE NOTICE '  - manager / admin123 (admin)';
    RAISE NOTICE '  - user123 / password123 (user)';
    RAISE NOTICE '  - testuser / test123 (user)';
    RAISE NOTICE '============================================';
    RAISE NOTICE '';
END $$;
