"""
Dream Analysis Service - "Analysis Triangle" Architecture
Analyzes dreams through three lenses:
1. Modern Psychology (Jung, Freud)
2. Western Mysticism (Tarot)
3. Eastern Philosophy (I Ching)

Uses LangChain, OpenAI (ChatOpenAI), and ChromaDB for RAG retrieval.
"""

import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from config import get_settings
from utils.db_loader import get_dream_collection
from utils.logger import log_info, log_warning, log_error

settings = get_settings()


# =============================================================================
# Vietnamese Folk Dream Book (Sổ Mơ Dân Gian) - Complete 100 Numbers (00-99)
# =============================================================================

import re

SO_MO_PATH = os.path.join(os.path.dirname(__file__), "../data/vietnamese_dream_numbers_full.json")

# Data structures for smart lookup
SO_MO_RAW = {}      # {"00": ["trứng", "trứng vịt"], ...}
SO_MO_INDEX = {}    # Reverse index: {"trứng": ["00"], "cá trắng": ["01"], ...}

try:
    with open(SO_MO_PATH, "r", encoding="utf-8") as f:
        SO_MO_RAW = json.load(f)
        
        # Build reverse lookup index: keyword -> list of numbers
        for num, keywords in SO_MO_RAW.items():
            for kw in keywords:
                kw_clean = kw.lower().strip()
                if kw_clean not in SO_MO_INDEX:
                    SO_MO_INDEX[kw_clean] = []
                if num not in SO_MO_INDEX[kw_clean]:
                    SO_MO_INDEX[kw_clean].append(num)
        
        log_info(f"Loaded Sổ Mơ Dân Gian: {len(SO_MO_RAW)} numbers, {len(SO_MO_INDEX)} keywords indexed")
except Exception as e:
    log_warning(f"Could not load Sổ Mơ: {e}")


def lookup_so_mo(user_dream: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Smart scan of dream text for Vietnamese folk dream keywords.
    Uses regex word boundaries and prioritizes longer (more specific) keywords.
    
    Returns (number_string, keyword) if found, else (None, None).
    - number_string can be multiple numbers like "01 - 41" per Tam Hợp logic.
    """
    if not SO_MO_INDEX:
        return None, None
        
    dream_lower = user_dream.lower()
    matches = []
    
    # Scan all indexed keywords against dream text
    for keyword, numbers in SO_MO_INDEX.items():
        # Use regex word boundary to avoid partial matches (e.g., "cá" in "cá nhân")
        # Vietnamese doesn't use strict word boundaries, so we use looser matching
        pattern = re.escape(keyword)
        if re.search(pattern, dream_lower):
            matches.append({
                "keyword": keyword,
                "numbers": numbers,
                "score": len(keyword)  # Longer = more specific
            })
    
    if not matches:
        return None, None
    
    # Sort by score (longest keyword first) to get most specific match
    # E.g., "cá trắng" (8 chars) wins over "cá" (2 chars)
    best_match = sorted(matches, key=lambda x: x['score'], reverse=True)[0]
    
    # =========================================================================
    # Bóng Số (Shadow Numbers) - Tam Hợp Expansion
    # If we find a base number (00-39), also suggest +40 and +80 variants
    # Example: chó=11 -> suggest 11 - 51 - 91
    # =========================================================================
    all_numbers = set()
    for num in best_match['numbers']:
        all_numbers.add(num)
        try:
            base = int(num)
            # Add +40 variant (larger version)
            shadow_40 = base + 40
            if shadow_40 <= 99:
                all_numbers.add(f"{shadow_40:02d}")
            # Add +80 variant (elder/giant version) - wraps around if needed
            shadow_80 = base + 80
            if shadow_80 <= 99:
                all_numbers.add(f"{shadow_80:02d}")
            elif shadow_80 <= 139:  # Wrap: 100->00, 101->01, etc.
                all_numbers.add(f"{shadow_80 - 100:02d}")
        except ValueError:
            pass
    
    # Format with separator (sorted numerically)
    sorted_numbers = sorted(all_numbers, key=lambda x: int(x))
    number_str = " - ".join(sorted_numbers)
    
    log_info(f"Sổ Mơ matched: '{best_match['keyword']}' -> {number_str} (Tam Hợp expanded)")
    
    return number_str, best_match['keyword']


# =============================================================================
# Output Structure (Pydantic Models)
# =============================================================================

class PsychologyDetailed(BaseModel):
    """Detailed 4-layer psychology analysis (Freud + Jung)."""
    
    # Layer 1: Emotional Labeling
    core_emotion: str = Field(description="Cảm xúc chủ đạo cụ thể (Ví dụ: Lo âu, Bi thương, Dồn nén, Giải phóng)")
    emotion_intensity: int = Field(ge=0, le=100, description="Mức độ cảm xúc (0-100%)")
    
    # Layer 2: Freudian Analysis (Id vs Superego conflict)
    hidden_desire: str = Field(description="Dục vọng/bản năng (Id) đang bị kìm nén - Cái bạn thực sự muốn")
    inner_conflict: str = Field(description="Xung đột giữa Id và Superego (áp lực xã hội/đạo đức)")
    
    # Layer 3: Jungian Archetype & Shadow
    archetype: str = Field(description="Cổ mẫu xuất hiện (Shadow/Persona/Child/Hero/Anima/Animus...)")
    shadow_aspect: str = Field(description="Phần Bóng âm - phần tính cách bạn đang chối bỏ hoặc giấu đi")
    
    # Layer 4: Therapeutic Action
    therapy_type: str = Field(description="Loại liệu pháp đề xuất (CBT/Mindfulness/Shadow Work/Journaling...)")
    actionable_exercise: str = Field(description="Bài tập cụ thể để thực hiện (Ví dụ: Grounding 5-4-3-2-1, Box Breathing...)")

class TarotDetailed(BaseModel):
    """Detailed 3-layer Tarot Deep Reading model."""
    
    # Card Identity
    card_name: str = Field(description="Tên lá bài tiếng Anh (Ví dụ: The Tower, The Moon, Ace of Cups)")
    card_number: int = Field(ge=0, le=77, description="Số thứ tự lá bài (0=The Fool, 1-21=Major Arcana, 22-77=Minor Arcana)")
    
    # Layer 1: Orientation (Upright/Reversed)
    is_reversed: bool = Field(description="True nếu lá bài ngược (Reversed), False nếu xuôi (Upright)")
    orientation_reason: str = Field(description="Lý do chọn chiều xuôi/ngược dựa trên tone cảm xúc của giấc mơ")
    
    # Layer 2: Elemental Energy
    suit: str = Field(description="Bộ bài (Major Arcana/Wands-Fire/Cups-Water/Swords-Air/Pentacles-Earth)")
    element: str = Field(description="Nguyên tố chính (Lửa/Nước/Gió/Đất/Spirit)")
    energy_analysis: str = Field(description="Phân tích năng lượng: giấc mơ đang thừa hay thiếu nguyên tố gì")
    
    # Layer 3: Visual Bridge
    visual_bridge: str = Field(description="Cầu nối hình ảnh: sự tương đồng giữa giấc mơ và hình vẽ trên lá bài")
    
    # Prediction
    prediction: str = Field(description="Lời tiên tri và hướng dẫn hành động bằng tiếng Việt")


class IChingDetailed(BaseModel):
    """Detailed I Ching analysis with specific advice for different life areas."""
    hexagram_name: str = Field(description="Tên quẻ Hán-Việt (Ví dụ: Thủy Thiên Nhu)")
    structure: str = Field(description="Cấu trúc quẻ (Ví dụ: Thượng Khảm (Nước) - Hạ Càn (Trời))")
    judgment_summary: str = Field(description="Lời Thoán: Tổng quan Cát/Hung/Bình")
    image_meaning: str = Field(description="Lời Tượng: Ý nghĩa hình tượng thiên nhiên")
    advice_career: str = Field(description="Lời khuyên cụ thể cho Công việc/Sự nghiệp dựa trên quẻ")
    advice_relationship: str = Field(description="Lời khuyên cụ thể cho Tình cảm/Gia đạo")
    actionable_step: str = Field(description="Một hành động cụ thể người dùng nên làm ngay")


class LuckyNumber(BaseModel):
    """A single lucky number with its source and meaning."""
    number: str = Field(description="Con số (Ví dụ: '17', '03', '32-72')")
    source: str = Field(description="Nguồn gốc (Ví dụ: 'Lá bài The Star', 'Quẻ Truân', 'Sổ Mơ: Thấy rắn')")
    meaning: str = Field(description="Giải thích ngắn gọn tại sao lại có số này")


class FinalSynthesis(BaseModel):
    """Final synthesis combining all analyses and lucky numbers."""
    core_message: str = Field(description="Tổng hợp lời khuyên từ Tâm lý, Tarot và Kinh Dịch thành một thông điệp nhất quán (3-4 câu)")
    numbers: List[LuckyNumber] = Field(description="3 con số may mắn từ Tarot, Kinh Dịch, và Sổ Mơ Dân Gian")


class DreamAnalysis(BaseModel):
    """Complete dream analysis output structure."""
    psychology: PsychologyDetailed = Field(
        description="4-layer psychology analysis (Emotion, Freud, Jung, Therapy)"
    )
    tarot: TarotDetailed = Field(
        description="3-layer Tarot Deep Reading (Orientation, Element, Visual Bridge)"
    )
    iching: IChingDetailed = Field(
        description="Detailed I Ching analysis with hexagram structure and specific advice"
    )
    synthesis: FinalSynthesis = Field(
        description="Final synthesis with core message and 3 lucky numbers"
    )
    art_prompt: str = Field(
        description="Highly detailed English prompt for Stable Diffusion image generation"
    )


class TriangleAnalysisResponse(BaseModel):
    """Full response from the Analysis Triangle service."""
    id: str = Field(description="Unique analysis ID")
    user_dream: str = Field(description="Original dream text")
    analysis: DreamAnalysis = Field(description="The three-lens analysis")
    sources: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Retrieved context sources for each lens"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Analysis Triangle Service
# =============================================================================

class AnalysisTriangleService:
    """
    Dream analysis service using the "Analysis Triangle" architecture.
    Combines Psychology, Tarot, and I Ching perspectives.
    """

    def __init__(self) -> None:
        self._llm: Optional[ChatOpenAI] = None
        self._json_parser = JsonOutputParser(pydantic_object=DreamAnalysis)

    @property
    def llm(self) -> ChatOpenAI:
        """Lazy initialization of the LLM (GPT-4o-mini for cost efficiency)."""
        if self._llm is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            
            self._llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model="gpt-4o-mini",  # Cost-efficient, fast, good at JSON
                temperature=0.7,
                max_tokens=2048,
            )
            log_info("Analysis Triangle LLM initialized (GPT-4o-mini)")
        return self._llm

    # -------------------------------------------------------------------------
    # Step A: Parallel Context Retrieval
    # -------------------------------------------------------------------------

    async def _retrieve_context(
        self,
        dream_text: str,
        filter_type: str,
        k: int = 2
    ) -> List[str]:
        """
        Retrieve relevant context from ChromaDB with a specific type filter.
        
        Args:
            dream_text: The user's dream description
            filter_type: The metadata type to filter by ('psychology', 'mystic', 'eastern_philosophy')
            k: Number of documents to retrieve
        
        Returns:
            List of retrieved document contents
        """
        try:
            collection = get_dream_collection()
            
            if collection.count() == 0:
                log_warning(f"ChromaDB collection is empty for filter: {filter_type}")
                return []
            
            # Query with metadata filter
            # Note: ChromaDB uses 'where' for metadata filtering
            results = collection.query(
                query_texts=[dream_text],
                n_results=min(k, collection.count()),
                where={"source_type": filter_type} if filter_type else None,
            )
            
            documents = []
            if results and results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                log_info(f"Retrieved {len(documents)} docs for filter '{filter_type}'")
            
            return documents
            
        except Exception as e:
            log_warning(f"Context retrieval error for {filter_type}: {e}")
            return []

    async def _parallel_retrieve(
        self,
        user_dream: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Perform parallel retrieval for all three analysis lenses.
        
        Returns:
            Tuple of (psychology_context, tarot_context, iching_context)
        """
        # Map our triangle lenses to the actual source_type values in ChromaDB
        # Based on the data we found earlier: 'psychology_text', 'mystical_text', 'symbol_dictionary'
        
        tasks = [
            self._retrieve_context(user_dream, "psychology_text", k=2),
            self._retrieve_context(user_dream, "mystical_text", k=1),
            self._retrieve_context(user_dream, "symbol_dictionary", k=1),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        context_psych = results[0] if isinstance(results[0], list) else []
        context_tarot = results[1] if isinstance(results[1], list) else []
        context_iching = results[2] if isinstance(results[2], list) else []
        
        log_info(f"Parallel retrieval complete: psych={len(context_psych)}, tarot={len(context_tarot)}, iching={len(context_iching)}")
        
        return context_psych, context_tarot, context_iching

    # -------------------------------------------------------------------------
    # Step B: Master System Prompt Construction
    # -------------------------------------------------------------------------

    def _build_master_prompt(
        self,
        user_dream: str,
        context_psych: List[str],
        context_tarot: List[str],
        context_iching: List[str],
        so_mo_number: Optional[str] = None,
        so_mo_keyword: Optional[str] = None
    ) -> List[dict]:
        """
        Build the master system prompt for the Analysis Triangle.
        
        Returns:
            List of messages (system + user) for the LLM
        """
        # Format context sections
        psych_section = "\n".join([f"  - {doc[:500]}" for doc in context_psych]) if context_psych else "  (No psychology context available)"
        tarot_section = "\n".join([f"  - {doc[:500]}" for doc in context_tarot]) if context_tarot else "  (No tarot/mystic context available)"
        iching_section = "\n".join([f"  - {doc[:500]}" for doc in context_iching]) if context_iching else "  (No I Ching/eastern philosophy context available)"
        
        # Format Sổ Mơ lookup result
        if so_mo_number and so_mo_keyword:
            so_mo_section = f"""
**SỔ MƠ DÂN GIAN (Vietnamese Folk Dream Book):**
  ⚠️ DETECTED KEYWORD: "{so_mo_keyword}" -> NUMBER: {so_mo_number}
  You MUST use this number "{so_mo_number}" for the Vietnamese Folk lucky number.
  Source format: "Sổ Mơ: {so_mo_keyword.capitalize()}"
"""
        else:
            so_mo_section = """
**SỔ MƠ DÂN GIAN (Vietnamese Folk Dream Book):**
  (No specific keyword detected - choose based on dream's main emotion/action)
  Common mappings: Rắn=32, Chó=11, Mèo=54, Ma=36, Nước=82, Rơi=68, Bay=69, Chạy=70
"""

        system_prompt = f"""You are the 'DreamSight Oracle', a wise AI capable of seeing through three lenses:
1. **Modern Psychology** (Jungian archetypes, Freudian symbolism, subconscious analysis)
2. **Western Mysticism** (Tarot cards, symbolic divination)
3. **Eastern Philosophy** (I Ching hexagrams, Yin-Yang balance, natural wisdom)

USER DREAM: "{user_dream}"

=== CONTEXT FOUND ===

**PSYCHOLOGY KNOWLEDGE:**
{psych_section}

**TAROT/MYSTIC KNOWLEDGE:**
{tarot_section}

**I CHING/EASTERN WISDOM:**
{iching_section}

{so_mo_section}

=== INSTRUCTIONS ===

Analyze the dream based on the context provided above. Be creative if context is limited.

1. **Psychology (CRITICAL - You are an expert Psychotherapist combining Freudian Psychoanalysis and Jungian Analytical Psychology)**:
   Do NOT give superficial advice like "don't worry" or "you're stressed". Perform a DEEP clinical analysis:
   
   - **Layer 1 - Core Emotion**: Identify the SPECIFIC emotional state (not just "scared" or "happy").
     Examples: Lo âu (Anxiety), Bi thương (Grief), Dồn nén (Repression), Giải phóng (Liberation), 
     Tội lỗi (Guilt), Bất lực (Helplessness), Khao khát (Longing).
     Also rate the intensity (0-100%).
   
   - **Layer 2 - Freudian Analysis (Hidden Conflict) - USE VIETNAMESE EXPLANATIONS!**:
      ⚠️ CRITICAL: Do NOT use raw terms "Id" or "Superego" alone! Always explain in plain Vietnamese!
      
      Use these formats:
      * Instead of "Id" → Write "Bản Năng (phần trong bạn muốn thỏa mãn ngay lập tức)"
      * Instead of "Superego" → Write "Áp lực xã hội (tiếng nói đạo đức, quy chuẩn mà cha mẹ/xã hội dạy)"
      
      Example output format:
      "Bản Năng trong bạn đang khao khát [DESIRE], nhưng Áp lực xã hội khiến bạn cảm thấy [GUILT/FEAR] vì [REASON]. 
       Đây là xung đột giữa 'điều bạn muốn' và 'điều bạn nghĩ mình nên làm'."
      
      Example: "Bản Năng muốn được nghỉ ngơi và buông bỏ trách nhiệm, nhưng Áp lực xã hội nhắc bạn rằng 'phải cố gắng'. Giấc mơ bị rượt đuổi = bạn đang chạy trốn khỏi sự mâu thuẫn này."
   
   - **Layer 3 - Jungian Archetype & Shadow (PERSONALIZE with dream images!)**:
     Do NOT give textbook definitions! TIE the archetype to SPECIFIC dream imagery.
     
     Which archetype is present?
     * Shadow (Bóng âm) = dark figure/enemy = hidden negative traits
     * Persona (Mặt nạ) = clothes/mask = social pressure  
     * Child (Hài nhi) = child figure = need for care
     * Anima/Animus = opposite gender figure = suppressed feminine/masculine
     
     FORMAT: "Hình ảnh [SPECIFIC DREAM IMAGE] đại diện cho [ARCHETYPE] - phần [EXPLANATION] mà ban ngày bạn thường [HOW THEY SUPPRESS IT]."
     Example: "Hình ảnh 'bay trên biển' trong mơ đại diện cho The Anima - phần tâm hồn khao khát tự do mà ban ngày bạn thường dùng lý trí để kìm nén."
   
   - **Layer 4 - Therapeutic Action (with specific prompts)**:
     Recommend a SPECIFIC, SMALL psychological exercise with an exact prompt/question:
     * Shadow Work: "Tối nay, viết 10 phút về: 'Điều tôi ghét nhất ở người khác mà thực ra cũng có trong tôi là...'"
     * Box Breathing: "Thở hộp 4-4-4-4: Hít vào 4s, giữ 4s, thở ra 4s, giữ 4s. Lặp lại 5 lần."
     * Grounding 5-4-3-2-1: "Ngay bây giờ: 5 thứ bạn thấy, 4 thứ bạn nghe, 3 thứ bạn chạm, 2 thứ bạn ngửi, 1 thứ bạn nếm."
     * Journaling: "Viết về: 'Nếu tôi không sợ ai phán xét, tôi sẽ...'"
   
   Tone: Professional, Empathetic, Analytical, Non-judgmental. Use Vietnamese terminology.

2. **Tarot (CRITICAL - You are a Master Tarot Reader with a Rider-Waite deck)**:
   Perform a "Deep Soul Reading" following this process:
   
   - **Layer 1 - Determine Orientation (Xuôi/Ngược)**:
     Analyze the dream's emotional tone carefully:
     * If dream feels liberating, calm, constructive -> Read as UPRIGHT (is_reversed: false)
     * If dream feels anxious, blocked, chaotic -> Read as REVERSED (is_reversed: true)
     Explain WHY you chose this orientation in orientation_reason.
   
   - **Layer 2 - Elemental Decoding (PRIORITY: Astrological Correspondence FIRST, then Visual)**:
     
     MAJOR ARCANA ZODIAC MAPPINGS (use these as PRIMARY element source):
     * The Fool (0): Uranus/Air | The Magician (1): Mercury/Air | High Priestess (2): Moon/Water
     * The Empress (3): Venus/Earth | The Emperor (4): Aries/Fire | Hierophant (5): Taurus/Earth
     * The Lovers (6): Gemini/Air | The Chariot (7): Cancer/Water | Strength (8): Leo/Fire
     * The Hermit (9): Virgo/Earth | Wheel Fortune (10): Jupiter/Fire | Justice (11): Libra/Air
     * The Hanged Man (12): Neptune/Water | Death (13): Scorpio/Water | Temperance (14): Sagittarius/Fire
     * The Devil (15): Capricorn/Earth | The Tower (16): Mars/Fire | THE STAR (17): AQUARIUS/AIR
     * The Moon (18): Pisces/Water | The Sun (19): Sun/Fire | Judgement (20): Pluto/Fire
     * The World (21): Saturn/Earth
     
     Format: "Lá bài thuộc nguyên tố [ASTROLOGICAL ELEMENT] (Zodiac), nhưng trong giấc mơ này, 
     hình ảnh [VISUAL ELEMENT] lại trỗi dậy mạnh mẽ..." -> Shows both knowledge AND flexibility.
     
     Minor Arcana: Wands=Fire, Cups=Water, Swords=Air, Pentacles=Earth
   
   - **Layer 3 - Visual Bridge**:
     Connect a SPECIFIC symbol in the dream to a SPECIFIC image on the Tarot card.
     Example: "Con chó trong giấc mơ tương ứng với con chó/sói trên lá The Moon..."
     Example: "Ngọn núi bạn mơ thấy giống như ngọn núi trên lá The Hermit..."
   
   - **Prediction**: Give a mystical yet practical forecast in Vietnamese.
   
   Tone: Mystical, "Witchy" but grounded. Use evocative language and Vietnamese terms 
   (Lá bài, Trải bài, Năng lượng, Chiều xuôi/ngược, Bộ Gậy/Ly/Kiếm/Tiền...).

3. **I Ching (CRITICAL - You are a Master of I Ching / Kinh Dịch)**:
   
   ⚠️ WARNING - STRICT VALIDATION REQUIRED ⚠️
   Do NOT generate, translate, or invent Hexagram names yourself!
   You MUST retrieve the EXACT Name, Chinese Character, Number, and Structure directly from the provided context_iching.
   If context says "Hexagram 3 - Truân (屯)", output EXACTLY that. Do NOT output a different hexagram.
   
   VALIDATION RULES:
   - Hexagram Number must match context (1-64)
   - Chinese name must match context exactly (e.g., 屯 for Truân, 需 for Nhu)
   - Structure must match: Upper Trigram symbols: ☰(Càn) ☱(Đoài) ☲(Ly) ☳(Chấn) ☴(Tốn) ☵(Khảm) ☶(Cấn) ☷(Khôn)
   - If context mentions "Thủy Lôi Truân" -> Upper: ☵(Khảm/Nước), Lower: ☳(Chấn/Sấm)
   - If context mentions "Thủy Thiên Nhu" -> Upper: ☵(Khảm/Nước), Lower: ☰(Càn/Trời)
   
   Based on the RETRIEVED Hexagram context, provide divination:
   
   - **Analyze Structure**: Identify Upper Trigram (Thượng Quái) and Lower Trigram (Hạ Quái).
     Use CORRECT symbols: ☰☱☲☳☴☵☶☷
     Explain how their interaction relates to the dream.
   
   - **Specific Domains (CRITICAL - Do NOT give generic advice)**:
     * **Career/Business (advice_career)**: Is it time to advance, retreat, or invest? Be specific.
     * **Love/Relationship (advice_relationship)**: Is there harmony or conflict? Should they be patient?
     * **Action (actionable_step)**: Give ONE concrete step the user should take TOMORROW.
   
   - **Tone**: Mystical, Wise, but Action-Oriented. Use Vietnamese terminology (Quân tử, Tiểu nhân, Thời vận...).

4. **SYNTHESIS & NUMEROLOGY (Act as a Wise Sage combining ALL analyses)**:
   
   **Core Message (Tổng Kết - 3-4 câu):**
   - Read the Psychology (subconscious), Tarot (energy), and I Ching (action) above.
   - Find the "Common Thread" (Sợi chỉ đỏ xuyên suốt) connecting all 3.
   - Write a warm, inspiring synthesis in VIETNAMESE that feels like a personal message.
   - Example: "Nỗi sợ trong bạn là có thật vì một sự thay đổi lớn đang đến, nhưng hành động tốt nhất lúc này là chờ đợi, không phải chiến đấu."
   
   **Lucky Numbers (Con Số May Mắn - EXACTLY 3 numbers):**
   
   Number 1 - TAROT (Màu Tím):
   - Extract the number from the chosen Tarot Card (The Fool=0, The Star=17, Ace=1, Two=2...)
   - Source: "Lá bài [Card Name]"
   
   Number 2 - I CHING (Màu Xanh Ngọc):  
   - Use the standard Hexagram number from context (1-64). Quẻ Truân=03, Quẻ Nhu=05, etc.
   - Source: "Quẻ [Hexagram Name] (#[Number])"
   
   Number 3 - VIETNAMESE FOLK / SỔ MƠ (Màu Vàng Kim):
   ⚠️ CRITICAL: Check the "SỔ MƠ DÂN GIAN" section in CONTEXT above FIRST!
   - If DETECTED KEYWORD exists -> You MUST use the EXACT number(s) provided (e.g., "11 - 51 - 91" for "Chó")
   - The number string may contain MULTIPLE numbers separated by " - " (Tam Hợp/Bóng Số logic)
   - Copy the ENTIRE number string as-is to the "number" field
   - Source: "Sổ Mơ: [Detected Keyword]"
   - If NO keyword detected -> Use dream's main object/emotion from the fallback mappings

5. **Art Prompt**: Write a detailed prompt in ENGLISH for an AI Image Generator (Stable Diffusion). Style must be: 'Surrealist style, cinematic lighting, masterpiece, highly detailed'. Describe the visual elements of the dream combined with Tarot/I Ching symbols. Make it vivid and painterly.

=== OUTPUT FORMAT ===

Return ONLY a valid JSON object matching this exact schema (no markdown, no extra text):

{{
  "psychology": {{
    "core_emotion": "Lo âu (Anxiety)",
    "emotion_intensity": 75,
    "hidden_desire": "Bạn thực sự khao khát được tự do khỏi trách nhiệm hiện tại...",
    "inner_conflict": "Id muốn buông bỏ tất cả, nhưng Superego đòi bạn phải hoàn thành nghĩa vụ...",
    "archetype": "The Shadow (Bóng âm)",
    "shadow_aspect": "Phần giận dữ và nổi loạn mà bạn đang kìm nén trong cuộc sống hàng ngày...",
    "therapy_type": "Shadow Work + Journaling",
    "actionable_exercise": "Tối nay, hãy viết 10 phút về 'Điều tôi tức giận nhất nhưng không dám nói ra là...'"
  }},
  "tarot": {{
    "card_name": "The Tower",
    "card_number": 16,
    "is_reversed": true,
    "orientation_reason": "Giấc mơ mang cảm giác lo âu và mất kiểm soát, nên lá bài được đọc theo chiều ngược.",
    "suit": "Major Arcana",
    "element": "Spirit (Tinh thần/Nghiệp)",
    "energy_analysis": "Giấc mơ có năng lượng Lửa quá mạnh - sự phá hủy, biến động. Cần nước để xoa dịu.",
    "visual_bridge": "Tòa tháp đổ sập trong giấc mơ tương ứng với hình ảnh The Tower đang cháy và người rơi xuống.",
    "prediction": "Một sự thay đổi lớn đang đến. Đừng cố bám víu vào những gì đã mục nát..."
  }},
  "iching": {{
    "hexagram_name": "Thủy Thiên Nhu (水天需)",
    "structure": "Thượng Khảm (Nước ☵) - Hạ Càn (Trời ☰)",
    "judgment_summary": "Cát - Đợi chờ đúng thời cơ sẽ hanh thông",
    "image_meaning": "Mây đọng trên trời, quân tử ăn uống yến lạc để chờ thời",
    "advice_career": "Đây không phải lúc để tiến công. Hãy củng cố nội lực, chuẩn bị kỹ lưỡng...",
    "advice_relationship": "Trong tình cảm, cần kiên nhẫn. Đừng vội vàng thúc ép...",
    "actionable_step": "Ngày mai, hãy dành 30 phút viết ra 3 điều bạn cần chuẩn bị trước khi hành động lớn."
  }},
  "synthesis": {{
    "core_message": "Nỗi sợ trong bạn là có thật vì một sự thay đổi lớn đang đến. Tâm lý học cho thấy bạn đang kìm nén điều gì đó, Tarot báo hiệu sự đổ vỡ cần thiết, và Kinh Dịch khuyên bạn chờ đợi. Hãy bình tĩnh - đây không phải lúc để chiến đấu, mà là lúc để chuẩn bị.",
    "numbers": [
      {{
        "number": "16",
        "source": "Lá bài The Tower",
        "meaning": "Số của sự thay đổi đột ngột và giải phóng khỏi cấu trúc cũ"
      }},
      {{
        "number": "05",
        "source": "Quẻ Nhu (#05)",
        "meaning": "Số của sự chờ đợi đúng thời cơ, kiên nhẫn sẽ được đền đáp"
      }},
      {{
        "number": "11 - 51 - 91",
        "source": "Sổ Mơ: Chó",
        "meaning": "Tam Hợp: Chó nhỏ (11) - Chó lớn (51) - Chó già (91)"
      }}
    ]
  }},
  "art_prompt": "Surrealist style painting of a dreamscape with..."
}}"""

        user_message = f"Analyze this dream through the three lenses and return the JSON analysis."

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

    # -------------------------------------------------------------------------
    # Step C: Execution and JSON Parsing
    # -------------------------------------------------------------------------

    def _parse_json_response(self, response_text: str) -> DreamAnalysis:
        """
        Parse the LLM response into a DreamAnalysis object.
        Handles various JSON formatting issues.
        """
        # Clean up common issues
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            data = json.loads(text)
            return DreamAnalysis(**data)
        except json.JSONDecodeError as e:
            log_error(f"JSON parse error: {e}")
            raise OutputParserException(f"Failed to parse JSON: {e}")
        except Exception as e:
            log_error(f"Validation error: {e}")
            raise OutputParserException(f"Failed to validate output: {e}")

    def _get_fallback_analysis(self, user_dream: str, error_msg: str) -> DreamAnalysis:
        """
        Return a fallback analysis structure when parsing fails.
        """
        return DreamAnalysis(
            psychology=PsychologyDetailed(
                core_emotion="Không xác định",
                emotion_intensity=50,
                hidden_desire="Hệ thống tạm thời không thể phân tích sâu. Vui lòng thử lại.",
                inner_conflict=f"Lỗi kỹ thuật: {error_msg}",
                archetype="N/A",
                shadow_aspect="Không có dữ liệu",
                therapy_type="Thử lại sau",
                actionable_exercise="Hãy thử phân tích lại sau vài phút."
            ),
            tarot=TarotDetailed(
                card_name="The Wheel of Fortune",
                card_number=10,
                is_reversed=False,
                orientation_reason="Bánh xe vận mệnh luôn xoay chuyển - đây là thông điệp trung tính.",
                suit="Major Arcana",
                element="Spirit (Tinh thần)",
                energy_analysis="Năng lượng đang ở trạng thái chuyển đổi.",
                visual_bridge="Như bánh xe không ngừng quay, đôi khi cần thời gian để hiểu rõ.",
                prediction="Hãy thử lại sau - có thể có thông điệp quan trọng đang chờ bạn."
            ),
            iching=IChingDetailed(
                hexagram_name="Mông (蒙) - Sự Mông Muội",
                structure="Thượng Cấn (Núi ☶) - Hạ Khảm (Nước ☵)",
                judgment_summary="Bình - Cần thêm thời gian để hiểu rõ",
                image_meaning="Suối chảy dưới chân núi, dần dần sẽ sáng tỏ",
                advice_career="Khi gặp trở ngại, hãy kiên nhẫn và học hỏi thêm.",
                advice_relationship="Đừng vội vàng phán xét, hãy dành thời gian thấu hiểu.",
                actionable_step="Hãy thử lại sau vài phút khi hệ thống ổn định."
            ),
            synthesis=FinalSynthesis(
                core_message="Hệ thống đang gặp trục trặc tạm thời. Hãy thử lại sau vài phút để nhận được thông điệp đầy đủ từ vũ trụ.",
                numbers=[
                    LuckyNumber(number="10", source="Lá bài Wheel of Fortune", meaning="Số của sự xoay chuyển vận mệnh"),
                    LuckyNumber(number="04", source="Quẻ Mông (#04)", meaning="Số của sự học hỏi và khai sáng"),
                    LuckyNumber(number="00", source="Sổ Mơ: Chờ đợi", meaning="Số của sự bình yên, thử lại sau")
                ]
            ),
            art_prompt=f"Surrealist style painting of a mysterious dream with swirling clouds and symbolic imagery, cinematic lighting, masterpiece quality, dream elements: {user_dream[:100]}"
        )

    async def analyze_dream_triangle(
        self,
        user_dream: str,
        max_retries: int = 2
    ) -> TriangleAnalysisResponse:
        """
        Main entry point for the Analysis Triangle dream analysis.
        
        Args:
            user_dream: The user's dream description
            max_retries: Number of retry attempts on parse failure
        
        Returns:
            TriangleAnalysisResponse with complete analysis
        """
        analysis_id = str(uuid.uuid4())
        log_info(f"Starting Analysis Triangle for dream (id: {analysis_id[:8]}...)")
        
        # Step A: Parallel context retrieval
        context_psych, context_tarot, context_iching = await self._parallel_retrieve(user_dream)
        
        # Step A.5: Pre-process Sổ Mơ lookup (Vietnamese Folk Dream Book)
        so_mo_number, so_mo_keyword = lookup_so_mo(user_dream)
        if so_mo_number:
            log_info(f"Sổ Mơ detected: '{so_mo_keyword}' -> {so_mo_number}")
        
        # Step B: Build the master prompt with Sổ Mơ context
        messages = self._build_master_prompt(
            user_dream,
            context_psych,
            context_tarot,
            context_iching,
            so_mo_number=so_mo_number,
            so_mo_keyword=so_mo_keyword
        )
        
        # Step C: Execute LLM call with retry logic
        analysis: Optional[DreamAnalysis] = None
        last_error = ""
        
        for attempt in range(max_retries + 1):
            try:
                log_info(f"LLM call attempt {attempt + 1}/{max_retries + 1}")
                
                # Convert dict messages to LangChain message objects
                lc_messages = [
                    SystemMessage(content=messages[0]["content"]),
                    HumanMessage(content=messages[1]["content"])
                ]
                
                response = await self.llm.ainvoke(lc_messages)
                response_text = response.content
                
                log_info(f"Received LLM response ({len(response_text)} chars)")
                
                # Parse the JSON response
                analysis = self._parse_json_response(response_text)
                log_info("Successfully parsed Analysis Triangle response")
                break  # Success, exit retry loop
                
            except OutputParserException as e:
                last_error = str(e)
                log_warning(f"Parse attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry
                    
            except Exception as e:
                last_error = str(e)
                log_error(f"LLM call failed: {e}")
                break  # Don't retry on LLM errors
        
        # Use fallback if all attempts failed
        if analysis is None:
            log_warning("Using fallback analysis due to parsing failures")
            analysis = self._get_fallback_analysis(user_dream, last_error)
        
        # Build and return the complete response
        return TriangleAnalysisResponse(
            id=analysis_id,
            user_dream=user_dream,
            analysis=analysis,
            sources={
                "psychology": [doc[:200] + "..." for doc in context_psych],
                "tarot": [doc[:200] + "..." for doc in context_tarot],
                "iching": [doc[:200] + "..." for doc in context_iching],
            },
            created_at=datetime.utcnow()
        )


# =============================================================================
# Singleton Service Instance
# =============================================================================

analysis_triangle_service = AnalysisTriangleService()


# =============================================================================
# Convenience Function
# =============================================================================

async def analyze_dream_triangle(user_dream: str) -> TriangleAnalysisResponse:
    """
    Convenience function to analyze a dream using the Analysis Triangle.
    
    Args:
        user_dream: The user's dream description
    
    Returns:
        TriangleAnalysisResponse with complete three-lens analysis
    """
    return await analysis_triangle_service.analyze_dream_triangle(user_dream)
