# Telegram File Sender MCP

Telegram文件发送MCP服务器，支持发送PDF、ZIP、图片等各种文件格式到Telegram。

## 功能特性

- 发送文档文件（PDF、ZIP、DOCX等）
- 发送图片文件（JPG、PNG、GIF等）
- 自动检测chat_id（如果未提供）
- 支持添加文件说明（caption）

## 安装依赖

```bash
pip install python-telegram-bot mcp
```

## 使用方法

### 发送文档

```python
send_telegram_document(
    file_path="C:/path/to/file.pdf",
    chat_id="123456789",  # 可选
    caption="这是文件说明"  # 可选
)
```

### 发送图片

```python
send_telegram_photo(
    file_path="C:/path/to/image.jpg",
    chat_id="123456789",  # 可选
    caption="这是图片说明"  # 可选
)
```

## 注意事项

- 如果不提供chat_id，系统会自动从最近的消息中获取
- 建议先向bot发送一条消息以确保能够自动检测chat_id
- 文件大小限制：Telegram bot API限制为50MB
