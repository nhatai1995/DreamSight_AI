"use client";

import { useMemo } from "react";

/**
 * Trigram definitions: each trigram has 3 lines (bottom to top)
 * true = solid line (Yang ━━━)
 * false = broken line (Yin ━ ━)
 */
const TRIGRAM_LINES: Record<string, [boolean, boolean, boolean]> = {
    // Bát Quái (8 Trigrams)
    "☰": [true, true, true],      // Càn (Trời) - 3 solid
    "☷": [false, false, false],   // Khôn (Đất) - 3 broken
    "☵": [false, true, false],    // Khảm (Nước) - middle solid
    "☲": [true, false, true],     // Ly (Lửa) - middle broken
    "☳": [false, false, true],    // Chấn (Sấm) - top solid
    "☴": [true, true, false],     // Tốn (Gió) - bottom broken
    "☶": [false, false, true],    // Cấn (Núi) - top solid only (actually ☶ is different)
    "☱": [false, true, true],     // Đoài (Đầm) - bottom broken
};

// Alternative names mapping
const TRIGRAM_NAMES: Record<string, string> = {
    "càn": "☰", "trời": "☰", "heaven": "☰",
    "khôn": "☷", "đất": "☷", "earth": "☷",
    "khảm": "☵", "nước": "☵", "water": "☵",
    "ly": "☲", "lửa": "☲", "fire": "☲",
    "chấn": "☳", "sấm": "☳", "thunder": "☳",
    "tốn": "☴", "gió": "☴", "wind": "☴",
    "cấn": "☶", "núi": "☶", "mountain": "☶",
    "đoài": "☱", "đầm": "☱", "lake": "☱",
};

interface HexagramVisualProps {
    /** Structure string like "Thượng Khảm (Nước ☵) - Hạ Càn (Trời ☰)" */
    structure: string;
    /** Size variant */
    size?: "sm" | "md" | "lg";
    /** Show as background watermark */
    asBackground?: boolean;
    /** Custom className */
    className?: string;
}

/**
 * Parses the structure string to extract upper and lower trigram symbols.
 */
function parseTrigramSymbols(structure: string): { upper: string | null; lower: string | null } {
    // Try to find Unicode trigram symbols directly
    const symbols = structure.match(/[☰☱☲☳☴☵☶☷]/g);

    if (symbols && symbols.length >= 2) {
        return { upper: symbols[0], lower: symbols[1] };
    }

    // Fallback: try to match names
    const upperMatch = structure.match(/thượng\s+(\w+)/i);
    const lowerMatch = structure.match(/hạ\s+(\w+)/i);

    const upperName = upperMatch?.[1]?.toLowerCase();
    const lowerName = lowerMatch?.[1]?.toLowerCase();

    return {
        upper: upperName ? (TRIGRAM_NAMES[upperName] || null) : null,
        lower: lowerName ? (TRIGRAM_NAMES[lowerName] || null) : null,
    };
}

/**
 * Single line component (solid or broken)
 */
function HexagramLine({ solid, size }: { solid: boolean; size: "sm" | "md" | "lg" }) {
    const sizeStyles = {
        sm: { width: "32px", height: "4px", gap: "3px" },
        md: { width: "48px", height: "6px", gap: "4px" },
        lg: { width: "64px", height: "8px", gap: "6px" },
    };

    const s = sizeStyles[size];

    if (solid) {
        // Solid line (Yang)
        return (
            <div
                className="bg-emerald-400 rounded-sm shadow-[0_0_8px_rgba(52,211,153,0.5)]"
                style={{ width: s.width, height: s.height }}
            />
        );
    }

    // Broken line (Yin)
    return (
        <div className="flex justify-between" style={{ width: s.width }}>
            <div
                className="bg-emerald-400 rounded-sm shadow-[0_0_8px_rgba(52,211,153,0.5)]"
                style={{ width: `calc(${s.width} / 2 - ${s.gap})`, height: s.height }}
            />
            <div
                className="bg-emerald-400 rounded-sm shadow-[0_0_8px_rgba(52,211,153,0.5)]"
                style={{ width: `calc(${s.width} / 2 - ${s.gap})`, height: s.height }}
            />
        </div>
    );
}

/**
 * Visual Hexagram Component
 * Renders the 6 lines of an I Ching hexagram based on upper and lower trigrams.
 */
export default function HexagramVisual({
    structure,
    size = "md",
    asBackground = false,
    className = "",
}: HexagramVisualProps) {
    const { upper, lower } = useMemo(() => parseTrigramSymbols(structure), [structure]);

    // Get the lines for each trigram (bottom to top within each trigram)
    const upperLines = upper ? TRIGRAM_LINES[upper] : [true, true, true];
    const lowerLines = lower ? TRIGRAM_LINES[lower] : [true, true, true];

    // Combine: hexagram is read bottom to top
    // Lines 1-3 (bottom) = lower trigram, Lines 4-6 (top) = upper trigram
    // But we render top to bottom, so reverse the order
    const allLines = [
        ...upperLines.slice().reverse(), // Top 3 lines (upper trigram, reversed)
        ...lowerLines.slice().reverse(), // Bottom 3 lines (lower trigram, reversed)
    ];

    const gapSize = size === "sm" ? "gap-1" : size === "md" ? "gap-1.5" : "gap-2";

    if (asBackground) {
        return (
            <div
                className={`absolute right-4 top-1/2 -translate-y-1/2 opacity-10 pointer-events-none ${className}`}
            >
                <div className={`flex flex-col items-center ${gapSize}`}>
                    {allLines.map((solid, i) => (
                        <HexagramLine key={i} solid={solid} size="lg" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className={`flex flex-col items-center ${gapSize} ${className}`}>
            {allLines.map((solid, i) => (
                <HexagramLine key={i} solid={solid} size={size} />
            ))}
        </div>
    );
}
