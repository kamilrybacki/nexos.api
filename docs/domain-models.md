# Domain Models & Type Hinting

The NexosAI SDK provides rich domain models and type hinting for all endpoint requests and responses, making development easier and safer with autocompletion and IDE support.

---

## Domain Models

All request and response payloads are defined as Python classes in `src/nexosapi/domain/`:

- `requests.py`: Request models for each endpoint (e.g., `ChatCompletionsRequest`)
- `responses.py`: Response models (e.g., `ChatCompletionsResponse`)
- `data.py`, `metadata.py`, `headers.py`, `base.py`: Supporting types for messages, tool options, metadata, etc.

These models use Pydantic for validation and type safety, so you get:
- Field validation
- Autocompletion in IDEs
- Type checking

---

## Type Hinting & IDE Support

When you use an endpoint controller (e.g., `chat.completions`), the `request` field exposes all available operations for building and sending requests:

```python
from nexosapi.api.endpoints import chat

# Autocompletion for request builder methods:
chat.completions.request.prepare(...)
chat.completions.request.with_search_engine_tool(...)
chat.completions.request.add_text_message(...)
chat.completions.request.add_image_to_last_message(...)
chat.completions.request.set_response_structure(...)
chat.completions.request.send(...)
```

Your IDE will show available methods and their type signatures, making it easy to:
- Discover request builder operations
- See expected argument types
- Get docstrings and usage hints

---

## Example: Type-Safe Request Building

```python
from nexosapi.api.endpoints import chat
from nexosapi.domain.requests import ChatCompletionsRequest

request = ChatCompletionsRequest(model="your-model-id", messages=[])
request = chat.completions.request.with_model(request, "gpt-3.5-turbo")
request = chat.completions.request.add_text_message(request, "Hello!")
```

Your IDE will autocomplete available fields and methods, and warn about type errors.

---

## Benefits

- **Faster development**: Autocompletion and type hints speed up coding.
- **Fewer bugs**: Type safety and validation catch errors early.
- **Better documentation**: Docstrings and type hints explain usage inline.

For details, see the domain model files in `src/nexosapi/domain/`.
