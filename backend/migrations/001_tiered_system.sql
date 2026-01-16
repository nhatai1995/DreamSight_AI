-- =============================================================================
-- DreamSight AI - Tiered Service System Migration
-- Run this SQL in Supabase SQL Editor: https://supabase.com/dashboard
-- =============================================================================

-- ============================================
-- PART 1: Create/Update profiles table
-- ============================================

-- Create profiles table if it doesn't exist (linked to auth.users)
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  display_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'master')),
  daily_usage INTEGER DEFAULT 0,
  last_reset_date DATE DEFAULT CURRENT_DATE
);

-- If table already exists, add the new columns
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'free',
ADD COLUMN IF NOT EXISTS daily_usage INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reset_date DATE DEFAULT CURRENT_DATE;

-- Add constraint for tier values (may fail if already exists)
DO $$
BEGIN
  ALTER TABLE profiles ADD CONSTRAINT profiles_tier_check CHECK (tier IN ('free', 'master'));
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Create index for faster tier lookups
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(tier);

-- Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile" 
  ON profiles FOR SELECT 
  USING (auth.uid() = id);

-- Policy: Users can update their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = id);

-- Trigger to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (NEW.id, NEW.email)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if exists, then create
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ============================================
-- PART 2: Create guest_usage tracking table
-- ============================================

CREATE TABLE IF NOT EXISTS guest_usage (
  ip_address TEXT PRIMARY KEY,
  usage_date DATE DEFAULT CURRENT_DATE,
  request_count INTEGER DEFAULT 0
);


-- ============================================
-- PART 3: PostgreSQL Functions
-- ============================================

-- Function to check and consume guest quota (FIXED first-request logic)
CREATE OR REPLACE FUNCTION check_guest_quota(guest_ip TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  current_count INTEGER;
  current_date_val DATE;
BEGIN
  -- Check if record exists
  SELECT request_count, usage_date INTO current_count, current_date_val
  FROM guest_usage WHERE ip_address = guest_ip;
  
  -- Case 1: New IP (no record exists)
  IF NOT FOUND THEN
    INSERT INTO guest_usage (ip_address, usage_date, request_count)
    VALUES (guest_ip, CURRENT_DATE, 1);
    RETURN TRUE;  -- First request allowed
  END IF;
  
  -- Case 2: Existing IP but different day (reset)
  IF current_date_val < CURRENT_DATE THEN
    UPDATE guest_usage 
    SET request_count = 1, usage_date = CURRENT_DATE
    WHERE ip_address = guest_ip;
    RETURN TRUE;  -- First request of new day
  END IF;
  
  -- Case 3: Same day, check quota (1 per day for guest)
  IF current_count < 1 THEN
    UPDATE guest_usage SET request_count = request_count + 1 
    WHERE ip_address = guest_ip;
    RETURN TRUE;
  END IF;
  
  -- Quota exceeded
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql;


-- Function to increment member daily usage
CREATE OR REPLACE FUNCTION increment_daily_usage(p_user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE profiles 
  SET daily_usage = daily_usage + 1
  WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;


-- Function to reset daily usage (called by cron or admin endpoint)
CREATE OR REPLACE FUNCTION reset_daily_usage()
RETURNS void AS $$
BEGIN
  UPDATE profiles 
  SET daily_usage = 0, last_reset_date = CURRENT_DATE
  WHERE last_reset_date < CURRENT_DATE OR last_reset_date IS NULL;
  
  -- Also reset guest usage table
  DELETE FROM guest_usage WHERE usage_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;


-- Function to cleanup old dreams (30-day retention)
CREATE OR REPLACE FUNCTION cleanup_old_dreams()
RETURNS void AS $$
BEGIN
  DELETE FROM dreams WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- PART 4: Optional pg_cron (if available)
-- ============================================
-- Note: pg_cron may not be available on Supabase Free tier
-- Use the admin endpoint POST /admin/cron/reset-usage as fallback

-- Uncomment these lines if pg_cron is enabled:
-- SELECT cron.schedule('reset-daily-usage', '0 0 * * *', 'SELECT reset_daily_usage();');
-- SELECT cron.schedule('cleanup-old-dreams', '0 1 * * *', 'SELECT cleanup_old_dreams();');


-- ============================================
-- VERIFICATION: Check migration success
-- ============================================
-- Run these to verify:

-- SELECT column_name, data_type, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'profiles' AND column_name IN ('tier', 'daily_usage', 'last_reset_date');

-- SELECT * FROM guest_usage LIMIT 5;
