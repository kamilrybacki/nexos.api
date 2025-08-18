# NexosAI API SDK

A modern Python SDK for integrating with the NexosAI cloud service. Easily connect your applications to NexosAI's powerful API for conversational AI, image, and audio processing.

---

## Features

- Unified API for chat, image, and audio endpoints
- Tool-augmented chat (web search, RAG, OCR)
- Type-safe request/response models (Pydantic)
- Easy configuration via environment variables or `.env` file
- Extensible architecture for custom endpoints

---

## Installation

For users:

```bash
pip install nexosapi
```

For contributors (local development):

```bash
git clone https://github.com/kamilrybacki/nexos.api.git
cd nexos.api
task init-project
```

---

## Quick Start

```python
from nexosapi.api.endpoints import chat

params = {
    "model": "your-model-id",
    "messages": [{"content": "Hello, how are you?", "role": "user"}],
}
chat.completions.request.prepare(params)
chat.completions.request.with_search_engine_tool(options={"search_context_size": "medium"})
response = await chat.completions.request.send()
print(response.model_dump())
```

---

## Documentation

- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Usage Examples](docs/usage.md)
- [Domain Models](docs/domain-models.md)
- [Endpoints](docs/endpoints/chat-completions.md)
- [Developer Guide](docs/developer_guide.md)

---

## Contributing

See [Developer Guide](docs/developer_guide.md) for instructions on adding new endpoints and request builder methods.

---

## License

MIT
