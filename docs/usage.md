# Usage Examples

This page provides practical usage examples for making queries with the NexosAI SDK, based on real Jupyter Notebook workflows.

Each endpoint can **prepare, transform and send** requests seamlessly, by use of the `RequestMaker` object,
available under the `request` attribute of each endpoint.

---

## Chat Completions: Simple Request

Send a basic message to the chat completions endpoint:

```python
from nexosapi.api.endpoints import chat

params = {
    "model": "your-model-id",
    "messages": [{"content": "Hello, how are you?", "name": "Kamil"}],
}
chat.completions.request.prepare(params)
print(chat.completions.request.dump())

# Send the request (async, Jupyter supports top-level await)
if chat.completions.request.pending is None:
    chat.completions.request.reload_last()
response = await chat.completions.request.send()
print(response.model_dump())
```

---

## Chat Completions: Web Search Tool Example

Use the web search tool to fetch live data (e.g., currency exchange rate):

```python
from nexosapi.api.endpoints import chat

# Prepare a request with system instructions
tool_request = {
    "model": "your-model-id",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides current currency prices using Google search."
        },
    ],
}
chat.completions.request.prepare(tool_request)
chat.completions.request.with_search_engine_tool(options={"search_context_size": "medium"})
print(chat.completions.request.dump())

# Send and print response
chat.completions.request.reload_last()
tool_response = await chat.completions.request.send()
print(tool_response.model_dump())
```

---

## Chat Completions: Image Query Example

Identify an object from an image and get a structured response:

```python
from nexosapi.api.endpoints import chat
from IPython.display import Image, display
from requests import request
from pydantic import BaseModel
import json

IMAGE_URL = "https://sketchok.com/images/articles/06-anime/003-pokemon/01/10.jpg"
response = request("GET", IMAGE_URL)
if response.status_code == 200:
    display(Image(response.content, width=300, height=300))

params = {
    "model": "your-model-id",
    "messages": [{"content": "Identify the Pokémon in the image."}],
}
chat.completions.request.prepare(params)
chat.completions.request.add_image_to_last_message(image_url=IMAGE_URL)
chat.completions.request.with_search_engine_tool(options={"search_context_size": "medium"})

class PokemonIdentificationResult(BaseModel):
    name: str
    confidence: float
    reasons: list[str]

chat.completions.request.set_response_structure(PokemonIdentificationResult)
print(chat.completions.request.dump())

if chat.completions.request.pending is None:
    chat.completions.request.reload_last()
response = await chat.completions.request.send()

# Validate response with Pydantic
response_content = response.choices[0].message.content
deserialized_content = json.loads(response_content)
response_data = PokemonIdentificationResult(**deserialized_content)
```

---

## Chat Completions: Ask for Weather

Get the current weather in a city using the web search tool:

```python
from nexosapi.api.endpoints import chat

params = {
    "model": "your-model-id",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides current weather information using Google search."
        },
        {
            "role": "user",
            "content": "What's the weather in Warsaw today?"
        },
    ],
}
chat.completions.request.prepare(params)
chat.completions.request.with_search_engine_tool(options={"search_context_size": "medium"})

chat.completions.request.reload_last()
response = await chat.completions.request.send()
```

---

## Chat Completions: Summarize a News Article

Summarize the content of a news article using a web search and structured response:

```python
from nexosapi.api.endpoints import chat
from pydantic import BaseModel
import json

NEWS_URL = "https://www.bbc.com/news/world-europe-66717489"

params = {
    "model": "your-model-id",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes news articles."
        },
        {
            "role": "user",
            "content": f"Summarize the main points of this article: {NEWS_URL}"
        },
    ],
}
chat.completions.request.prepare(params)
chat.completions.request.with_search_engine_tool(options={"search_context_size": "large"})

class NewsSummary(BaseModel):
    headline: str
    summary: str
    url: str

chat.completions.request.set_response_structure(NewsSummary)

chat.completions.request.reload_last()
response = await chat.completions.request.send()

response_content = response.choices[0].message.content
deserialized_content = json.loads(response_content)
news_data = NewsSummary(**deserialized_content)
```

---

## Chat Completions: Extract Entities from Text

Extract named entities from a user-provided text and return them in a structured format:

```python
from nexosapi.api.endpoints import chat
from pydantic import BaseModel
import json

params = {
    "model": "your-model-id",
    "messages": [
        {
            "role": "system",
            "content": "You are an assistant that extracts named entities from text."
        },
        {
            "role": "user",
            "content": "Barack Obama was born in Hawaii and served as the 44th President of the United States."
        },
    ],
}
chat.completions.request.prepare(params)

class EntityExtractionResult(BaseModel):
    persons: list[str]
    locations: list[str]
    organizations: list[str]

chat.completions.request.set_response_structure(EntityExtractionResult)
print(chat.completions.request.dump())

chat.completions.request.reload_last()
response = await chat.completions.request.send()

response_content = response.choices[0].message.content
deserialized_content = json.loads(response_content)
entities = EntityExtractionResult(**deserialized_content)
```
