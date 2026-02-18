# server.py
import asyncio

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import (
    TextContent
)

mcp = FastMCP(name="MCP server", port=8000)

@mcp.tool(description="A tool that simulates file processing and sends progress notifications")
async def process_files(message: str, ctx: Context) -> TextContent:
    files = [f"file_{i}.txt" for i in range(1, 4)]
    for idx, file in enumerate(files, 1):
        await ctx.info(f"Processing {file} ({idx}/{len(files)})...")
        await asyncio.sleep(1)  
    await ctx.info("All files processed!")
    return TextContent(type="text", text=f"Processed files: {', '.join(files)} | Message: {message}")

@mcp.tool(description="A simple addition tool that takes two integers and returns their sum")
async def add(left: int, right: int, ctx: Context) -> TextContent:
    await ctx.info(f"calculate {left} + {right}...")
    await asyncio.sleep(1)
    return TextContent(type="text", text=f"{left + right}")

if __name__ == "__main__":
    mcp.run(transport="streamable-http")