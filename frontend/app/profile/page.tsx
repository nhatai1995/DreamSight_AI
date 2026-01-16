"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    User, History, Settings, LogOut, ArrowLeft,
    Loader2, Moon, ChevronDown, ChevronUp,
    Eye, Sparkles, BookOpen, Lock, Calendar,
    Save, AlertCircle, CheckCircle, Users
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { supabase } from "@/lib/supabase";

// ============================================
// Types
// ============================================

interface DreamHistoryItem {
    id: string;
    content: string;
    analysis_data: {
        interpretation?: string;
        mode?: string;
    };
    created_at: string;
}

interface UserProfile {
    display_name: string;
    birthdate: string;
    gender: string;
}

// ============================================
// Dream History Card Component
// ============================================

function DreamCard({ dream }: { dream: DreamHistoryItem }) {
    const [expanded, setExpanded] = useState(false);

    const date = new Date(dream.created_at).toLocaleDateString("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-900/50 border border-white/10 rounded-xl overflow-hidden"
        >
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full p-4 text-left hover:bg-white/5 transition-colors"
            >
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                            <Moon className="w-4 h-4 text-purple-400" />
                            <span className="text-xs text-gray-500">{date}</span>
                        </div>
                        <p className="text-gray-200 line-clamp-2">
                            {dream.content}
                        </p>
                    </div>
                    {expanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                    ) : (
                        <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                    )}
                </div>
            </button>

            <AnimatePresence>
                {expanded && dream.analysis_data?.interpretation && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-white/10"
                    >
                        <div className="p-4 bg-purple-950/20">
                            <div className="flex items-center gap-2 mb-3">
                                <Eye className="w-4 h-4 text-cyan-400" />
                                <span className="text-sm font-medium text-cyan-300">Giải mã</span>
                            </div>
                            <p className="text-sm text-gray-300 leading-relaxed">
                                {dream.analysis_data.interpretation}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

// ============================================
// Main Profile Page
// ============================================

export default function ProfilePage() {
    const router = useRouter();
    const { user, isLoading: authLoading, signOut, getToken } = useAuth();

    const [activeTab, setActiveTab] = useState<"history" | "settings">("history");
    const [dreams, setDreams] = useState<DreamHistoryItem[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(false);
    const [historyError, setHistoryError] = useState<string | null>(null);

    // Profile form state
    const [profile, setProfile] = useState<UserProfile>({
        display_name: "",
        birthdate: "",
        gender: ""
    });
    const [isSavingProfile, setIsSavingProfile] = useState(false);
    const [profileMessage, setProfileMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    // Password change state
    const [passwords, setPasswords] = useState({
        current: "",
        new: "",
        confirm: ""
    });
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [passwordMessage, setPasswordMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    // Redirect if not logged in
    useEffect(() => {
        if (!authLoading && !user) {
            router.push("/auth");
        }
    }, [user, authLoading, router]);

    // Load user metadata on mount
    useEffect(() => {
        if (user?.user_metadata) {
            setProfile({
                display_name: user.user_metadata.display_name || user.email?.split("@")[0] || "",
                birthdate: user.user_metadata.birthdate || "",
                gender: user.user_metadata.gender || ""
            });
        }
    }, [user]);

    // Fetch dream history
    useEffect(() => {
        async function fetchHistory() {
            if (!user) return;

            setIsLoadingHistory(true);
            setHistoryError(null);

            try {
                const token = await getToken();
                if (!token) {
                    setHistoryError("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
                    return;
                }

                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const response = await fetch(`${apiUrl}/api/dreams/history`, {
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "X-API-Key": process.env.NEXT_PUBLIC_API_SECRET || "",
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    console.error("History API Error:", response.status, errorData);
                    throw new Error(errorData.detail || `Lỗi ${response.status}`);
                }

                const data = await response.json();
                setDreams(data);
            } catch (error: any) {
                console.error("Error fetching history:", error);
                setHistoryError(error.message || "Không thể tải lịch sử. Vui lòng thử lại.");
            } finally {
                setIsLoadingHistory(false);
            }
        }

        if (activeTab === "history") {
            fetchHistory();
        }
    }, [user, activeTab, getToken]);

    // Handle profile save
    const handleSaveProfile = async () => {
        setIsSavingProfile(true);
        setProfileMessage(null);

        try {
            const { error } = await supabase.auth.updateUser({
                data: {
                    display_name: profile.display_name,
                    birthdate: profile.birthdate,
                    gender: profile.gender
                }
            });

            if (error) throw error;

            setProfileMessage({ type: "success", text: "Đã lưu thông tin thành công!" });
        } catch (error: any) {
            console.error("Error saving profile:", error);
            setProfileMessage({ type: "error", text: error.message || "Không thể lưu thông tin" });
        } finally {
            setIsSavingProfile(false);
        }
    };

    // Handle password change
    const handleChangePassword = async () => {
        setPasswordMessage(null);

        if (passwords.new !== passwords.confirm) {
            setPasswordMessage({ type: "error", text: "Mật khẩu xác nhận không khớp" });
            return;
        }

        if (passwords.new.length < 6) {
            setPasswordMessage({ type: "error", text: "Mật khẩu mới phải có ít nhất 6 ký tự" });
            return;
        }

        setIsChangingPassword(true);

        try {
            const { error } = await supabase.auth.updateUser({
                password: passwords.new
            });

            if (error) throw error;

            setPasswordMessage({ type: "success", text: "Đã đổi mật khẩu thành công!" });
            setPasswords({ current: "", new: "", confirm: "" });
        } catch (error: any) {
            console.error("Error changing password:", error);
            setPasswordMessage({ type: "error", text: error.message || "Không thể đổi mật khẩu" });
        } finally {
            setIsChangingPassword(false);
        }
    };

    // Handle logout
    const handleLogout = async () => {
        await signOut();
        router.push("/");
    };

    // Loading state
    if (authLoading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    // Not logged in (redirect will happen)
    if (!user) return null;

    return (
        <div className="min-h-screen bg-slate-950">
            {/* Background */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-900/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-900/10 rounded-full blur-[120px]" />
            </div>

            <div className="relative z-10 max-w-2xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <button
                        onClick={() => router.push("/")}
                        className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-400" />
                    </button>
                    <h1 className="text-2xl font-bold text-white">Hồ sơ cá nhân</h1>
                </div>

                {/* User Info Card */}
                <div className="p-6 bg-gradient-to-br from-purple-900/20 to-cyan-900/20 border border-white/10 rounded-2xl mb-6">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                            <User className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">
                                {profile.display_name || user.email?.split("@")[0]}
                            </h2>
                            <p className="text-sm text-gray-400">{user.email}</p>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setActiveTab("history")}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "history"
                            ? "bg-purple-600 text-white"
                            : "bg-white/5 text-gray-400 hover:bg-white/10"
                            }`}
                    >
                        <History className="w-4 h-4" />
                        <span>Lịch sử</span>
                    </button>
                    <button
                        onClick={() => setActiveTab("settings")}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${activeTab === "settings"
                            ? "bg-purple-600 text-white"
                            : "bg-white/5 text-gray-400 hover:bg-white/10"
                            }`}
                    >
                        <Settings className="w-4 h-4" />
                        <span>Cài đặt</span>
                    </button>
                </div>

                {/* Tab Content */}
                <AnimatePresence mode="wait">
                    {activeTab === "history" && (
                        <motion.div
                            key="history"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                        >
                            <div className="flex items-center gap-2 mb-4">
                                <BookOpen className="w-5 h-5 text-purple-400" />
                                <h3 className="text-lg font-medium text-white">Nhật ký giấc mơ</h3>
                            </div>

                            {isLoadingHistory ? (
                                <div className="flex items-center justify-center py-12">
                                    <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                                    <span className="ml-2 text-gray-400">Đang tải...</span>
                                </div>
                            ) : historyError ? (
                                <div className="text-center py-12">
                                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                                    <p className="text-red-400 mb-4">{historyError}</p>
                                    <div className="flex gap-3 justify-center">
                                        <button
                                            onClick={() => {
                                                setHistoryError(null);
                                                setActiveTab("history"); // Trigger re-fetch
                                            }}
                                            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
                                        >
                                            Thử lại
                                        </button>
                                        <button
                                            onClick={async () => {
                                                await signOut();
                                                router.push("/auth");
                                            }}
                                            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-gray-300 rounded-lg transition-colors"
                                        >
                                            Đăng nhập lại
                                        </button>
                                    </div>
                                </div>
                            ) : dreams.length === 0 ? (
                                <div className="text-center py-12">
                                    <Moon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                                    <p className="text-gray-400 mb-2">Chưa có giấc mơ nào được lưu</p>
                                    <p className="text-sm text-gray-500">
                                        Đăng nhập và giải mã giấc mơ để bắt đầu lưu trữ
                                    </p>
                                    <button
                                        onClick={() => router.push("/")}
                                        className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
                                    >
                                        Giải mã giấc mơ
                                    </button>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {dreams.map((dream) => (
                                        <DreamCard key={dream.id} dream={dream} />
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    )}

                    {activeTab === "settings" && (
                        <motion.div
                            key="settings"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            {/* ==================== PROFILE INFO SECTION ==================== */}
                            <div className="p-5 bg-slate-900/50 border border-white/10 rounded-xl">
                                <div className="flex items-center gap-2 mb-4">
                                    <User className="w-5 h-5 text-cyan-400" />
                                    <h3 className="text-lg font-medium text-white">Thông tin cá nhân</h3>
                                </div>

                                <div className="space-y-4">
                                    {/* Display Name */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Tên hiển thị
                                        </label>
                                        <input
                                            type="text"
                                            value={profile.display_name}
                                            onChange={(e) => setProfile({ ...profile, display_name: e.target.value })}
                                            placeholder="Nhập tên của bạn"
                                            className="w-full px-4 py-3 bg-slate-800 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                                        />
                                    </div>

                                    {/* Birthdate */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            <Calendar className="w-4 h-4 inline mr-2" />
                                            Ngày sinh
                                        </label>
                                        <input
                                            type="date"
                                            value={profile.birthdate}
                                            onChange={(e) => setProfile({ ...profile, birthdate: e.target.value })}
                                            className="w-full px-4 py-3 bg-slate-800 border border-white/10 rounded-lg text-gray-100 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                                        />
                                    </div>

                                    {/* Gender */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            <Users className="w-4 h-4 inline mr-2" />
                                            Giới tính
                                        </label>
                                        <select
                                            value={profile.gender}
                                            onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                                            className="w-full px-4 py-3 bg-slate-800 border border-white/10 rounded-lg text-gray-100 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none"
                                        >
                                            <option value="">Chọn giới tính</option>
                                            <option value="male">Nam</option>
                                            <option value="female">Nữ</option>
                                            <option value="other">Khác</option>
                                        </select>
                                    </div>

                                    {/* Profile Message */}
                                    {profileMessage && (
                                        <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${profileMessage.type === "success"
                                            ? "bg-green-900/30 border border-green-500/30 text-green-300"
                                            : "bg-red-900/30 border border-red-500/30 text-red-300"
                                            }`}>
                                            {profileMessage.type === "success" ? (
                                                <CheckCircle className="w-4 h-4" />
                                            ) : (
                                                <AlertCircle className="w-4 h-4" />
                                            )}
                                            {profileMessage.text}
                                        </div>
                                    )}

                                    {/* Save Profile Button */}
                                    <button
                                        onClick={handleSaveProfile}
                                        disabled={isSavingProfile}
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg transition-colors"
                                    >
                                        {isSavingProfile ? (
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                        ) : (
                                            <Save className="w-5 h-5" />
                                        )}
                                        <span>Lưu thông tin</span>
                                    </button>
                                </div>
                            </div>

                            {/* ==================== CHANGE PASSWORD SECTION ==================== */}
                            <div className="p-5 bg-slate-900/50 border border-white/10 rounded-xl">
                                <div className="flex items-center gap-2 mb-4">
                                    <Lock className="w-5 h-5 text-yellow-400" />
                                    <h3 className="text-lg font-medium text-white">Đổi mật khẩu</h3>
                                </div>

                                <div className="space-y-4">
                                    {/* New Password */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Mật khẩu mới
                                        </label>
                                        <input
                                            type="password"
                                            value={passwords.new}
                                            onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                                            placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)"
                                            className="w-full px-4 py-3 bg-slate-800 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 focus:border-yellow-500/50 focus:ring-2 focus:ring-yellow-500/20 focus:outline-none"
                                        />
                                    </div>

                                    {/* Confirm Password */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Xác nhận mật khẩu
                                        </label>
                                        <input
                                            type="password"
                                            value={passwords.confirm}
                                            onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                                            placeholder="Nhập lại mật khẩu mới"
                                            className="w-full px-4 py-3 bg-slate-800 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 focus:border-yellow-500/50 focus:ring-2 focus:ring-yellow-500/20 focus:outline-none"
                                        />
                                    </div>

                                    {/* Password Message */}
                                    {passwordMessage && (
                                        <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${passwordMessage.type === "success"
                                            ? "bg-green-900/30 border border-green-500/30 text-green-300"
                                            : "bg-red-900/30 border border-red-500/30 text-red-300"
                                            }`}>
                                            {passwordMessage.type === "success" ? (
                                                <CheckCircle className="w-4 h-4" />
                                            ) : (
                                                <AlertCircle className="w-4 h-4" />
                                            )}
                                            {passwordMessage.text}
                                        </div>
                                    )}

                                    {/* Change Password Button */}
                                    <button
                                        onClick={handleChangePassword}
                                        disabled={isChangingPassword || !passwords.new || !passwords.confirm}
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 text-white rounded-lg transition-colors"
                                    >
                                        {isChangingPassword ? (
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                        ) : (
                                            <Lock className="w-5 h-5" />
                                        )}
                                        <span>Đổi mật khẩu</span>
                                    </button>
                                </div>
                            </div>

                            {/* ==================== ACCOUNT INFO SECTION ==================== */}
                            <div className="p-5 bg-slate-900/50 border border-white/10 rounded-xl">
                                <div className="flex items-center gap-2 mb-4">
                                    <Settings className="w-5 h-5 text-gray-400" />
                                    <h3 className="text-lg font-medium text-white">Thông tin tài khoản</h3>
                                </div>

                                <div className="space-y-3 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Email:</span>
                                        <span className="text-gray-200">{user.email}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Ngày tạo:</span>
                                        <span className="text-gray-200">
                                            {user.created_at
                                                ? new Date(user.created_at).toLocaleDateString("vi-VN")
                                                : "Không rõ"}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* ==================== LOGOUT BUTTON ==================== */}
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center justify-center gap-2 p-4 bg-red-900/20 border border-red-500/30 text-red-400 rounded-xl hover:bg-red-900/30 transition-colors"
                            >
                                <LogOut className="w-5 h-5" />
                                <span>Đăng xuất</span>
                            </button>

                            {/* App Info */}
                            <div className="pt-4 text-center">
                                <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
                                    <Sparkles className="w-4 h-4" />
                                    <span>DreamSight Oracle v1.0</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
