/**
 * Authentication Context
 * Manages user session state across the React Native app.
 */

"use client";

import React, {
    createContext,
    useContext,
    useEffect,
    useState,
    ReactNode,
} from "react";
import { Session, User, AuthError } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

// ============================================
// Types
// ============================================

interface AuthContextType {
    user: User | null;
    session: Session | null;
    isLoading: boolean;
    signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
    signUp: (email: string, password: string) => Promise<{ error: AuthError | null }>;
    signOut: () => Promise<void>;
    getToken: () => Promise<string | null>;
}

// ============================================
// Context
// ============================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================
// Provider Component
// ============================================

interface AuthProviderProps {
    children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check for existing session on app start
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                // Get initial session
                const { data: { session: initialSession } } = await supabase.auth.getSession();
                setSession(initialSession);
                setUser(initialSession?.user ?? null);
            } catch (error) {
                console.error("Error initializing auth:", error);
            } finally {
                setIsLoading(false);
            }
        };

        initializeAuth();

        // Listen for auth state changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, currentSession) => {
                console.log("Auth state changed:", event);
                setSession(currentSession);
                setUser(currentSession?.user ?? null);
                setIsLoading(false);
            }
        );

        // Cleanup subscription on unmount
        return () => {
            subscription.unsubscribe();
        };
    }, []);

    // Sign in with email and password
    const signIn = async (email: string, password: string) => {
        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            });
            return { error };
        } catch (error) {
            return { error: error as AuthError };
        }
    };

    // Sign up with email and password
    const signUp = async (email: string, password: string) => {
        try {
            const { error } = await supabase.auth.signUp({
                email,
                password,
            });
            return { error };
        } catch (error) {
            return { error: error as AuthError };
        }
    };

    // Sign out
    const signOut = async () => {
        try {
            await supabase.auth.signOut();
            setUser(null);
            setSession(null);
        } catch (error) {
            console.error("Error signing out:", error);
        }
    };

    // Get access token for API calls (with auto-refresh)
    const getToken = async (): Promise<string | null> => {
        try {
            // 1. Get current session
            const { data: { session: currentSession }, error } = await supabase.auth.getSession();

            if (error) {
                console.error("Error getting session:", error);
                return null;
            }

            if (!currentSession) {
                console.log("No active session found");
                return null;
            }

            // 2. Check if token is expiring soon (< 60 seconds)
            const expiresAt = currentSession.expires_at;
            const now = Math.floor(Date.now() / 1000);

            if (expiresAt && expiresAt - now < 60) {
                console.log("Token expiring soon, refreshing...");
                const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();

                if (refreshError || !refreshData.session) {
                    console.error("Failed to refresh session:", refreshError);
                    return null;
                }

                console.log("Token refreshed successfully");
                return refreshData.session.access_token;
            }

            return currentSession.access_token;
        } catch (error) {
            console.error("Error getting token:", error);
            return null;
        }
    };

    const value: AuthContextType = {
        user,
        session,
        isLoading,
        signIn,
        signUp,
        signOut,
        getToken,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ============================================
// Hook
// ============================================

export function useAuth(): AuthContextType {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}

export default AuthContext;
