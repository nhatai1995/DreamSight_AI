"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DreamInterpretationRequest(BaseModel):
    """Request model for dream interpretation."""
    
    dream_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The dream narrative to interpret",
        examples=["I was flying over a beautiful ocean with dolphins swimming below"]
    )
    include_symbols: bool = Field(
        default=True,
        description="Whether to include symbol analysis in the response"
    )
    language: str = Field(
        default="en",
        description="Response language (en, vi, etc.)"
    )


class DreamSymbol(BaseModel):
    """A symbol identified in the dream."""
    
    symbol: str = Field(..., description="The dream symbol identified")
    meaning: str = Field(..., description="Interpretation of the symbol")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How relevant this symbol is to the dream"
    )


class DreamInterpretationResponse(BaseModel):
    """Response model for dream interpretation."""
    
    id: str = Field(..., description="Unique interpretation ID")
    dream_text: str = Field(..., description="The original dream text")
    interpretation: str = Field(..., description="The AI-generated interpretation")
    symbols: List[DreamSymbol] = Field(
        default_factory=list,
        description="List of symbols identified in the dream"
    )
    emotional_theme: str = Field(
        default="",
        description="The primary emotional theme of the dream"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the interpretation"
    )


class DreamSearchRequest(BaseModel):
    """Request model for searching dream symbols."""
    
    query: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Search query for dream symbols"
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return"
    )


class DreamSearchResult(BaseModel):
    """A single search result."""
    
    content: str = Field(..., description="The matching content")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    score: float = Field(..., description="Similarity score")


class DreamSearchResponse(BaseModel):
    """Response model for dream symbol search."""
    
    query: str = Field(..., description="The original search query")
    results: List[DreamSearchResult] = Field(
        default_factory=list,
        description="List of matching results"
    )
    total_count: int = Field(..., description="Total number of results found")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


# ============================================================================
# Analyze Dream Models (RAG + LLM with Image Prompt Generation)
# ============================================================================

from enum import Enum


class AnalysisMode(str, Enum):
    """Analysis mode for dream interpretation."""
    PSYCHOLOGICAL = "psychological"
    MYSTICAL = "mystical"


class AnalyzeDreamRequest(BaseModel):
    """Request model for RAG-based dream analysis."""
    
    user_dream: str = Field(
        ...,
        min_length=10,
        max_length=500,  # Reduced to save tokens (production limit)
        description="The dream narrative provided by the user (max 500 chars)",
        examples=["I dreamt I was walking through an endless forest of mirrors"]
    )
    mode: AnalysisMode = Field(
        default=AnalysisMode.MYSTICAL,
        description="Analysis mode: 'psychological' for Jungian analysis, 'mystical' for esoteric interpretation"
    )


class SourceMetadata(BaseModel):
    """Metadata for a retrieved source document."""
    
    source_type: str = Field(
        default="unknown",
        description="Type of source (dream_dictionary, tarot, i_ching, etc.)"
    )
    title: Optional[str] = Field(
        None,
        description="Title or name of the source document"
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score from vector search"
    )
    excerpt: str = Field(
        ...,
        description="Excerpt of the retrieved content"
    )


class AnalyzeDreamResponse(BaseModel):
    """Response model for RAG-based dream analysis."""
    
    interpretation: str = Field(
        ...,
        description="The LLM-generated dream interpretation based on retrieved context"
    )
    image_prompt: str = Field(
        ...,
        description="A detailed prompt for generating a Surrealist/Dali-style image of the dream"
    )
    image_base64: Optional[str] = Field(
        None,
        description="Base64-encoded generated dream image, or null if generation failed"
    )
    sources: List[SourceMetadata] = Field(
        default_factory=list,
        description="List of source documents used for the interpretation"
    )
    mode: AnalysisMode = Field(
        ...,
        description="The analysis mode used"
    )
    user_dream: str = Field(
        ...,
        description="The original dream text"
    )

