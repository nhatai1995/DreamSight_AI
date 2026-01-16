"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Sparkles, Moon, RefreshCw, BookOpen, Image as ImageIcon,
    Brain, Compass, BookHeart, PenLine  // Icons for the three lenses
} from "lucide-react";
import dreamApi, { ApiException } from "@/lib/api";
import { TriangleAnalysisResponse } from "@/types";
import TypewriterText from "./TypewriterText";
import HexagramVisual from "./HexagramVisual";
import TarotCard from "./TarotCard";
import JournalingModal from "./JournalingModal";
import CosmicTicket from "./CosmicTicket";

export default function DreamForm() {
    const [dreamText, setDreamText] = useState("");
    const [result, setResult] = useState<TriangleAnalysisResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isJournalingOpen, setIsJournalingOpen] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);
        setResult(null);

        try {
            const response = await dreamApi.analyzeTriangle({ user_dream: dreamText });
            setResult(response);
        } catch (err) {
            if (err instanceof ApiException) {
                setError(err.detail || err.message);
            } else {
                setError("The oracle is silent right now. Please try again later.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleReset = () => {
        setDreamText("");
        setResult(null);
        setError(null);
    };

    return (
        <div className="w-full max-w-6xl mx-auto px-4">
            <AnimatePresence mode="wait">
                {!result ? (
                    <motion.div
                        key="input-form"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.5 }}
                        className="w-full max-w-2xl mx-auto"
                    >
                        <form onSubmit={handleSubmit} className="space-y-6 relative">
                            {/* Glassmorphism Card */}
                            <div className="p-1 rounded-2xl bg-gradient-to-b from-purple-500/20 to-cyan-500/20 backdrop-blur-md border border-white/10 shadow-[0_0_50px_-12px_rgba(168,85,247,0.4)]">
                                <div className="bg-slate-950/80 rounded-xl p-6 sm:p-8">
                                    <div className="mb-6 flex items-center gap-3 text-purple-300">
                                        <Moon className="w-5 h-5" />
                                        <span className="text-sm font-medium tracking-widest uppercase">
                                            Consult the Oracle
                                        </span>
                                    </div>

                                    <div className="relative group">
                                        <textarea
                                            value={dreamText}
                                            onChange={(e) => setDreamText(e.target.value)}
                                            placeholder="Whisper your dream here... (e.g., I was floating in a void of neon lights)"
                                            className="w-full h-40 bg-slate-900/50 text-gray-100 p-4 rounded-xl border border-white/10 focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 focus:outline-none transition-all resize-none placeholder-gray-500"
                                            minLength={10}
                                            maxLength={5000}
                                            required
                                        />

                                        {/* Glowing corner accents */}
                                        <div className="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-cyan-400/50 rounded-tl-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                                        <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-purple-400/50 rounded-br-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>

                                    <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
                                        <span>{dreamText.length}/5000 runes</span>
                                        {dreamText.length > 0 && dreamText.length < 10 && (
                                            <span className="text-red-400">Dream too short...</span>
                                        )}
                                    </div>

                                    <motion.button
                                        whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(168,85,247,0.4)" }}
                                        whileTap={{ scale: 0.98 }}
                                        disabled={isLoading || dreamText.length < 10}
                                        type="submit"
                                        className="w-full mt-8 py-4 px-6 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl font-bold text-white tracking-wide shadow-lg disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
                                    >
                                        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                                        <div className="relative flex items-center justify-center gap-2">
                                            {isLoading ? (
                                                <>
                                                    <RefreshCw className="w-5 h-5 animate-spin" />
                                                    <span>Divining...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Sparkles className="w-5 h-5" />
                                                    <span>Reveal Meaning</span>
                                                </>
                                            )}
                                        </div>
                                    </motion.button>
                                </div>
                            </div>

                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 bg-red-900/30 border border-red-500/30 rounded-xl text-red-200 text-center text-sm backdrop-blur-sm"
                                >
                                    {error}
                                </motion.div>
                            )}
                        </form>
                    </motion.div>
                ) : (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-8 w-full"
                    >
                        {/* Three Lenses Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                            {/* Psychology Lens - Digital Profile Design */}
                            <motion.div
                                initial={{ y: 50, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.1 }}
                                className="p-px rounded-2xl bg-gradient-to-br from-blue-500/30 to-purple-500/30 md:col-span-3"
                            >
                                <div className="bg-slate-950/90 rounded-2xl p-6 border border-white/5 backdrop-blur-xl">
                                    <div className="flex items-center gap-3 mb-4 border-b border-white/10 pb-3">
                                        <Brain className="w-6 h-6 text-blue-400" />
                                        <h3 className="text-lg font-bold text-blue-300">Phân Tích Tâm Lý Sâu</h3>
                                    </div>

                                    {/* Layer 1: Mood Bar */}
                                    <div className="mb-5">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-medium text-blue-200">
                                                {result.analysis.psychology.core_emotion}
                                            </span>
                                            <span className="text-xs text-gray-400">
                                                {result.analysis.psychology.emotion_intensity}%
                                            </span>
                                        </div>
                                        <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${result.analysis.psychology.emotion_intensity}%` }}
                                                transition={{ duration: 1, delay: 0.5 }}
                                                className={`h-full rounded-full ${result.analysis.psychology.emotion_intensity > 70
                                                    ? "bg-gradient-to-r from-red-500 to-orange-500"
                                                    : result.analysis.psychology.emotion_intensity > 40
                                                        ? "bg-gradient-to-r from-yellow-500 to-orange-500"
                                                        : "bg-gradient-to-r from-green-500 to-cyan-500"
                                                    }`}
                                            />
                                        </div>
                                    </div>

                                    {/* Layer 2 & 3: Freud & Jung Analysis */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        {/* Freudian Conflict */}
                                        <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="text-xs text-blue-400 uppercase tracking-wider">🔮 Dục Vọng Ẩn Giấu (Id)</span>
                                            </div>
                                            <p className="text-sm text-blue-100 mb-3">{result.analysis.psychology.hidden_desire}</p>
                                            <div className="pt-3 border-t border-blue-500/20">
                                                <span className="text-xs text-purple-400 uppercase tracking-wider">⚔️ Xung Đột Nội Tâm</span>
                                                <p className="text-sm text-purple-100 mt-1">{result.analysis.psychology.inner_conflict}</p>
                                            </div>
                                        </div>

                                        {/* The Shadow Card - Dark themed for emphasis */}
                                        <div className="p-4 bg-slate-900 border-2 border-purple-500/40 rounded-lg relative overflow-hidden">
                                            <div className="absolute top-0 right-0 w-20 h-20 bg-purple-500/10 rounded-full blur-2xl" />
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="text-xs text-purple-400 uppercase tracking-wider font-bold">
                                                    👤 {result.analysis.psychology.archetype}
                                                </span>
                                            </div>
                                            <div className="bg-purple-950/50 border border-purple-500/30 rounded-lg p-3 mt-2">
                                                <p className="text-xs text-purple-300 uppercase mb-1">Phần bạn đang chối bỏ:</p>
                                                <p className="text-sm text-purple-100 italic">"{result.analysis.psychology.shadow_aspect}"</p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Layer 4: Prescription Card */}
                                    <div className="p-4 bg-gradient-to-r from-amber-500/10 to-yellow-500/10 border border-yellow-500/30 rounded-lg">
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-lg">📋</span>
                                                <span className="text-sm font-bold text-yellow-400 uppercase tracking-wider">
                                                    Toa Thuốc Tinh Thần ({result.analysis.psychology.therapy_type})
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-2 p-3 bg-yellow-500/10 rounded-lg border-l-4 border-yellow-500 mb-3">
                                            <input type="checkbox" className="mt-1 accent-yellow-500" />
                                            <p className="text-sm text-yellow-100 font-medium">
                                                {result.analysis.psychology.actionable_exercise}
                                            </p>
                                        </div>
                                        {/* Start Journaling Button */}
                                        <button
                                            onClick={() => setIsJournalingOpen(true)}
                                            className="w-full py-2 px-4 rounded-lg bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border border-yellow-500/40 text-yellow-300 text-sm font-medium hover:from-yellow-500/30 hover:to-amber-500/30 transition-all flex items-center justify-center gap-2"
                                        >
                                            <PenLine className="w-4 h-4" />
                                            Bắt đầu viết ngay
                                        </button>
                                    </div>
                                </div>
                            </motion.div>

                            {/* Tarot Lens - Interactive Card */}
                            <motion.div
                                initial={{ y: 50, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.2 }}
                                className="md:col-span-3"
                            >
                                <div className="flex items-center gap-3 mb-4">
                                    <Compass className="w-6 h-6 text-purple-400" />
                                    <h3 className="text-lg font-bold text-purple-300">Tarot - Giải Bài Sâu</h3>
                                </div>
                                <TarotCard tarot={result.analysis.tarot} />
                            </motion.div>

                            {/* I Ching Lens - Detailed */}
                            <motion.div
                                initial={{ y: 50, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.3 }}
                                className="p-px rounded-2xl bg-gradient-to-br from-emerald-500/30 to-transparent md:col-span-3"
                            >
                                <div className="bg-slate-950/90 rounded-2xl p-6 border border-white/5 backdrop-blur-xl relative overflow-hidden">
                                    {/* Background Hexagram Watermark */}
                                    <HexagramVisual
                                        structure={result.analysis.iching.structure}
                                        asBackground={true}
                                        className="opacity-[0.08]"
                                    />

                                    <div className="flex items-center gap-3 mb-4 border-b border-white/10 pb-3">
                                        <BookHeart className="w-6 h-6 text-emerald-400" />
                                        <h3 className="text-lg font-bold text-emerald-300">Kinh Dịch - Chi Tiết</h3>
                                    </div>

                                    {/* Hexagram Header with Visual */}
                                    <div className="mb-4 flex items-center justify-center gap-6">
                                        {/* Visual Hexagram */}
                                        <div className="flex-shrink-0">
                                            <HexagramVisual
                                                structure={result.analysis.iching.structure}
                                                size="md"
                                            />
                                        </div>

                                        {/* Name and Structure */}
                                        <div className="text-center">
                                            <h4 className="text-2xl font-bold text-emerald-200 mb-1">
                                                {result.analysis.iching.hexagram_name}
                                            </h4>
                                            <p className="text-sm text-emerald-400/70">
                                                {result.analysis.iching.structure}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Judgment & Image */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                                            <p className="text-xs text-emerald-400 uppercase tracking-wider mb-1">Lời Thoán</p>
                                            <p className="text-sm text-emerald-200">{result.analysis.iching.judgment_summary}</p>
                                        </div>
                                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                                            <p className="text-xs text-emerald-400 uppercase tracking-wider mb-1">Lời Tượng</p>
                                            <p className="text-sm text-emerald-200">{result.analysis.iching.image_meaning}</p>
                                        </div>
                                    </div>

                                    {/* Specific Advice */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                            <p className="text-xs text-blue-400 uppercase tracking-wider mb-1">💼 Công Việc</p>
                                            <p className="text-sm text-blue-200">{result.analysis.iching.advice_career}</p>
                                        </div>
                                        <div className="p-3 bg-pink-500/10 border border-pink-500/20 rounded-lg">
                                            <p className="text-xs text-pink-400 uppercase tracking-wider mb-1">💕 Tình Cảm</p>
                                            <p className="text-sm text-pink-200">{result.analysis.iching.advice_relationship}</p>
                                        </div>
                                        <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                                            <p className="text-xs text-yellow-400 uppercase tracking-wider mb-1">⚡ Hành Động Ngay</p>
                                            <p className="text-sm text-yellow-200 font-medium">{result.analysis.iching.actionable_step}</p>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        </div>

                        {/* Art Prompt Section */}
                        <motion.div
                            initial={{ y: 30, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.4 }}
                            className="p-px rounded-2xl bg-gradient-to-r from-cyan-500/30 via-purple-500/30 to-pink-500/30"
                        >
                            <div className="bg-slate-950/90 rounded-2xl p-6 border border-white/5 backdrop-blur-xl">
                                <div className="flex items-center gap-3 mb-4">
                                    <ImageIcon className="w-6 h-6 text-cyan-400" />
                                    <h3 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-400">
                                        Dream Visualization Prompt
                                    </h3>
                                </div>
                                <p className="text-gray-400 text-sm italic leading-relaxed">
                                    "{result.analysis.art_prompt}"
                                </p>
                            </div>
                        </motion.div>

                        {/* Cosmic Ticket - Final Synthesis & Lucky Numbers */}
                        <CosmicTicket synthesis={result.analysis.synthesis} />

                        {/* Reset Button */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.8 }}
                            className="flex justify-center"
                        >
                            <button
                                onClick={handleReset}
                                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors px-6 py-3 rounded-xl border border-white/10 hover:border-purple-500/50"
                            >
                                <RefreshCw className="w-4 h-4" />
                                <span>Interpret Another Dream</span>
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Journaling Modal */}
            {result && (
                <JournalingModal
                    isOpen={isJournalingOpen}
                    onClose={() => setIsJournalingOpen(false)}
                    prompt={result.analysis.psychology.actionable_exercise}
                    therapyType={result.analysis.psychology.therapy_type}
                />
            )}
        </div>
    );
}
