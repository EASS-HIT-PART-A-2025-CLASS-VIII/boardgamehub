from mcp.server.fastmcp import FastMCP
from app.crud import list_boardgames
from app.database import get_session

mcp = FastMCP("io.eass.boardgames")

@mcp.tool(name="list-boardgames-page")
async def list_boardgames_page(page: int = 1, page_size: int = 5) -> dict:
    """List board games with pagination.
    
    Args:
        page: The page number to retrieve (1-based index)
        page_size: The number of items per page
    """
    # Create a fresh generator for the dependency
    gen = get_session()
    session = next(gen)
    try:
        offset = (page - 1) * page_size
        items, total = list_boardgames(session, offset=offset, limit=page_size)
        return {
            "status": 200, 
            "total": total, 
            "items": [item.model_dump() for item in items]
        }
    finally:
        session.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")
