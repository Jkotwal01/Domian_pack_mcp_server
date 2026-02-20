"""Test script for PDF RAG flow."""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.rag_manager import ingest_pdf, _get_retriever
from app.utils.templates import generate_domain_template

async def test_generation_only():
    print("🧠 Testing Template Generation (No RAG)...")
    domain_name = "Legal Contract Analysis"
    description = "Analyzing legal documents for clauses and risks"
    
    try:
        template = await generate_domain_template(
            domain_name=domain_name,
            description=description,
            retriever=None
        )
        
        print(f"✅ Generation Source: {'DEFAULT' if template.get('name') == 'New Domain' else 'LLM'}")
        print("Entities:")
        for entity in template.get('entities', []):
            print(f" - Name: {entity.get('name')}, Type: {entity.get('type')}")
    except Exception as e:
        print(f"❌ Generation failed with exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv()
    # Also print settings for sanity check
    from app.config import settings
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Groq Model: {settings.GROQ_MODEL}")
    
    asyncio.run(test_generation_only())
