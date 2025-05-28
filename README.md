Local usage:

1. Run Localstack in docker container:
    ```
    docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack
    ```
2. Create dummy data (buckets + objects)
2. Run MCP server:
    ```
    mcp dev full/path/to/mcp-server/s3/server.py
    ```
    