# SDK Configuration

This guide explains how to configure the NexosAI SDK using environment variables and a `.env` file.

---

## Environment Variables

Set the following variables in your `.env` file (see `.env.dist` for a template):

| **Variable**                  | **Description**                                 | **Default**             |
|-------------------------------|-------------------------------------------------|-------------------------|
| `NEXOSAI__BASE_URL`           | Base URL for the API service (**required**)     | `https://api.nexos.ai`  |
| `NEXOSAI__API_KEY`            | API key for authentication (**required**)       | `your_api_key_here`     |
| `NEXOSAI__VERSION`            | API version                                     | `v1`                    |
| `NEXOSAI__TIMEOUT`            | Request timeout in seconds                      | `30`                    |
| `NEXOSAI__RETRIES`            | Number of retries for failed requests           | `3`                     |
| `NEXOSAI__EXPONENTIAL_BACKOFF`| Use exponential backoff for retries             | `True`                  |
| `NEXOSAI__MINIMUM_WAIT`       | Minimum wait time between retries (seconds)     | `1`                     |
| `NEXOSAI__MAXIMUM_WAIT`       | Maximum wait time between retries (seconds)     | `10`                    |
| `NEXOSAI__RERAISE_EXCEPTIONS` | Reraise exceptions after retries                | `True`                  |
| `NEXOSAI__RATE_LIMIT`         | Rate limit per second (`0` = no limit)          | `0`                     |
| `NEXOSAI__FOLLOW_REDIRECTS`   | Follow HTTP redirects                           | `True`                  |

Copy `.env.dist` to `.env` and fill in your values:

```bash
cp examples/.env.dist examples/.env
```
