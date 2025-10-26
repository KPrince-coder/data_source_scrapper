# Contributing Guide

Thank you for your interest in contributing to the BECE Questions Data Scraper! This guide will help you get started with development.

## Development Setup

### Prerequisites

- Python 3.13 or higher
- Git
- A code editor (VS Code recommended)

### Initial Setup

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/KPrince-coder/data_source_scraper.git
   cd data_source_scraper
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Install Playwright browsers** (for screenshot functionality):

   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your ImageKit credentials (optional for basic development)
   ```

### Project Structure

```text
data_source_scraper/
├── config/                 # Configuration management
│   ├── screenshot_config.py
│   └── logging_config.py
├── services/              # Core services
│   ├── screenshot_service.py
│   ├── screenshot_storage_service.py
│   ├── data_enrichment_service.py
│   └── screenshot_workflow.py
├── tests/                 # Test files
├── docs/                  # Documentation
├── main.py               # Main spider
├── run_spider.py         # CLI interface
└── README.md
```

## Development Workflow

### Making Changes

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:

   ```bash
   # Run basic scraper test
   uv run python run_spider.py -s science -y 2022 --no-screenshots
   
   # Test screenshot functionality (requires ImageKit setup)
   uv run python tests/test_screenshot.py
   uv run python tests/test_upload.py
   ```

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**:

   ```bash
   git push origin feature/your-feature-name
   ```

### Coding Standards

#### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and functions
- Use meaningful variable and function names

#### Example Function

```python
def process_screenshot(
    url: str, 
    subject: str, 
    year: str,
    timeout: Optional[int] = None
) -> Optional[str]:
    """
    Process a screenshot for the given URL.
    
    Args:
        url: The URL to capture
        subject: Subject name (e.g., 'science')
        year: Year as string (e.g., '2022')
        timeout: Optional timeout in milliseconds
        
    Returns:
        Screenshot URL if successful, None otherwise
        
    Raises:
        ScreenshotError: If capture fails after retries
    """
    # Implementation here
    pass
```

#### Error Handling

- Use comprehensive error handling with try/except blocks
- Log errors with appropriate context
- Provide graceful degradation when possible
- Don't let screenshot failures break data extraction

```python
try:
    result = capture_screenshot(url)
    if not result:
        logger.warning(f"Screenshot failed for {url}, continuing without visual archive")
        return None
except Exception as e:
    logger.error(f"Screenshot error for {url}: {e}")
    return None
```

#### Logging

- Use the configured logger from `config.logging_config`
- Include relevant context in log messages
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing {subject} {year}")
logger.warning(f"Retrying upload attempt {attempt}/{max_retries}")
logger.error(f"Failed to upload screenshot: {error}")
```

## Testing

### Running Tests

```bash
# Test screenshot capture
uv run python tests/test_screenshot.py

# Test ImageKit upload (requires credentials)
uv run python tests/test_upload.py

# Test basic scraper functionality
uv run python run_spider.py -s science -y 2022 --no-screenshots
```

### Writing Tests

When adding new functionality, include appropriate tests:

1. **Unit tests** for individual functions
2. **Integration tests** for service interactions
3. **End-to-end tests** for complete workflows

Example test structure:

```python
def test_screenshot_capture():
    """Test screenshot capture functionality."""
    service = create_screenshot_service(test_config)
    
    # Test successful capture
    result = await service.capture_screenshot(
        "https://example.com",
        "test_output.png"
    )
    
    assert result is True
    assert Path("test_output.png").exists()
    
    # Cleanup
    Path("test_output.png").unlink(missing_ok=True)
```

## Common Development Tasks

### Adding a New Service

1. Create the service file in `services/`
2. Follow the existing service patterns
3. Add comprehensive error handling
4. Include factory function
5. Update imports in workflow files
6. Add tests
7. Update documentation

### Modifying Configuration

1. Update the config classes in `config/screenshot_config.py`
2. Update `.env.example` with new variables
3. Update validation logic
4. Update documentation

### Adding CLI Options

1. Add argument to `run_spider.py` parser
2. Pass the argument through the call chain
3. Update help text and examples
4. Update documentation

## Debugging

### Common Issues

#### Screenshot Capture Fails

```bash
# Test with visible browser
PLAYWRIGHT_HEADLESS=false uv run python tests/test_screenshot.py

# Check browser installation
playwright install --help
```

#### ImageKit Upload Issues

```bash
# Test configuration
uv run python -c "from config.screenshot_config import load_config; print(load_config().imagekit.is_configured())"

# Test with verbose logging
uv run python run_spider.py -s science -y 2022 --verbose
```

#### Import Errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
uv sync
```

### Debugging Tools

- **Verbose logging**: Use `--verbose` flag
- **Log files**: Check `logs/` directory
- **Browser debugging**: Set `PLAYWRIGHT_HEADLESS=false`
- **ImageKit dashboard**: Check uploads at imagekit.io

## Documentation

### Updating Documentation

When making changes:

1. Update relevant documentation files in `docs/`
2. Update docstrings in code
3. Update README.md if needed
4. Update API reference if adding new methods

### Documentation Style

- Use clear, concise language
- Include code examples
- Provide troubleshooting tips
- Link related sections

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Documentation
- [ ] Updated relevant documentation
- [ ] Added code comments where needed
```

## Getting Help

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: Request review from maintainers

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

Thank you for contributing! 🎉
