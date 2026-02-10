
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_upload_csv(async_client: AsyncClient, admin_token_headers: dict[str, str] | None = None) -> None:
    # 1. Prepare CSV content
    # Format matches bgg_dataset.csv structure: ID;Name;Year Published;Min Players;Max Players;Play Time;Min Age;Users Rated;Rating Average;BGG Rank;Complexity Average;Owned Users;Mechanics;Domains
    # We only need the fields our parser uses: Name, Year Published, Min/Max Players, Play Time, Complexity Average, Rating Average
    csv_content = """ID;Name;Year Published;Min Players;Max Players;Play Time;Min Age;Users Rated;Rating Average;BGG Rank;Complexity Average;Owned Users;Mechanics;Domains
1;Test Game One;2024;2;4;60;12;100;7.5;1;2,5;Card Drafting;Strategy
2;Test Game Two;2023;1;5;30;8;50;8.0;2;1,5;Dice Rolling;Family
"""
    
    # 2. Upload file
    # Ensure filename ends with .csv
    files = {"file": ("test_upload.csv", csv_content, "text/csv")}
    
    # Note: The upload endpoint is currently public in routers/boardgames.py (no Depends(require_role...))
    # If it required auth, we'd pass headers=admin_token_headers
    response = await async_client.post("/boardgames/upload", files=files)
    
    # 3. Verify response
    assert response.status_code == 201
    data = response.json()
    assert "Successfully added" in data["message"]
    # We added 2 games, but if they already exist (idempotency check by name), it might report 0 added.
    # To be safe in a test environment (which usually resets DB), we expect > 0 if DB is empty, or 0 if not.
    # Let's verify we got a success structure.
    assert "errors" in data
    assert len(data["errors"]) == 0

    # 4. Verify games were added by querying them
    # Game 1
    resp_get = await async_client.get("/boardgames/?page=1&page_size=100")
    assert resp_get.status_code == 200
    items = resp_get.json()["items"]
    
    # Check for "Test Game One"
    found = any(g["name"] == "Test Game One" for g in items)
    assert found, "Uploaded game 'Test Game One' not found in list"

