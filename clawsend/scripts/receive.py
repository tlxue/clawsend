#!/usr/bin/env python3
"""
Receive messages from the ClawHub relay.

Fetches unread messages, verifies signatures, and optionally decrypts payloads.

Usage:
    python receive.py [--server URL] [--limit N] [--json]
"""

import argparse
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.vault import Vault, VaultNotFoundError
from lib.client import RelayClient, output_json, output_human, output_error, ClientError
from lib.auto_setup import ensure_ready, DEFAULT_RELAY
from lib import crypto
from lib import envelope as env


def verify_message(message: dict, signature: str, sender_public_key: str) -> bool:
    """Verify message signature."""
    try:
        public_key = crypto.b64_to_public_signing_key(sender_public_key)
        signable = env.get_signable_content(message)
        return crypto.verify_json(public_key, signable, signature)
    except crypto.SignatureError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Receive messages from the ClawHub relay'
    )
    parser.add_argument(
        '--server',
        default=DEFAULT_RELAY,
        help=f'Relay server URL (default: {DEFAULT_RELAY})'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=50,
        help='Maximum messages to retrieve (default: 50)'
    )
    parser.add_argument(
        '--vault-dir',
        help='Custom vault directory'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON to stdout'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip signature verification (not recommended)'
    )
    parser.add_argument(
        '--decrypt',
        action='store_true',
        help='Attempt to decrypt encrypted payloads'
    )
    args = parser.parse_args()

    # Auto-setup: create vault and register if needed
    try:
        vault = ensure_ready(
            vault_dir=args.vault_dir,
            server=args.server,
            json_mode=args.json,
        )
    except Exception as e:
        if args.json:
            output_error(f'Setup failed: {e}', code='setup_error')
        else:
            print(f"Error: Setup failed: {e}", file=sys.stderr)
        sys.exit(1)

    client = RelayClient(vault, args.server)

    try:
        if not args.json:
            output_human(f"Fetching messages from {args.server}...")

        result = client.receive(limit=args.limit)
        messages = result.get('messages', [])

        if not args.json:
            output_human(f"Received {len(messages)} message(s)")

        # Get sender info for verification
        sender_keys = {}

        # Cache for sender info (keys and aliases)
        sender_info_cache = {}

        def get_sender_info(sender_id: str) -> dict:
            """Get sender's signing key and alias."""
            if sender_id in sender_info_cache:
                return sender_info_cache[sender_id]
            try:
                agents = client.list_agents(limit=500)
                for agent in agents.get('agents', []):
                    sender_info_cache[agent['vault_id']] = {
                        'signing_public_key': agent['signing_public_key'],
                        'alias': agent.get('alias'),
                    }
            except Exception:
                pass
            return sender_info_cache.get(sender_id, {})

        def get_sender_key(sender_id: str) -> str:
            return get_sender_info(sender_id).get('signing_public_key')

        def get_sender_alias(sender_id: str) -> str:
            """Get sender's alias, or vault_id if no alias."""
            info = get_sender_info(sender_id)
            return info.get('alias') or sender_id

        processed = []

        for msg_data in messages:
            message = msg_data['message']
            signature = msg_data['signature']
            sender = msg_data['sender']
            encrypted_payload = msg_data.get('encrypted_payload')

            # Resolve sender alias
            sender_alias = get_sender_alias(sender)

            msg_result = {
                'message_id': msg_data['message_id'],
                'sender': sender,
                'sender_alias': sender_alias,
                'received_at': msg_data['received_at'],
                'envelope': message['envelope'],
                'payload': message['payload'],
                'verified': False,
                'decrypted': False,
            }

            # Verify signature
            if not args.no_verify:
                sender_key = get_sender_key(sender)
                if sender_key:
                    if verify_message(message, signature, sender_key):
                        msg_result['verified'] = True
                    else:
                        msg_result['verification_error'] = 'Invalid signature'
                else:
                    msg_result['verification_error'] = 'Sender key not found'

            # Decrypt if requested and available
            if args.decrypt and encrypted_payload:
                try:
                    decrypted = vault.decrypt(encrypted_payload)
                    msg_result['payload'] = decrypted
                    msg_result['decrypted'] = True
                except crypto.DecryptionError as e:
                    msg_result['decryption_error'] = str(e)

            # Check if from known contact
            msg_result['known_contact'] = vault.is_known_contact(sender)

            # Handle quarantine
            if vault.should_quarantine(sender):
                vault.save_to_quarantine(message, 'unknown_sender')
                msg_result['quarantined'] = True
            else:
                vault.save_message(message, 'received')
                msg_result['quarantined'] = False

            processed.append(msg_result)

        if args.json:
            output_json({
                'messages': processed,
                'count': len(processed),
            })
        else:
            if not processed:
                print("\nNo new messages.", file=sys.stderr)
            else:
                for msg in processed:
                    print("\n" + "="*60, file=sys.stderr)
                    print(f"Message ID: {msg['message_id']}", file=sys.stderr)
                    # Show alias if different from vault_id
                    if msg.get('sender_alias') and msg['sender_alias'] != msg['sender']:
                        print(f"From: {msg['sender_alias']} ({msg['sender']})", file=sys.stderr)
                    else:
                        print(f"From: {msg['sender']}", file=sys.stderr)
                    print(f"Intent: {msg['envelope'].get('intent', msg['payload'].get('intent'))}", file=sys.stderr)
                    print(f"Type: {msg['envelope']['type']}", file=sys.stderr)
                    print(f"Received: {msg['received_at']}", file=sys.stderr)

                    status = []
                    if msg['verified']:
                        status.append("verified")
                    elif msg.get('verification_error'):
                        status.append(f"UNVERIFIED ({msg['verification_error']})")
                    if msg['decrypted']:
                        status.append("decrypted")
                    if msg['known_contact']:
                        status.append("known contact")
                    if msg.get('quarantined'):
                        status.append("QUARANTINED")

                    print(f"Status: {', '.join(status) if status else 'none'}", file=sys.stderr)
                    print(f"Body: {json.dumps(msg['payload'].get('body'), indent=2)}", file=sys.stderr)

    except ClientError as e:
        if args.json:
            output_error(str(e), code=e.response.get('code') if e.response else 'error')
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if args.json:
            output_error(str(e))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
