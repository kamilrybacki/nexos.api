# Developer Guide: Extending NexosAI SDK

This guide explains how to add new endpoint controllers and request builder methods to the NexosAI SDK. It covers the controller architecture, request manager pattern, and best practices for extending the SDK.

---

## 1. Controller Architecture

All endpoint controllers inherit from `NexosAIAPIEndpointController`, which provides:

- Endpoint registration and validation
- Request/response model binding
- Dependency injection for HTTP service
- A nested `_RequestManager` class for request lifecycle management

**Location:**

- Base: `src/nexosapi/api/controller.py`
- Example: `src/nexosapi/api/endpoints/chat/completions.py`

---

## 2. Creating a New Controller

1. **Define Request and Response Models**
   - Create Pydantic models for your endpoint in `domain/requests.py` and `domain/responses.py`.

2. **Subclass the Controller**
   - Inherit from `NexosAIAPIEndpointController` and set:
     - `endpoint` (e.g., `post:/my/endpoint`)
     - `request_model` and `response_model`

```python
from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.domain.requests import MyRequestModel
from nexosapi.domain.responses import MyResponseModel

class MyEndpointController(NexosAIAPIEndpointController[MyRequestModel, MyResponseModel]):
    endpoint = "post:/my/endpoint"
    request_model = MyRequestModel
    response_model = MyResponseModel
```

---

## 3. Adding Request Preparation/Transformation Methods

Define a nested `Operations` class with static methods that transform the request model. Each method should:

- Accept the request model as the first argument
- Return the updated request model
- Be statically typed for IDE support

```python
class Operations:
    @staticmethod
    def with_custom_option(request: MyRequestModel, option: str) -> MyRequestModel:
        request.option = option
        return request
```

Assign the `Operations` class to the controller:

```python
operations = Operations()
```

---

## 4. Request Manager Pattern

The controller's `request` field is an instance of `_RequestManager`, which:

- Handles request preparation (`prepare`)
- Applies transformation methods (from `Operations`)
- Sends requests (`send`)
- Supports method chaining

**Example usage:**

```python
controller = MyEndpointController()
controller.request.prepare({"option": "value"})\
    .with_custom_option("new-value")\
    .send()
```

---

## 5. Best Practices

- Use Pydantic models for all request/response payloads
- Validate endpoint format (`verb:/path`)
- Document each transformation method with type hints and docstrings
- Keep request builder methods stateless and chainable
- Use the `on_response` and `on_error` hooks for custom response/error handling

---

## 6. Example: Chat Completions Controller

See `src/nexosapi/api/endpoints/chat/completions.py` for a full implementation:

- Static builder methods in `Operations` (e.g., `with_search_engine_tool`, `add_text_message`)
- Type-safe chaining via the request manager
- Endpoint registration and validation

---

## 7. Registering the Controller

Controllers are automatically registered in `CONTROLLERS_REGISTRY` for dependency injection and endpoint management.

---

## 8. Advanced: Custom Response/Error Hooks

Override `on_response` and `on_error` in your controller to customize post-processing or error handling.

```python
async def on_response(self, response: MyResponseModel) -> MyResponseModel:
    # Custom logic
    return response
```

---

For more details, see the source files:

- `api/controller.py` and `api/controller.pyi`
- Example: `api/endpoints/chat/completions.py` and `completions.pyi`
