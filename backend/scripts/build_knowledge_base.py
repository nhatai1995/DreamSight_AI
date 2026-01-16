"""
Build Dream Knowledge Base
Generates a comprehensive dream dictionary and knowledge base, 
then ingests it into ChromaDB for RAG retrieval.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_loader import get_dream_collection
import chromadb
from chromadb.utils import embedding_functions

# Sample Dream Dictionary Data
DREAM_DATA = [
    # Common Symbols
    {
        "title": "Flying Dreams",
        "content": "Flying in dreams often represents a sense of freedom, liberation, or a desire to escape from restrictions in waking life. Lucid flying suggests control over one's destiny. Difficulty staying aloft may indicate a lack of confidence.",
        "source_type": "symbol_dictionary",
        "tags": ["flying", "action", "freedom"]
    },
    {
        "title": "Falling Dreams",
        "content": "Falling is one of the most common dream themes. It usually signifies anxiety, loss of control, or a fear of failure. Freudian analysis suggests it may relate to giving in to temptation. Jungian analysis views it as a reminder to stay grounded.",
        "source_type": "symbol_dictionary",
        "tags": ["falling", "anxiety", "action"]
    },
    {
        "title": "Teeth Falling Out",
        "content": "Dreams about teeth falling out are often linked to anxiety about appearance, communication, or powerless. It can symbolize a fear of aging, loss of vitality, or saying something you regret.",
        "source_type": "symbol_dictionary",
        "tags": ["teeth", "body", "anxiety"]
    },
    {
        "title": "Being Chased",
        "content": "Being chased suggests you are running away from a problem, fear, or aspect of yourself in waking life. The pursuer often represents a suppressed emotion or a responsibility you are avoiding.",
        "source_type": "symbol_dictionary",
        "tags": ["chase", "fear", "action"]
    },
    {
        "title": "Water Symbolism",
        "content": "Water represents the emotional state and the subconscious. Calm water indicates peace and emotional balance. Turbulent or muddy water suggests emotional turmoil or confusion. Drowning implies being overwhelmed by feelings.",
        "source_type": "symbol_dictionary",
        "tags": ["water", "nature", "emotions"]
    },
    {
        "title": "House as Self",
        "content": "In dreams, a house often represents the self or the psyche. Different rooms relate to different aspects of life. An attic may symbolize intellect or hidden memories, while a basement represents the subconscious or primal instincts.",
        "source_type": "symbol_dictionary",
        "tags": ["house", "places", "self"]
    },
    {
        "title": "Snakes",
        "content": "Snakes are complex symbols representing transformation, healing, fear, or hidden threats. Shedding skin implies rebirth. A biting snake may represent a 'toxic' person or situation, or a wake-up call from the unconscious.",
        "source_type": "symbol_dictionary",
        "tags": ["snake", "animal", "transformation"]
    },
    {
        "title": "Naked in Public",
        "content": "Dreaming of being naked in public symbolizes vulnerability, shame, or a fear of being exposed. It can also represent a desire for honesty and being one's true self without social masks.",
        "source_type": "symbol_dictionary",
        "tags": ["naked", "social", "vulnerability"]
    },
    {
        "title": "Death and Dying",
        "content": "Death in dreams rarely predicts actual death. Instead, it symbolizes the end of a phase, a significant change, or the need to let go of old habits. It is a symbol of transformation and new beginnings.",
        "source_type": "symbol_dictionary",
        "tags": ["death", "transformation", "endings"]
    },
    {
        "title": "exams_or_tests", 
        "content": "Taking an exam in a dream, especially one you are unprepared for, highlights self-criticism and fear of failure. It often occurs when you feel scrutinized or judged in waking life.",
        "source_type": "symbol_dictionary", 
        "tags": ["test", "school", "anxiety"]
    },

    # Jungian Concepts
    {
        "title": "The Shadow (Jungian)",
        "content": " The Shadow represents the darker, unconscious aspects of the personality that the conscious ego does not identify with. Encountering a shadow figure (often same-sex, dark, or hostile) forces the dreamer to confront their own repressed traits.",
        "source_type": "psychology_text",
        "tags": ["jung", "shadow", "psychology"]
    },
    {
        "title": "Anima and Animus",
        "content": "The Anima is the feminine inner personality in men, and the Animus is the masculine inner personality in women. They appear in dreams as figures guiding the dreamer toward psychological balance and wholeness.",
        "source_type": "psychology_text",
        "tags": ["jung", "anima", "animus"]
    },
    
    # Mystical Concepts
    {
        "title": "Lucid Dreaming",
        "content": "Lucid dreaming is the state of being aware that you are dreaming while in the dream. In mystical traditions, this is seen as a gateway to higher consciousness and astral travel.",
        "source_type": "mystical_text",
        "tags": ["lucid", "consciousness", "mystical"]
    },
    {
        "title": "Prophetic Dreams",
        "content": "Some traditions believe dreams can forecast future events. These are often distinguished by their vividness and strong emotional resonance, differing from the chaotic nature of ordinary processing dreams.",
        "source_type": "mystical_text",
        "tags": ["prophecy", "future", "mystical"]
    }
]

def populate_db():
    print("Connecting to ChromaDB...")
    collection = get_dream_collection()
    
    current_count = collection.count()
    print(f"Current document count: {current_count}")
    
    if current_count > 0:
        print("Database already contains data. Skipping population.")
        return

    print(f"Preparing to ingest {len(DREAM_DATA)} documents...")
    
    ids = [f"doc_{i}" for i in range(len(DREAM_DATA))]
    documents = [item["content"] for item in DREAM_DATA]
    metadatas = [
        {
            "title": item["title"],
            "source_type": item["source_type"],
            "tags": ",".join(item["tags"])
        }
        for item in DREAM_DATA
    ]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"✓ Successfully populated database with {len(DREAM_DATA)} documents!")

if __name__ == "__main__":
    populate_db()
