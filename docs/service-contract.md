# Service Contract

## Overview
This document defines the behavioral contract for the BoardGameHub API, specifically focusing on data retrieval patterns, output formats, and caching mechanisms.

## 1. Pagination
The API enforces deterministic pagination to handle large datasets efficiently.

- **Parameters**:
    - `page` (int, default: 1): The page number to retrieve.
    - `page_size` (int, default: 10, max: 100): The number of items per page.
- **Response Headers**:
    - `X-Total-Count`: Total number of items available across all pages.
- **Ordering**: Results are deterministically ordered by `id` to ensure stable pagination.

### Example Request
```http
GET /boardgames/?page=1&page_size=5 HTTP/1.1
```

### Example Response
```json
{
  "page": 1,
  "page_size": 5,
  "total": 42,
  "items": [
    {
      "id": 1,
      "name": "Catan",
      "rating": 7.1,
      "year_published": 1995,
      ...
    }
  ]
}
```

## 2. CSV Export
Clients can request data in CSV format for easy import into spreadsheet tools.

- **Trigger**: Set query parameter `format=csv`.
- **Response Header**: `Content-Type: text/csv`
- **Content-Disposition**: `attachment; filename="boardgames.csv"`

### Example Request
```http
GET /boardgames/?format=csv HTTP/1.1
```

## 3. ETag & Caching
To reduce bandwidth, the API supports **Conditional GET** requests using ETags.

- **Mechanism**: The server computes a SHA-256 hash of the response body (ETag).
- **Client Behavior**: Clients should store the `ETag` from the response headers. On subsequent requests, send it in the `If-None-Match` header.
- **Server Behavior**:
    - If the data has not changed, the server returns `304 Not Modified` with no body.
    - If the data has changed, the server returns `200 OK` with the new body and new ETag.

### Workflow
1.  **First Request**:
    ```http
    GET /boardgames/ HTTP/1.1
    ```
    **Response**:
    ```http
    HTTP/1.1 200 OK
    ETag: "W/6b86b273..."
    ```

2.  **Subsequent Request**:
    ```http
    GET /boardgames/ HTTP/1.1
    If-None-Match: "W/6b86b273..."
    ```
    **Response**:
    ```http
    HTTP/1.1 304 Not Modified
    ```
