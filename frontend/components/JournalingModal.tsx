"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Save, Sparkles } from "lucide-react";

interface JournalingModalProps {
    isOpen: boolean;
    onClose: () => void;
    prompt: string;
    therapyType: string;
}

/**
 * JournalingModal - Popup for users to write their therapy exercise immediately.
 */
export default function JournalingModal({
    isOpen,
    onClose,
    prompt,
    therapyType,
}: JournalingModalProps) {
    const [text, setText] = useState("");
    const [isSaved, setIsSaved] = useState(false);

    const handleSave = () => {
        // Save to localStorage for persistence
        const journalEntries = JSON.parse(localStorage.getItem("dreamJournal") || "[]");
        journalEntries.push({
            timestamp: new Date().toISOString(),
            therapyType,
            prompt,
            entry: text,
        });
        localStorage.setItem("dreamJournal", JSON.stringify(journalEntries));
        setIsSaved(true);
        setTimeout(() => {
            setIsSaved(false);
            onClose();
            setText("");
        }, 1500);
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full max-w-lg bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl border border-yellow-500/30 shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-yellow-500/20 bg-yellow-500/5">
                            <div className="flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-yellow-400" />
                                <h3 className="text-lg font-bold text-yellow-200">
                                    {therapyType}
                                </h3>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-400" />
                            </button>
                        </div>

                        {/* Prompt */}
                        <div className="p-4 bg-amber-500/5 border-b border-yellow-500/10">
                            <p className="text-sm text-yellow-100 font-medium italic">
                                📝 "{prompt}"
                            </p>
                        </div>

                        {/* Writing Area */}
                        <div className="p-4">
                            <textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                placeholder="Bắt đầu viết tại đây... Đừng suy nghĩ quá nhiều, chỉ cần để dòng suy nghĩ tuôn trào."
                                className="w-full h-48 p-4 bg-slate-800/50 border border-yellow-500/20 rounded-xl text-gray-200 text-sm placeholder:text-gray-500 focus:outline-none focus:border-yellow-500/50 focus:ring-2 focus:ring-yellow-500/20 resize-none"
                                autoFocus
                            />

                            {/* Word count */}
                            <div className="flex items-center justify-between mt-2">
                                <span className="text-xs text-gray-500">
                                    {text.split(/\s+/).filter(Boolean).length} từ
                                </span>
                                <span className="text-xs text-gray-500">
                                    Viết ít nhất 50 từ để thấy hiệu quả
                                </span>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="flex gap-3 p-4 border-t border-yellow-500/10 bg-yellow-500/5">
                            <button
                                onClick={onClose}
                                className="flex-1 py-2 px-4 rounded-xl border border-gray-600 text-gray-400 hover:bg-gray-800 transition-colors"
                            >
                                Để sau
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={text.trim().length < 10}
                                className={`flex-1 py-2 px-4 rounded-xl flex items-center justify-center gap-2 transition-all ${isSaved
                                        ? "bg-green-500 text-white"
                                        : text.trim().length >= 10
                                            ? "bg-gradient-to-r from-yellow-500 to-amber-500 text-black font-medium hover:opacity-90"
                                            : "bg-gray-700 text-gray-500 cursor-not-allowed"
                                    }`}
                            >
                                {isSaved ? (
                                    <>✓ Đã lưu!</>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4" />
                                        Lưu vào nhật ký
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
