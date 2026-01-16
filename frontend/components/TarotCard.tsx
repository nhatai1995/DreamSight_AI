"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TarotDetailed } from "@/types";
import { Sparkles, Flame, Droplets, Wind, Mountain, Stars } from "lucide-react";

interface TarotCardProps {
    tarot: TarotDetailed;
}

/**
 * Get element icon and color based on suit/element
 */
function getElementStyles(element: string) {
    const lower = element.toLowerCase();
    if (lower.includes("lửa") || lower.includes("fire")) {
        return { icon: Flame, color: "text-orange-400", bgColor: "from-orange-500/20 to-red-500/20" };
    }
    if (lower.includes("nước") || lower.includes("water")) {
        return { icon: Droplets, color: "text-cyan-400", bgColor: "from-cyan-500/20 to-blue-500/20" };
    }
    if (lower.includes("gió") || lower.includes("air")) {
        return { icon: Wind, color: "text-sky-400", bgColor: "from-sky-500/20 to-indigo-500/20" };
    }
    if (lower.includes("đất") || lower.includes("earth")) {
        return { icon: Mountain, color: "text-amber-400", bgColor: "from-amber-500/20 to-yellow-500/20" };
    }
    // Spirit / Major Arcana
    return { icon: Stars, color: "text-purple-400", bgColor: "from-purple-500/20 to-pink-500/20" };
}

/**
 * TarotCard Component with 3D Flip Animation
 * Shows card back initially, flips on click to reveal the reading.
 */
export default function TarotCard({ tarot }: TarotCardProps) {
    const [isFlipped, setIsFlipped] = useState(false);
    const elementStyles = getElementStyles(tarot.element);
    const ElementIcon = elementStyles.icon;

    return (
        <div className="perspective-1000 w-full">
            <motion.div
                className="relative w-full cursor-pointer"
                style={{ transformStyle: "preserve-3d" }}
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
                onClick={() => setIsFlipped(!isFlipped)}
            >
                {/* Card Back (Initial State) */}
                <motion.div
                    className={`w-full p-6 rounded-2xl border-2 ${isFlipped ? "hidden" : "block"
                        } bg-gradient-to-br from-purple-900/90 to-indigo-900/90 border-purple-500/30`}
                    style={{ backfaceVisibility: "hidden" }}
                >
                    <div className="flex flex-col items-center justify-center min-h-[280px] text-center">
                        {/* Mystical Back Pattern */}
                        <div className="relative">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-0 w-24 h-24 border-2 border-purple-400/30 rounded-full"
                            />
                            <motion.div
                                animate={{ rotate: -360 }}
                                transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-2 w-20 h-20 border border-pink-400/20 rounded-full"
                            />
                            <Sparkles className="w-24 h-24 text-purple-300 relative z-10" />
                        </div>
                        <motion.p
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="mt-6 text-purple-200 text-sm font-medium"
                        >
                            Bấm để lật bài...
                        </motion.p>
                        <p className="mt-2 text-purple-400/60 text-xs">
                            ~ Tarot Reading ~
                        </p>
                    </div>
                </motion.div>

                {/* Card Front (Revealed State) */}
                <motion.div
                    className={`w-full rounded-2xl border-2 overflow-hidden ${isFlipped ? "block" : "hidden"
                        } ${tarot.is_reversed
                            ? "border-red-500/50 bg-gradient-to-br from-red-950/90 to-purple-950/90"
                            : "border-yellow-500/50 bg-gradient-to-br from-yellow-950/90 to-amber-950/90"
                        }`}
                    style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
                >
                    <div className="p-6">
                        {/* Card Header */}
                        <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-3">
                            <div className="flex items-center gap-2">
                                <ElementIcon className={`w-5 h-5 ${elementStyles.color}`} />
                                <span className={`text-xs font-medium ${elementStyles.color}`}>
                                    {tarot.suit}
                                </span>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full ${tarot.is_reversed
                                ? "bg-red-500/20 text-red-300"
                                : "bg-yellow-500/20 text-yellow-300"
                                }`}>
                                {tarot.is_reversed ? "↓ Ngược" : "↑ Xuôi"}
                            </span>
                        </div>

                        {/* Card Name - Always upright for readability */}
                        <div className="text-center mb-4">
                            <h3 className={`text-2xl font-bold ${tarot.is_reversed ? "text-red-200" : "text-yellow-200"
                                }`}>
                                {tarot.card_name}
                            </h3>
                            <p className="text-xs text-gray-400 mt-1">
                                Card #{tarot.card_number}
                            </p>
                        </div>

                        {/* Layer 1: Orientation Reason */}
                        <div className="mb-3 p-3 bg-white/5 rounded-lg">
                            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                                Lý do chọn chiều
                            </p>
                            <p className="text-sm text-gray-200">{tarot.orientation_reason}</p>
                        </div>

                        {/* Layer 2: Element Analysis */}
                        <div className={`mb-3 p-3 bg-gradient-to-r ${elementStyles.bgColor} rounded-lg border border-white/10`}>
                            <p className="text-xs uppercase tracking-wider mb-1" style={{ color: elementStyles.color.replace("text-", "") }}>
                                🔥 Năng lượng: {tarot.element}
                            </p>
                            <p className="text-sm text-gray-200">{tarot.energy_analysis}</p>
                        </div>

                        {/* Layer 3: Visual Bridge */}
                        <div className="mb-3 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                            <p className="text-xs text-indigo-400 uppercase tracking-wider mb-1">
                                🔗 Cầu nối hình ảnh
                            </p>
                            <p className="text-sm text-indigo-200 italic">"{tarot.visual_bridge}"</p>
                        </div>

                        {/* Prediction */}
                        <div className={`p-3 rounded-lg ${tarot.is_reversed
                            ? "bg-red-500/10 border border-red-500/30"
                            : "bg-yellow-500/10 border border-yellow-500/30"
                            }`}>
                            <p className={`text-xs uppercase tracking-wider mb-1 ${tarot.is_reversed ? "text-red-400" : "text-yellow-400"
                                }`}>
                                ✨ Lời tiên tri
                            </p>
                            <p className={`text-sm font-medium ${tarot.is_reversed ? "text-red-200" : "text-yellow-200"
                                }`}>
                                {tarot.prediction}
                            </p>
                        </div>

                        {/* Tap to flip back hint */}
                        <p className="text-center text-gray-500 text-xs mt-4">
                            Bấm để xem lại mặt sau
                        </p>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
}
