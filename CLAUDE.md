# CLAUDE.md - Coding Guidelines and Commands

## Build/Test/Lint Commands
- Python: `python3 -m pytest <path_to_test_file>` (Single test)
- Python Lint: `pylint <file_or_directory>`
- Python Type Check: `mypy <file_or_directory>`
- JavaScript: `npm test -- <test_file>` (Single test)
- JavaScript Lint: `npm run lint`

## Code Style Guidelines
- **Python**: Follow PEP 8 conventions (4 spaces indent)
- **JavaScript**: Use ESLint with Prettier formatting
- **Imports**: Group standard library, third-party, and local imports
- **Naming**: camelCase for JS, snake_case for Python
- **Type Hints**: Use type annotations in Python, TypeScript for JS
- **Documentation**: Docstrings for functions/classes following Google style
- **Error Handling**: Use specific exceptions with meaningful messages
- **Git Workflow**: feature/fix branches with conventional commits

## Project Structure
- `bin/` - Contains project environment utilities
- Separate concerns using modular design patterns
- Follow existing patterns for new components

## Security
- Never commit API keys or secrets
- Handle user inputs securely
- Log errors without exposing sensitive information