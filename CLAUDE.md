# CLAUDE.md

Project-specific guidance for Claude Code.

## Publishing to ClawHub

ClawHub is the skill registry for OpenClaw. To publish this skill:

### Prerequisites

1. Install the ClawHub CLI: `npm install -g clawhub`
2. Generate a token at https://clawhub.ai (Settings > API Tokens)

### Login

Use `https://clawhub.ai` (without www):

```bash
npx clawhub auth login --token <YOUR_TOKEN> --registry https://clawhub.ai
```

### Publish

```bash
npx clawhub publish ./clawsend \
  --slug clawsend \
  --name "ClawSend" \
  --version <VERSION> \
  --changelog "<CHANGELOG>" \
  --registry https://clawhub.ai
```

### Verify

```bash
npx clawhub whoami --registry https://clawhub.ai
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
