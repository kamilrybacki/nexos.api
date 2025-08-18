# Installation

This page explains how to install the NexosAI API SDK in your Python environment.

---

## Prerequisites

- Python 3.12 or newer
- Access to the NexosAI API (API key required)

---

## Install via pip (Recommended for Users)

If the SDK is published on PyPI:

```bash
pip install nexosapi
```

If you are installing from source (e.g., cloning the repository):

```bash
git clone https://github.com/kamilrybacki/nexos.api.git
cd nexos.api
pip install .
```

---

## Local Development (Recommended for Contributors)

To use the following commands, you need to have `task` installed.
Plkease refer to the [Taskfile installation docs for details](https://taskfile.dev/docs/installation).

For easier setup and development, use the provided Taskfile for common commands:

1. **Initialize the project and install all dependencies:**

```bash
task init-project
```

1. **Install development dependencies only:**

```bash
task install-dev
```

1. **Install production dependencies only:**

```bash
task install-prod
```

1. **Enable pre-commit hooks:**

```bash
task enable-pre-commit
```

1. **Run tests:**

```bash
task test
```

1. **Run linters and formatters:**

```bash
task lint
```

---

## Virtual Environment (Recommended)

Create and activate a virtual environment to isolate dependencies:

```bash
python -m venv <venv_path>
source <venv_path>/bin/activate
```

---

```bash
poetry install
```

---

## Verify Installation

Check that the SDK is installed and importable:

```python
import nexosapi
print(nexosapi.__version__)
```

---

## Next Steps

- [Configuration Guide](configuration.md): Set up your environment and credentials
- [Usage Examples](usage.md): See practical code samples for each endpoint
