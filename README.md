# mini-kvstore
A mini key-value store accessible via HTTP REST API for use in GitHub Actions

## Install

Install using [uv](https://docs.astral.sh/uv/getting-started/):

```sh
uv sync
```

## Usage

Create `.env` file containing the following keys:

```
KVSTORE_TOKEN=xxxx-super-secret-token-xxxx
KVSTORE_PORT=443
KVSTORE_SSL_CERT=/path/to/fullchain.pem
KVSTORE_SSL_KEY=/path/to/privkey.pem
```

Run `./run.sh` or `uv run server` as root.

## The API

* The key and values are arbitrary strings.
* You have to set the HTTP Bearer token authentication header.
* Set a key: `POST /` with the JSON body like `{"key": "...", "value": "..."}`.
  - If the key already exists, it is overwritten.
* Get a key: `GET /?key={key}`
  - If the key does not exist, it returns 404.
* Delete a key: `DELETE /?key={key}`
  - If the key does not exist, it returns 404.

## Example

```bash
curl -X POST "https://service-url/" \
  -H "Authorization: Bearer xxx-super-secret-token-xxx" \
  -H "Content-Type: application/json" \
  -d '{"key": "example", "value": "data"}'

curl -X GET "https://localhost:8000/?key=example" \
  -H "Authorization: Bearer xxx-super-secret-token-xxx"

curl -X DELETE "https://localhost:8000/?key=example" \
  -H "Authorization: Bearer xxx-super-secret-token-xxx"
```
