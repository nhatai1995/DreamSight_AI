/**
 * Authentication Screen
 * Simple login/signup form with email and password.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Lock, LogIn, UserPlus, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function AuthScreen() {
    const router = useRouter();
    const { signIn, signUp, isLoading: authLoading } = useAuth();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isSignUp, setIsSignUp] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setIsLoading(true);

        try {
            if (isSignUp) {
                // Sign Up
                const { error } = await signUp(email, password);
                if (error) {
                    setError(error.message);
                } else {
                    setSuccess("Account created! Please check your email to verify.");
                }
            } else {
                // Sign In
                const { error } = await signIn(email, password);
                if (error) {
                    setError(error.message);
                } else {
                    // Redirect to home on successful login
                    router.push("/");
                }
            }
        } catch (err) {
            setError("An unexpected error occurred. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    if (authLoading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
            {/* Background Effects */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-[20%] left-[10%] w-[40%] h-[40%] bg-purple-900/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[20%] right-[10%] w-[40%] h-[40%] bg-cyan-900/20 rounded-full blur-[120px]" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10 w-full max-w-md"
            >
                {/* Card */}
                <div className="p-px rounded-2xl bg-gradient-to-b from-purple-500/30 to-cyan-500/30">
                    <div className="bg-slate-950/90 rounded-2xl p-8 backdrop-blur-xl">
                        {/* Header */}
                        <div className="text-center mb-8">
                            <div className="text-5xl mb-4">👁️</div>
                            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-cyan-400">
                                {isSignUp ? "Create Account" : "Welcome Back"}
                            </h1>
                            <p className="text-gray-400 mt-2 text-sm">
                                {isSignUp
                                    ? "Join the Oracle to save your dreams"
                                    : "Sign in to access your dream history"}
                            </p>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Email Input */}
                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-purple-400 transition-colors" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="Email address"
                                    required
                                    className="w-full pl-12 pr-4 py-3 bg-slate-900/50 border border-white/10 rounded-xl text-gray-100 placeholder-gray-500 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all"
                                />
                            </div>

                            {/* Password Input */}
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-purple-400 transition-colors" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Password"
                                    required
                                    minLength={6}
                                    className="w-full pl-12 pr-4 py-3 bg-slate-900/50 border border-white/10 rounded-xl text-gray-100 placeholder-gray-500 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all"
                                />
                            </div>

                            {/* Error Message */}
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex items-center gap-2 p-3 bg-red-900/30 border border-red-500/30 rounded-lg text-red-200 text-sm"
                                >
                                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                    <span>{error}</span>
                                </motion.div>
                            )}

                            {/* Success Message */}
                            {success && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-3 bg-green-900/30 border border-green-500/30 rounded-lg text-green-200 text-sm"
                                >
                                    {success}
                                </motion.div>
                            )}

                            {/* Submit Button */}
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-3 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl font-semibold text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : isSignUp ? (
                                    <>
                                        <UserPlus className="w-5 h-5" />
                                        <span>Sign Up</span>
                                    </>
                                ) : (
                                    <>
                                        <LogIn className="w-5 h-5" />
                                        <span>Sign In</span>
                                    </>
                                )}
                            </motion.button>
                        </form>

                        {/* Toggle Sign In / Sign Up */}
                        <div className="mt-6 text-center">
                            <button
                                type="button"
                                onClick={() => {
                                    setIsSignUp(!isSignUp);
                                    setError(null);
                                    setSuccess(null);
                                }}
                                className="text-gray-400 hover:text-white text-sm transition-colors"
                            >
                                {isSignUp ? (
                                    <>
                                        Already have an account?{" "}
                                        <span className="text-purple-400">Sign in</span>
                                    </>
                                ) : (
                                    <>
                                        Don't have an account?{" "}
                                        <span className="text-cyan-400">Sign up</span>
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Continue as Guest */}
                        <div className="mt-4 text-center">
                            <button
                                type="button"
                                onClick={() => router.push("/")}
                                className="text-gray-500 hover:text-gray-300 text-xs transition-colors"
                            >
                                Continue as Guest →
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
