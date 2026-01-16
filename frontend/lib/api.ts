/**
 * API Client for the Dream Interpretation Backend.
 * All fetch logic is centralized here - components should not make direct fetch calls.
 * 
 * Security:
 * - X-API-Key: Required for ALL requests (client verification)
 * - Authorization: Optional Bearer token for authenticated users
 */

import type {
    DreamInterpretationRequest,
    DreamInterpretationResponse,
    DreamSearchRequest,
    DreamSearchResponse,
    CommonSymbolsResponse,
    HealthCheckResponse,
    ApiError,
    AnalyzeDreamRequest,
    AnalyzeDreamResponse,
    TriangleAnalysisRequest,
    TriangleAnalysisResponse,
} from "@/types";
import { getAccessToken } from "@/lib/supabase";

// ============================================
// Environment Variables (Next.js uses NEXT_PUBLIC_ prefix)
// ============================================
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_SECRET_KEY = process.env.NEXT_PUBLIC_API_SECRET || "";

// Validate configuration
if (!API_SECRET_KEY) {
    console.warn("⚠️ NEXT_PUBLIC_API_SECRET is not set. API calls will fail with 403.");
}

/**
 * Custom error class for API errors.
 */
export class ApiException extends Error {
    public statusCode: number;
    public detail?: string;

    constructor(error: ApiError) {
        super(error.error || error.detail || "Unknown error");
        this.name = "ApiException";
        this.statusCode = error.status_code;
        this.detail = error.detail;
    }

    /**
     * Check if this is an API key error (403 Forbidden)
     */
    isApiKeyError(): boolean {
        return this.statusCode === 403;
    }

    /**
     * Check if this is an auth token error (401 Unauthorized)
     */
    isAuthError(): boolean {
        return this.statusCode === 401;
    }

    /**
     * Check if this is a rate limit error (429 Too Many Requests)
     */
    isRateLimitError(): boolean {
        return this.statusCode === 429;
    }
}

/**
 * Build common headers for all API requests.
 * Always includes X-API-Key for client verification.
 */
function buildBaseHeaders(): HeadersInit {
    const headers: HeadersInit = {
        "Content-Type": "application/json",
    };

    // Always include API key (required by backend)
    if (API_SECRET_KEY) {
        headers["X-API-Key"] = API_SECRET_KEY;
    }

    return headers;
}

/**
 * Generic fetch wrapper with error handling.
 * Includes X-API-Key but NOT auth token.
 */
async function apiFetch<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const config: RequestInit = {
        ...options,
        headers: {
            ...buildBaseHeaders(),
            ...options.headers,
        },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        let errorData: ApiError;
        try {
            const json = await response.json();
            errorData = {
                error: json.detail || json.message || "Request failed",
                status_code: response.status,
                detail: json.detail,
            };
        } catch {
            errorData = {
                error: `HTTP ${response.status}: ${response.statusText}`,
                status_code: response.status,
            };
        }
        throw new ApiException(errorData);
    }

    return response.json();
}

/**
 * Authenticated fetch wrapper.
 * Includes X-API-Key (always) and Authorization Bearer token (if logged in).
 */
async function apiFetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    // Get auth token (null if not logged in)
    const token = await getAccessToken();

    const headers: HeadersInit = {
        ...buildBaseHeaders(),
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
    };

    const config: RequestInit = {
        ...options,
        headers,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        let errorData: ApiError;
        try {
            const json = await response.json();
            errorData = {
                error: json.detail || json.message || "Request failed",
                status_code: response.status,
                detail: json.detail,
            };
        } catch {
            errorData = {
                error: `HTTP ${response.status}: ${response.statusText}`,
                status_code: response.status,
            };
        }

        const exception = new ApiException(errorData);

        // Log specific error types for debugging
        if (exception.isApiKeyError()) {
            console.error("❌ API Key error: Check NEXT_PUBLIC_API_SECRET");
        } else if (exception.isAuthError()) {
            console.error("❌ Auth error: Token expired or invalid");
        } else if (exception.isRateLimitError()) {
            console.error("⏱️ Rate limit exceeded");
        }

        throw exception;
    }

    return response.json();
}

/**
 * Dream history response type
 */
export interface DreamHistoryItem {
    id: number;
    user_id: string;
    content: string;
    analysis: {
        interpretation: string;
        image_prompt: string;
        mode: string;
        sources?: Array<{
            source_type: string;
            title: string | null;
            relevance_score: number;
        }>;
    };
    created_at: string;
}

/**
 * Dream Interpretation API Functions
 */
export const dreamApi = {
    /**
     * Interpret a dream using AI.
     * Requires: X-API-Key
     */
    interpretDream: async (
        request: DreamInterpretationRequest
    ): Promise<DreamInterpretationResponse> => {
        return apiFetch<DreamInterpretationResponse>("/api/dreams/interpret", {
            method: "POST",
            body: JSON.stringify(request),
        });
    },

    /**
     * Analyze a dream using RAG and LLM (Mystic/Psychological).
     * Requires: X-API-Key
     * Optional: Authorization Bearer token (saves to DB if provided)
     */
    analyzeDream: async (
        request: AnalyzeDreamRequest
    ): Promise<AnalyzeDreamResponse> => {
        return apiFetchWithAuth<AnalyzeDreamResponse>("/api/dreams/analyze", {
            method: "POST",
            body: JSON.stringify(request),
        });
    },

    /**
     * Get user's dream history.
     * Requires: X-API-Key + Authorization Bearer token
     */
    getDreamHistory: async (limit: number = 10): Promise<DreamHistoryItem[]> => {
        return apiFetchWithAuth<DreamHistoryItem[]>(
            `/api/dreams/history?limit=${limit}`,
            { method: "GET" }
        );
    },

    /**
     * Search for dream symbols in the knowledge base.
     * Requires: X-API-Key
     */
    searchSymbols: async (
        request: DreamSearchRequest
    ): Promise<DreamSearchResponse> => {
        return apiFetch<DreamSearchResponse>("/api/dreams/search", {
            method: "POST",
            body: JSON.stringify(request),
        });
    },

    /**
     * Get a list of common dream symbols.
     * Requires: X-API-Key
     */
    getCommonSymbols: async (): Promise<CommonSymbolsResponse> => {
        return apiFetch<CommonSymbolsResponse>("/api/dreams/symbols/common", {
            method: "GET",
        });
    },

    /**
     * Check API health status.
     * Note: /api/health does NOT require API key
     */
    healthCheck: async (): Promise<HealthCheckResponse> => {
        const url = `${API_BASE_URL}/api/health`;
        const response = await fetch(url);
        return response.json();
    },

    /**
     * Analyze dream using the Analysis Triangle (Psychology + Tarot + I Ching).
     * Requires: X-API-Key
     */
    analyzeTriangle: async (request: TriangleAnalysisRequest): Promise<TriangleAnalysisResponse> => {
        return apiFetch<TriangleAnalysisResponse>("/api/dreams/triangle", {
            method: "POST",
            body: JSON.stringify(request),
        });
    },
};

export default dreamApi;
