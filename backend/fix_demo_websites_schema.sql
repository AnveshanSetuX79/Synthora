-- Fix demo_websites table schema
-- Run this in your database to add the missing html_content column

-- Check if html_content column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'demo_websites' 
        AND column_name = 'html_content'
    ) THEN
        -- Drop old columns if they exist
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'demo_websites' AND column_name = 'url') THEN
            ALTER TABLE demo_websites DROP COLUMN IF EXISTS url;
        END IF;
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'demo_websites' AND column_name = 'cached') THEN
            ALTER TABLE demo_websites DROP COLUMN IF EXISTS cached;
        END IF;
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'demo_websites' AND column_name = 'unique_visitors') THEN
            ALTER TABLE demo_websites DROP COLUMN IF EXISTS unique_visitors;
        END IF;
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'demo_websites' AND column_name = 'avg_time_on_page') THEN
            ALTER TABLE demo_websites DROP COLUMN IF EXISTS avg_time_on_page;
        END IF;
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'demo_websites' AND column_name = 'generated_at') THEN
            ALTER TABLE demo_websites DROP COLUMN IF EXISTS generated_at;
        END IF;
        
        -- Add new columns
        ALTER TABLE demo_websites ADD COLUMN html_content TEXT;
        ALTER TABLE demo_websites ADD COLUMN last_viewed_at TIMESTAMPTZ;
        ALTER TABLE demo_websites ADD COLUMN created_by VARCHAR(36);
        
        -- Add foreign key for created_by
        ALTER TABLE demo_websites 
        ADD CONSTRAINT fk_demo_websites_created_by 
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;
        
        -- Make html_content non-nullable (after adding it)
        -- First set a default value for existing rows
        UPDATE demo_websites SET html_content = '<html><body>Demo content</body></html>' WHERE html_content IS NULL;
        
        -- Now make it non-nullable
        ALTER TABLE demo_websites ALTER COLUMN html_content SET NOT NULL;
        
        RAISE NOTICE 'Successfully added html_content column to demo_websites table';
    ELSE
        RAISE NOTICE 'html_content column already exists in demo_websites table';
    END IF;
END $$;
