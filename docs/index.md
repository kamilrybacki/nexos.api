# NexosAI API SDK

Welcome to `nexos.api` — a modern Python SDK for integrating with the [NexosAI](https://nexos.ai) service. NexosAI exposes a powerful API for conversational AI, image, and audio processing. This SDK makes it easy to connect your own applications and services to NexosAI's endpoints.

---

## What is NexosAI?

NexosAI is an advanced AI platform offering:

- Chat completions with tool integrations (web search, RAG, OCR)
- Image generation and analysis
- Audio transcription and synthesis
- A robust, cloud-hosted API for scalable AI workflows

---

## Why Use This SDK?

- **Easy Integration**: Quickly connect your Python apps to the NexosAI API.
- **Unified Interface**: Access chat, image, and audio endpoints with a consistent, type-safe API.
- **Tool Augmentation**: Enhance chat with web search, retrieval-augmented generation, and OCR.
- **Type Safety**: Pydantic models for requests and responses, with IDE autocompletion.
- **Configurable**: Use environment variables or a `.env` file for setup.
- **Extensible**: Add custom endpoints and tools as needed.

---

## How It Works

1. **Configure**: Set your NexosAI API key and options in environment variables or a `.env` file.
2. **Build Requests**: Use endpoint controllers and request builder methods to construct queries.
3. **Send & Receive**: Get structured, validated responses from NexosAI for chat, image, and audio tasks.

---

## Example Use Cases

- Integrate NexosAI chat into your web or mobile app
- Automate customer support with AI-powered conversations
- Analyze and generate images for your service
- Transcribe or synthesize audio for media workflows
- Build new services that leverage NexosAI's cloud API

---

## Get Started

- [Configuration Guide](configuration.md): Set up your environment and credentials
- [Usage Examples](usage.md): See practical code samples for each endpoint
- [Domain Models](domain-models.md): Learn about type hinting and autocompletion
- [Chat Completions Endpoint](endpoints/chat-completions.md): Deep dive into chat operations

---

NexosAI API SDK is built for developers who want a fast, safe, and flexible way to integrate NexosAI's cloud API into their own services.
Explore the docs and start building!

---

For even more detailed look at the SDK functionality, check out the API Reference (use the navigation menu in the upper-left corner) and [Developer Guide](developer_guide.md).
