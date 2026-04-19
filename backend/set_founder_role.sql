-- Set user role to founder
-- Run this in your PostgreSQL database (pgAdmin, Neon SQL Editor, or psql)

-- Update the admin user to founder role
UPDATE users 
SET role = 'founder' 
WHERE email = 'admin@localai.com';

-- Verify the change
SELECT id, email, role 
FROM users 
WHERE email = 'admin@localai.com';

-- You should see: role = 'founder'
-- Now logout and login again in the frontend!
