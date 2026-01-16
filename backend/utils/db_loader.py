"""
Database Loader Utility
Handles extraction of dream_knowledge_db.zip and ChromaDB initialization.
Checks if extraction is needed to prevent overwriting on every restart.
"""

import os
import zipfile
import shutil
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import get_settings

settings = get_settings()

# Global ChromaDB client instance
_chroma_client: Optional[chromadb.Client] = None
_dream_collection: Optional[chromadb.Collection] = None


def get_project_root() -> Path:
    """Get the project root directory (parent of backend folder)."""
    return Path(__file__).parent.parent.parent


def get_zip_path() -> Path:
    """Get the path to the dream knowledge zip file."""
    return get_project_root() / settings.dream_knowledge_zip


def get_extraction_path() -> Path:
    """Get the path where the zip will be extracted."""
    return Path(settings.chroma_db_path)


def is_already_extracted() -> bool:
    """
    Check if the database has already been extracted.
    Returns True if the extraction folder exists and contains data.
    """
    extraction_path = get_extraction_path()
    
    if not extraction_path.exists():
        return False
    
    # Check if the folder contains ChromaDB data
    chroma_files = list(extraction_path.glob("*"))
    return len(chroma_files) > 0


def extract_database() -> bool:
    """
    Extract the dream_knowledge_db.zip file if not already extracted.
    Returns True if extraction was performed or data already exists.
    """
    zip_path = get_zip_path()
    extraction_path = get_extraction_path()
    
    # Check if already extracted
    if is_already_extracted():
        print(f"✓ Database already extracted at: {extraction_path}")
        return True
    
    # Check if zip file exists
    if not zip_path.exists():
        print(f"✗ Warning: {settings.dream_knowledge_zip} not found at {zip_path}")
        print("  Creating empty ChromaDB database...")
        extraction_path.mkdir(parents=True, exist_ok=True)
        return True
    
    # Create extraction directory
    extraction_path.mkdir(parents=True, exist_ok=True)
    
    # Extract the zip file
    print(f"→ Extracting {settings.dream_knowledge_zip} to {extraction_path}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
        print(f"✓ Successfully extracted database to: {extraction_path}")
        return True
    except zipfile.BadZipFile as e:
        print(f"✗ Error: Invalid zip file - {e}")
        return False
    except Exception as e:
        print(f"✗ Error extracting database: {e}")
        return False


def get_chroma_client() -> chromadb.Client:
    """
    Get or create the ChromaDB client instance.
    Uses persistent storage at the configured path.
    """
    global _chroma_client
    
    if _chroma_client is None:
        extraction_path = get_extraction_path()
        
        _chroma_client = chromadb.PersistentClient(
            path=str(extraction_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        print(f"✓ ChromaDB client initialized at: {extraction_path}")
    
    return _chroma_client


def get_dream_collection() -> chromadb.Collection:
    """
    Get or create the dream knowledge collection.
    """
    global _dream_collection
    
    if _dream_collection is None:
        client = get_chroma_client()
        
        # Get or create the dreams collection
        _dream_collection = client.get_or_create_collection(
            name="dream_knowledge",
            metadata={"description": "Dream symbols and interpretations"}
        )
        print(f"✓ Dream collection loaded with {_dream_collection.count()} documents")
    
    return _dream_collection


def initialize_database() -> bool:
    """
    Initialize the database by extracting zip (if needed) and loading ChromaDB.
    This is the main entry point called during application startup.
    """
    print("\n" + "="*50)
    print("Initializing Dream Knowledge Database")
    print("="*50)
    
    # Step 1: Extract database if needed
    if not extract_database():
        print("✗ Failed to initialize database")
        return False
    
    # Step 2: Initialize ChromaDB client and collection
    try:
        get_dream_collection()
        print("="*50 + "\n")
        return True
    except Exception as e:
        print(f"✗ Error initializing ChromaDB: {e}")
        return False


def reset_database() -> bool:
    """
    Reset the database by removing the extraction folder.
    The next call to initialize_database will re-extract from zip.
    """
    global _chroma_client, _dream_collection
    
    extraction_path = get_extraction_path()
    
    if extraction_path.exists():
        shutil.rmtree(extraction_path)
        _chroma_client = None
        _dream_collection = None
        print(f"✓ Database reset. Removed: {extraction_path}")
        return True
    
    return False
