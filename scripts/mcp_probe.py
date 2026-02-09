import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from scripts.boardgames_mcp import list_boardgames_page

async def run_probe():
    print("Testing functionality directly...")
    try:
        result = await list_boardgames_page(page=1, page_size=2)
        print("Success! Result:")
        print(result)
    except Exception as e:
        print(f"Error running tool: {e}")

if __name__ == "__main__":
    asyncio.run(run_probe())
