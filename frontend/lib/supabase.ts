/**
 * Supabase Client Configuration
 * Initializes Supabase for Web (Next.js).
 * Uses default browser localStorage for session persistence.
 */

import { createClient } from "@supabase/supabase-js";

// ============================================
// Environment Variables (Next.js uses NEXT_PUBLIC_ prefix)
// ============================================
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// Validate configuration
if (!SUPABASE_URL || SUPABASE_URL.includes("your-project")) {
    console.warn("⚠️ NEXT_PUBLIC_SUPABASE_URL is not configured properly");
}
if (!SUPABASE_ANON_KEY || SUPABASE_ANON_KEY === "your-anon-key-here") {
    console.warn("⚠️ NEXT_PUBLIC_SUPABASE_ANON_KEY is not configured properly");
}

// Create Supabase client
// Note: In Web environment, Supabase automatically uses localStorage
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true, // Useful for OAuth callbacks on web
    },
});

/**
 * Get the current user's access token (for API calls).
 * Returns null if not logged in.
 */
export async function getAccessToken(): Promise<string | null> {
    try {
        const { data } = await supabase.auth.getSession();
        return data.session?.access_token ?? null;
    } catch (error) {
        console.error("Error getting access token:", error);
        return null;
    }
}

/**
 * Check if user is currently authenticated.
 */
export async function isAuthenticated(): Promise<boolean> {
    const { data } = await supabase.auth.getSession();
    return !!data.session;
}

/**
 * Get current user info.
 */
export async function getCurrentUser() {
    const { data } = await supabase.auth.getUser();
    return data.user;
}

export default supabase;
