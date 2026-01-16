/**
 * TypeScript type definitions for the Dream Interpretation App.
 * These types mirror the backend Pydantic schemas for type safety.
 */

/**
 * Request payload for dream interpretation.
 */
export interface DreamInterpretationRequest {
  dream_text: string;
  include_symbols?: boolean;
  language?: string;
}

/**
 * A symbol identified in the dream.
 */
export interface DreamSymbol {
  symbol: string;
  meaning: string;
  relevance_score: number;
}

/**
 * Response from the dream interpretation API.
 */
export interface DreamInterpretationResponse {
  id: string;
  dream_text: string;
  interpretation: string;
  symbols: DreamSymbol[];
  emotional_theme: string;
  created_at: string;
}

/**
 * Request payload for searching dream symbols.
 */
export interface DreamSearchRequest {
  query: string;
  limit?: number;
}

/**
 * A single search result from the knowledge base.
 */
export interface DreamSearchResult {
  content: string;
  metadata: Record<string, unknown>;
  score: number;
}

/**
 * Response from the dream symbol search API.
 */
export interface DreamSearchResponse {
  query: string;
  results: DreamSearchResult[];
  total_count: number;
}

/**
 * Common dream symbol reference.
 */
export interface CommonSymbol {
  name: string;
  category: string;
  meaning: string;
}

/**
 * Response containing common dream symbols.
 */
export interface CommonSymbolsResponse {
  symbols: CommonSymbol[];
}

/**
 * API error response.
 */
export interface ApiError {
  error: string;
  detail?: string;
  status_code: number;
}

/**
 * API health check response.
 */
export interface HealthCheckResponse {
  status: string;
  app_name: string;
  version: string;
}

/**
 * Analysis Mode Enum
 */
export enum AnalysisMode {
  PSYCHOLOGICAL = "psychological",
  MYSTICAL = "mystical",
}

/**
 * Request payload for RAG-based analysis.
 */
export interface AnalyzeDreamRequest {
  user_dream: string;
  mode: AnalysisMode;
}

/**
 * Source metadata from retrieval.
 */
export interface SourceMetadata {
  source_type: string;
  title: string | null;
  relevance_score: number;
  excerpt: string;
}

/**
 * Response from the analyze dream API.
 */
export interface AnalyzeDreamResponse {
  interpretation: string;
  image_prompt: string;
  image_base64: string | null;
  sources: SourceMetadata[];
  mode: AnalysisMode;
  user_dream: string;
}

// =============================================================================
// Analysis Triangle Types (NEW)
// =============================================================================

/**
 * Detailed 4-layer psychology analysis (Freud + Jung).
 */
export interface PsychologyDetailed {
  // Layer 1: Emotional Labeling
  core_emotion: string;
  emotion_intensity: number; // 0-100

  // Layer 2: Freudian Analysis
  hidden_desire: string;
  inner_conflict: string;

  // Layer 3: Jungian Archetype & Shadow
  archetype: string;
  shadow_aspect: string;

  // Layer 4: Therapeutic Action
  therapy_type: string;
  actionable_exercise: string;
}

/**
 * Detailed 3-layer Tarot Deep Reading model.
 */
export interface TarotDetailed {
  // Card Identity
  card_name: string;
  card_number: number; // 0-77

  // Layer 1: Orientation
  is_reversed: boolean;
  orientation_reason: string;

  // Layer 2: Elemental Energy
  suit: string;
  element: string;
  energy_analysis: string;

  // Layer 3: Visual Bridge
  visual_bridge: string;

  // Prediction
  prediction: string;
}

/**
 * Detailed I Ching analysis with specific advice for different life areas.
 */
export interface IChingDetailed {
  hexagram_name: string;
  structure: string;
  judgment_summary: string;
  image_meaning: string;
  advice_career: string;
  advice_relationship: string;
  actionable_step: string;
}
/**
 * A single lucky number with its source and meaning.
 */
export interface LuckyNumber {
  number: string;
  source: string;
  meaning: string;
}

/**
 * Final synthesis combining all analyses and lucky numbers.
 */
export interface FinalSynthesis {
  core_message: string;
  numbers: LuckyNumber[];
}

/**
 * Complete Analysis Triangle output.
 */
export interface DreamAnalysis {
  psychology: PsychologyDetailed;
  tarot: TarotDetailed;
  iching: IChingDetailed;
  synthesis: FinalSynthesis;
  art_prompt: string;
}

/**
 * Full response from the Analysis Triangle API.
 */
export interface TriangleAnalysisResponse {
  id: string;
  user_dream: string;
  analysis: DreamAnalysis;
  sources: {
    psychology: string[];
    tarot: string[];
    iching: string[];
  };
  created_at: string;
}

/**
 * Request for Analysis Triangle.
 */
export interface TriangleAnalysisRequest {
  user_dream: string;
}
