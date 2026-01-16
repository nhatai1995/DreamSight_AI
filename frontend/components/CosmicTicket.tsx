"use client";

import { motion } from "framer-motion";
import { FinalSynthesis } from "@/types";
import { Sparkles, Star, Quote } from "lucide-react";

interface CosmicTicketProps {
    synthesis: FinalSynthesis;
}

/**
 * Get color scheme based on number source
 */
function getNumberColor(source: string) {
    const lower = source.toLowerCase();
    if (lower.includes("tarot") || lower.includes("lá bài")) {
        return {
            bg: "from-purple-500/20 to-violet-500/20",
            border: "border-purple-500/50",
            text: "text-purple-300",
            glow: "shadow-purple-500/30",
            label: "TAROT"
        };
    }
    if (lower.includes("quẻ") || lower.includes("kinh dịch") || lower.includes("i ching")) {
        return {
            bg: "from-teal-500/20 to-cyan-500/20",
            border: "border-teal-500/50",
            text: "text-teal-300",
            glow: "shadow-teal-500/30",
            label: "KINH DỊCH"
        };
    }
    // Vietnamese Folk / Sổ Mơ
    return {
        bg: "from-yellow-500/20 to-amber-500/20",
        border: "border-yellow-500/50",
        text: "text-yellow-300",
        glow: "shadow-yellow-500/30",
        label: "SỔ MƠ"
    };
}

/**
 * CosmicTicket Component - "Tấm Vé Thông Hành Vũ Trụ"
 * Displays final synthesis message and 3 lucky numbers in glowing circles.
 */
export default function CosmicTicket({ synthesis }: CosmicTicketProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="relative overflow-hidden"
        >
            {/* Cosmic Background Effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-950/50 via-purple-950/30 to-slate-950/50 rounded-3xl" />
            <div className="absolute top-0 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-1/4 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />

            <div className="relative p-8 rounded-3xl border border-white/10 backdrop-blur-sm">
                {/* Header */}
                <div className="flex items-center justify-center gap-3 mb-6">
                    <Star className="w-5 h-5 text-yellow-400" />
                    <h3 className="text-xl font-bold bg-gradient-to-r from-purple-300 via-pink-300 to-yellow-300 bg-clip-text text-transparent">
                        Vé Thông Hành Vũ Trụ
                    </h3>
                    <Star className="w-5 h-5 text-yellow-400" />
                </div>

                {/* Core Message - Handwriting Style */}
                <div className="mb-8 p-6 bg-white/5 rounded-2xl border border-white/10 relative">
                    <Quote className="absolute top-3 left-3 w-6 h-6 text-purple-400/50" />
                    <Quote className="absolute bottom-3 right-3 w-6 h-6 text-purple-400/50 rotate-180" />
                    <p className="text-center text-lg text-gray-200 italic leading-relaxed px-6 font-serif">
                        "{synthesis.core_message}"
                    </p>
                </div>

                {/* Lucky Numbers */}
                <div className="mb-4">
                    <p className="text-center text-sm text-gray-400 uppercase tracking-wider mb-4">
                        ✨ Con Số May Mắn ✨
                    </p>
                    <div className="grid grid-cols-3 gap-4">
                        {synthesis.numbers.map((num, i) => {
                            const colors = getNumberColor(num.source);
                            return (
                                <motion.div
                                    key={i}
                                    initial={{ scale: 0, rotate: -180 }}
                                    animate={{ scale: 1, rotate: 0 }}
                                    transition={{ delay: 0.7 + i * 0.15, type: "spring", stiffness: 200 }}
                                    className="flex flex-col items-center"
                                >
                                    {/* Glowing Number Container - Dynamic size based on content */}
                                    <div className={`relative min-w-20 min-h-20 px-4 py-3 rounded-2xl bg-gradient-to-br ${colors.bg} ${colors.border} border-2 flex items-center justify-center shadow-lg ${colors.glow} shadow-xl mb-3`}>
                                        {/* Glow effect */}
                                        <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${colors.bg} blur-md opacity-50`} />
                                        <span className={`relative font-bold ${colors.text} ${num.number.length > 8 ? 'text-sm' :
                                                num.number.length > 4 ? 'text-lg' : 'text-2xl'
                                            } text-center whitespace-nowrap`}>
                                            {num.number}
                                        </span>
                                    </div>

                                    {/* Label */}
                                    <span className={`text-xs font-bold ${colors.text} uppercase tracking-wider mb-1`}>
                                        {colors.label}
                                    </span>

                                    {/* Source */}
                                    <p className="text-xs text-gray-400 text-center line-clamp-2 px-2">
                                        {num.source}
                                    </p>

                                    {/* Meaning Tooltip */}
                                    <p className="text-xs text-gray-500 text-center mt-1 italic line-clamp-2">
                                        {num.meaning}
                                    </p>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>

                {/* Decorative Footer */}
                <div className="flex items-center justify-center gap-2 pt-4 border-t border-white/10">
                    <Sparkles className="w-4 h-4 text-purple-400/50" />
                    <span className="text-xs text-gray-500">Powered by Ancient Wisdom & Modern AI</span>
                    <Sparkles className="w-4 h-4 text-purple-400/50" />
                </div>
            </div>
        </motion.div>
    );
}
