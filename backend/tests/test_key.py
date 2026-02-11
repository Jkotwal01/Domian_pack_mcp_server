import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_models():
    async for model in client.models.list():
        print(model.id)

if __name__ == "__main__":
    asyncio.run(test_models())
