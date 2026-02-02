#!/usr/bin/env python3
"""
Telegram File Sender MCP Server
Provides file sending capabilities to Claude Code CLI via MCP
Supports: PDF, ZIP, images, and other document formats
"""
import asyncio
import logging
import os
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from telegram import Bot
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("telegram-file-sender")

# Telegram bot instance
bot: Bot | None = None


def get_bot() -> Bot:
    """Get or create Telegram bot instance"""
    global bot
    if bot is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        bot = Bot(token=token)
    return bot


async def get_chat_id_from_updates() -> str | None:
    """Get the most recent chat_id from bot updates"""
    try:
        telegram_bot = get_bot()
        updates = await telegram_bot.get_updates(limit=100)

        if updates:
            for update in reversed(updates):
                if update.message:
                    return str(update.message.chat_id)
        return None
    except Exception as e:
        logger.error(f"Error getting chat_id: {e}")
        return None


async def send_document(arguments: dict) -> list[TextContent]:
    """Send a document file to Telegram"""
    chat_id = arguments.get("chat_id")
    file_path = arguments.get("file_path")
    caption = arguments.get("caption", "")

    if not file_path:
        return [TextContent(type="text", text="Error: file_path is required")]

    if not os.path.exists(file_path):
        return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

    # Auto-detect chat_id if not provided
    if not chat_id:
        chat_id = await get_chat_id_from_updates()
        if not chat_id:
            return [TextContent(type="text", text="Error: chat_id not provided and could not auto-detect. Please send a message to the bot first.")]

    try:
        telegram_bot = get_bot()
        with open(file_path, 'rb') as file:
            message = await telegram_bot.send_document(
                chat_id=chat_id,
                document=file,
                caption=caption
            )

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        result = f"Document sent successfully!\nFile: {file_name}\nSize: {file_size} bytes\nChat ID: {message.chat_id}\nMessage ID: {message.message_id}"
        return [TextContent(type="text", text=result)]
    except TelegramError as e:
        return [TextContent(type="text", text=f"Telegram error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def send_photo(arguments: dict) -> list[TextContent]:
    """Send a photo to Telegram"""
    chat_id = arguments.get("chat_id")
    file_path = arguments.get("file_path")
    caption = arguments.get("caption", "")

    if not file_path:
        return [TextContent(type="text", text="Error: file_path is required")]

    if not os.path.exists(file_path):
        return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

    # Auto-detect chat_id if not provided
    if not chat_id:
        chat_id = await get_chat_id_from_updates()
        if not chat_id:
            return [TextContent(type="text", text="Error: chat_id not provided and could not auto-detect. Please send a message to the bot first.")]

    try:
        telegram_bot = get_bot()
        with open(file_path, 'rb') as file:
            message = await telegram_bot.send_photo(
                chat_id=chat_id,
                photo=file,
                caption=caption
            )

        file_name = os.path.basename(file_path)
        result = f"Photo sent successfully!\nFile: {file_name}\nChat ID: {message.chat_id}\nMessage ID: {message.message_id}"
        return [TextContent(type="text", text=result)]
    except TelegramError as e:
        return [TextContent(type="text", text=f"Telegram error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Telegram file sending tools"""
    return [
        Tool(
            name="send_telegram_document",
            description="Send a document file (PDF, ZIP, DOCX, etc.) to Telegram",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to send"
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "Telegram chat ID (optional, will auto-detect if not provided)"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption for the file",
                        "default": ""
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="send_telegram_photo",
            description="Send a photo/image file to Telegram",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the image file"
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "Telegram chat ID (optional, will auto-detect if not provided)"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption for the photo",
                        "default": ""
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "send_telegram_document":
            return await send_document(arguments)
        elif name == "send_telegram_photo":
            return await send_photo(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())



