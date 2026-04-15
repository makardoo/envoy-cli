# envoy-cli

> A CLI tool for managing and syncing `.env` files across local, staging, and production environments securely.

---

## Installation

```bash
pip install envoy-cli
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envoy-cli
```

---

## Usage

Initialize a new envoy project in your repository:

```bash
envoy init
```

Push your local `.env` to a remote environment:

```bash
envoy push --env staging
```

Pull the latest `.env` from production:

```bash
envoy pull --env production
```

Diff your local `.env` against a remote environment:

```bash
envoy diff --env staging
```

Run a command with a remote environment loaded (without writing to disk):

```bash
envoy run --env production -- python manage.py migrate
```

---

## Configuration

Envoy reads from a `.envoy.toml` file in your project root. On first run, `envoy init` will guide you through setup, including your storage backend (S3, GCS, or Vault) and encryption preferences.

---

## Features

- 🔐 End-to-end encryption for all stored secrets
- 🔄 Sync across local, staging, and production environments
- 🕵️ Audit log of who pulled or pushed changes
- ⚡ Zero plaintext storage — secrets never touch disk unencrypted

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)