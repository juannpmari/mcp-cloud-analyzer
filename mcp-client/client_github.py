from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",  # Executable
    args=["mcp-remote",
        "https://api.githubcopilot.com/mcp/",
        "--header",
        "Authorization: Bearer token",

        ],
)


# Optional: create a sampling callback
async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=handle_sampling_message
        ) as session:
            # Initialize the connection
            await session.initialize()

            # # List available prompts
            # prompts = await session.list_prompts()

            # # Get a prompt
            # prompt = await session.get_prompt(
            #     "example-prompt", arguments={"arg1": "value"}
            # )

            # # List available resources
            # resources = await session.list_resources()

            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(tool.name)
            print(f"Found {len(tools.tools)} tools")

            # Call a tool
            result = await session.call_tool("list_commits", arguments={"owner": "juannpmari", "repo": "commercial-assistant"})
            # Depending on the provided OAuth scope, this tool will find or not a private repo:
            # read:user - find public repo
            # repo - find public and private repo
            print(result)

            # Read a resource
            # content, mime_type = await session.read_resource("file://some/path")

        


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())