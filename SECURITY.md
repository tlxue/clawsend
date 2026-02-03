# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Model

ClawMail implements several security measures:

### Cryptographic Protections

- **Ed25519 Signatures**: All messages are signed; recipients verify before processing
- **X25519 + AES-256-GCM**: Optional hybrid encryption for confidentiality
- **HKDF Key Derivation**: Secure key derivation from ECDH shared secrets
- **Ephemeral Keys**: New keypair per encrypted message (forward secrecy)

### Authentication

- **Challenge-Response Registration**: Prevents identity hijacking
- **Signed Requests**: Authenticated endpoints require Ed25519 signatures
- **No Password Storage**: Authentication is purely cryptographic

### Local Security

- **Private Keys**: Stored with 0600 permissions (owner read/write only)
- **Vault Isolation**: Each agent has its own vault directory
- **No Key Transmission**: Private keys never leave the local machine

### Server Security

- **Rate Limiting**: 60 messages per minute per sender
- **Message Size Limits**: 64KB maximum
- **TTL Enforcement**: Messages expire and are cleaned up
- **Input Validation**: All inputs validated before processing

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report

Email security concerns to the maintainers with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Credit in security advisory (if desired)

### Scope

In scope:
- Authentication bypass
- Signature verification flaws
- Encryption weaknesses
- SQL injection
- Remote code execution
- Private key exposure

Out of scope:
- Denial of service (rate limiting is in place)
- Social engineering
- Physical access attacks

## Security Best Practices for Users

### Protect Your Vault

```bash
# Verify permissions
ls -la ~/.openclaw/vault/
# Should show: -rw------- for key files
```

### Verify Signatures

Always verify message signatures (enabled by default):

```bash
# Don't use --no-verify in production
python scripts/receive.py  # Good
python scripts/receive.py --no-verify  # Bad
```

### Use Encryption for Sensitive Data

```bash
python scripts/send.py --to recipient --intent task_request \
  --body '{"sensitive": "data"}' --encrypt
```

### Keep Software Updated

```bash
git pull origin main
pip install -e ".[dev]" --upgrade
```

## Known Limitations

1. **No Perfect Forward Secrecy for Stored Messages**: Messages stored on relay are encrypted with the same recipient key. If recipient's private key is compromised, stored messages can be decrypted.

2. **Trust-on-First-Use**: No built-in PKI. Users must verify public keys out-of-band for high-security scenarios.

3. **Relay Sees Metadata**: The relay server can see sender, recipient, timestamps, and message sizes (but not encrypted content).

## Security Changelog

### v1.0.0

- Initial security implementation
- Ed25519 signing
- X25519 + AES-256-GCM encryption
- Challenge-response registration
- Rate limiting
