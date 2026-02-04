# CLAUDE.md

Project-specific guidance for Claude Code.

## Publishing to ClawHub

ClawHub is the skill registry for OpenClaw. To publish this skill:

### Prerequisites

1. Install the ClawHub CLI: `npm install -g clawhub`
2. Generate a token at https://clawhub.ai (Settings > API Tokens)

### Login

Due to a redirect bug, use the `www` subdomain explicitly:

```bash
clawdhub auth login --token <YOUR_TOKEN> --no-browser --registry https://www.clawhub.ai
```

### Publish

```bash
clawdhub publish ./clawsend \
  --slug clawsend \
  --name "ClawSend" \
  --version <VERSION> \
  --changelog "<CHANGELOG>" \
  --registry https://www.clawhub.ai
```

### Verify

```bash
clawdhub whoami --registry https://www.clawhub.ai
```

## Development

```bash
# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run local relay server
python clawsend/scripts/server.py --port 5001

# Test health
curl http://localhost:5001/health
```

## Deployment

The relay is deployed on Railway:

```bash
railway login
railway init --name clawsend-relay
railway up --detach
railway domain  # Get public URL
```
