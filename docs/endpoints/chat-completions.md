# Chat Completions Endpoint

This page documents the usage of the Chat Completions endpoint controller and its request builder methods. Each method is type-hinted for IDE autocompletion and safe usage.

---

## Overview

The `ChatCompletionsEndpointController` exposes a `request` field with a rich set of builder methods for constructing and sending chat completion requests. All methods support method chaining for a fluent interface.

---

## Request Builder Methods

### `prepare`

Initialize a new request with a dictionary or model:

```python
chat.completions.request.prepare({
    "model": "6948fe4d-98ce-4f36-bc49-5f652cc07b65",
    "messages": [{"content": "Hello!", "role": "user"}]
})
```

---

### `with_model`

Set the model to use for the request:

```python
chat.completions.request.with_model("6948fe4d-98ce-4f36-bc49-5f652cc07b65")
```

---

### `add_text_message`

Add a user or assistant message:

```python
chat.completions.request.add_text_message("What's the weather in Paris?", role="user")
```

---

### `add_image_to_last_message`

Attach an image to the last message:

```python
chat.completions.request.add_image_to_last_message(image_url="https://sketchok.com/images/articles/06-anime/003-pokemon/01/10.jpg")
```

---

### `with_search_engine_tool`

Enable the web search tool for the request:

```python
from nexosapi.domain.metadata import WebSearchToolOptions, WebSearchUserLocation

search_options = WebSearchToolOptions(
    search_context_size="medium",
    user_location=WebSearchUserLocation(city="Paris", country="France")
)
chat.completions.request.with_search_engine_tool(options=search_options)
```

---

### `with_rag_tool`

Enable the RAG tool for retrieval-augmented generation:

```python
from nexosapi.domain.metadata import RAGToolOptions

rag_options = RAGToolOptions(
    collection_uuid="my-corpus-uuid",
    query="What is the capital of France?",
    threshold=0.8,
    top_n=5,
    model_uuid="model-uuid"
)
chat.completions.request.with_rag_tool(options=rag_options)
```

---

### `with_ocr_tool`

Enable the OCR tool for extracting text from images:

```python
from nexosapi.domain.metadata import OCRToolOptions

ocr_options = OCRToolOptions(file_id="file-uuid")
chat.completions.request.with_ocr_tool(options=ocr_options)
```

---

### `with_parallel_tool_calls`

Enable or disable parallel tool calls:

```python
chat.completions.request.with_parallel_tool_calls(enabled=True)
```

---

### `with_thinking`

Enable or disable the thinking mode:

```python
from nexosapi.domain.metadata import ChatThinkingModeConfiguration

thinking_config = ChatThinkingModeConfiguration(type="enabled", budget_tokens=1024)
chat.completions.request.with_thinking(config=thinking_config)
```

---

### `with_tool_choice`

Specify which tool to use (e.g., auto or a specific function):

```python
chat.completions.request.with_tool_choice("auto")
chat.completions.request.with_tool_choice("name:my_function")
```

---

### `set_response_structure`

Define the expected response schema (Pydantic model or dict):

```python
from pydantic import BaseModel
class MyResponse(BaseModel):
    result: str
chat.completions.request.set_response_structure(MyResponse)
```

---

### `dump`

Show the current request payload:

```python
print(chat.completions.request.dump())
```

---

### `send`

Send the request asynchronously and get the response:

```python
response = await chat.completions.request.send()
print(response.model_dump())
```

---

### `reload_last`

Reload the last request for reuse:

```python
chat.completions.request.reload_last()
```

---

## Example: Full Request Flow

```python
from nexosapi.api.endpoints import chat
from nexosapi.domain.metadata import WebSearchToolOptions, WebSearchUserLocation
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    description: str

chat.completions.request.prepare({
    "model": "6948fe4d-98ce-4f36-bc49-5f652cc07b65",
    "messages": [{"content": "What's the weather in Paris?", "role": "user"}]
})\
.with_search_engine_tool(options=WebSearchToolOptions(
    search_context_size="medium",
    user_location=WebSearchUserLocation(city="Paris", country="France")
))\
.set_response_structure(WeatherResponse)

response = await chat.completions.request.send()
print(response.model_dump())
```
