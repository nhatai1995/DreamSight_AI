"use client";

import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { motion } from "framer-motion";
import { LogIn, User, LogOut, Loader2, History } from "lucide-react";
import { useState } from "react";

/**
 * AuthButton Component
 * Shows login button when not logged in, user menu when logged in
 */
export default function AuthButton() {
    const { user, isLoading, signOut } = useAuth();
    const [showMenu, setShowMenu] = useState(false);

    if (isLoading) {
        return (
            <div className="w-10 h-10 flex items-center justify-center">
                <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
            </div>
        );
    }

    // User is logged in
    if (user) {
        return (
            <div className="relative">
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowMenu(!showMenu)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-colors"
                >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-purple-300 text-sm hidden sm:block max-w-[120px] truncate">
                        {user.email?.split("@")[0]}
                    </span>
                </motion.button>

                {/* Dropdown Menu */}
                {showMenu && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute top-full right-0 mt-2 w-48 bg-slate-900 border border-white/10 rounded-xl shadow-xl overflow-hidden z-50"
                    >
                        <div className="p-3 border-b border-white/10">
                            <p className="text-xs text-gray-500">Đăng nhập với</p>
                            <p className="text-sm text-gray-200 truncate">{user.email}</p>
                        </div>
                        <Link
                            href="/profile"
                            onClick={() => setShowMenu(false)}
                            className="w-full flex items-center gap-2 px-4 py-3 text-gray-300 hover:bg-purple-500/10 transition-colors text-sm"
                        >
                            <History className="w-4 h-4" />
                            <span>Hồ sơ & Lịch sử</span>
                        </Link>
                        <button
                            onClick={() => {
                                signOut();
                                setShowMenu(false);
                            }}
                            className="w-full flex items-center gap-2 px-4 py-3 text-red-400 hover:bg-red-500/10 transition-colors text-sm"
                        >
                            <LogOut className="w-4 h-4" />
                            <span>Đăng xuất</span>
                        </button>
                    </motion.div>
                )}
            </div>
        );
    }

    // User is not logged in - show login button
    return (
        <Link href="/auth">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600/80 to-cyan-600/80 hover:from-purple-600 hover:to-cyan-600 border border-purple-500/30 text-white font-medium text-sm transition-all shadow-lg shadow-purple-500/20"
            >
                <LogIn className="w-4 h-4" />
                <span className="hidden sm:inline">Đăng nhập</span>
            </motion.button>
        </Link>
    );
}
