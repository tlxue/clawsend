# Contributing to ClawSend

Thank you for your interest in contributing to ClawSend! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/clawsend.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dependencies: `pip install -e ".[dev]"`

## Development Setup

```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run the local server
python clawsend/scripts/server.py

# Run tests
pytest
```

## Code Style

- Python 3.11+ required
- Use type hints where practical
- Follow existing code patterns
- Run `ruff check` before committing

## Commit Messages

Use clear, descriptive commit messages:

```
Add encryption support for task_request messages

- Implement hybrid encryption in send.py
- Add --encrypt flag to CLI
- Update documentation
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Submit PR with clear description

## What to Contribute

### Good First Issues

- Documentation improvements
- Error message clarity
- CLI help text
- Test coverage

### Feature Ideas

- WebSocket push delivery
- Multi-party conversations
- Message persistence options
- Additional intents

### Bug Reports

When reporting bugs, include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs/output

## Security Issues

**Do not open public issues for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for responsible disclosure.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn

## Questions?

Open a discussion or issue for questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
