# API Reference

## Authentication

### Login (Get Token)
`POST /auth/token`

## Board Games

### List Board Games
`GET /boardgames/`

- **Parameters**:
    - `page` (int): Page number (default: 1)
    - `page_size` (int): Items per page (default: 10, max: 100)
    - `format` (str): "json" or "csv" (default: "json")

### Get Board Game
`GET /boardgames/{id}`

### Create Board Game
`POST /boardgames/`

### Update Board Game
`PUT /boardgames/{id}`

### Delete Board Game
`DELETE /boardgames/{id}`
