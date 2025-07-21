# Contributing to Pr0Xy-chaIN

Thank you for your interest in contributing to Pr0Xy-chaIN! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues
1. Check existing issues to avoid duplicates
2. Use the issue template when available
3. Include system information (OS, Python version)
4. Provide detailed steps to reproduce
5. Include log excerpts when applicable

### Suggesting Features
1. Check if the feature already exists
2. Open an issue with the "enhancement" label
3. Describe the use case and expected behavior
4. Consider implementation complexity

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Follow the coding standards below
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Pr0Xy-chaIN.git
cd Pr0Xy-chaIN

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # (if available)

# Run tests
python -m pytest tests/

# Check code style
flake8 *.py
black --check *.py
```

## 📝 Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names
- Add docstrings for all public functions

### Code Structure
- Keep functions focused and small
- Use meaningful commit messages
- Add comments for complex logic
- Handle exceptions appropriately

### Example Function
```python
def validate_proxy(proxy: str, timeout: int = 10) -> bool:
    """Validate if a proxy is working.
    
    Args:
        proxy: Proxy string in format 'ip:port'
        timeout: Connection timeout in seconds
        
    Returns:
        True if proxy is working, False otherwise
        
    Raises:
        ValueError: If proxy format is invalid
    """
    if ':' not in proxy:
        raise ValueError(f"Invalid proxy format: {proxy}")
        
    # Implementation here
    return True
```

## 🧪 Testing Guidelines

### Unit Tests
- Write tests for all new functionality
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

### Integration Tests
- Test tool integrations end-to-end
- Use test fixtures for consistent setup
- Clean up after tests

### Test Structure
```python
def test_proxy_validation_success():
    """Test successful proxy validation."""
    manager = ProxyChainManager()
    result = manager.test_proxy("1.2.3.4:8080")
    assert isinstance(result, bool)

def test_proxy_validation_invalid_format():
    """Test proxy validation with invalid format."""
    manager = ProxyChainManager()
    with pytest.raises(ValueError):
        manager.test_proxy("invalid-format")
```

## 📖 Documentation

### Code Documentation
- Update docstrings for modified functions
- Include usage examples in docstrings
- Document any breaking changes

### User Documentation
- Update README.md for new features
- Add examples to DOCUMENTATION.md
- Update QUICK_REFERENCE.md for new commands

## 🔒 Security Considerations

### Security Testing
- Never commit real credentials or API keys
- Use test data for all examples
- Validate user input appropriately
- Consider security implications of changes

### Responsible Disclosure
- Report security vulnerabilities privately
- Allow time for fixes before public disclosure
- Follow coordinated disclosure practices

## 🚀 Release Process

### Version Numbers
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in relevant files
- Tag releases appropriately

### Changelog
- Update CHANGELOG.md with new features
- Include breaking changes
- Credit contributors

## 🏷️ Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No hardcoded paths or credentials
- [ ] Commit messages are clear

### PR Template
```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Added new tests
- [ ] All tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 💡 Ideas for Contributions

### High Priority
- Enhanced error handling and recovery
- Performance optimizations
- Cross-platform compatibility improvements
- More proxy source integrations

### Medium Priority
- GUI/Web interface
- Docker containerization
- Configuration validation
- Proxy quality scoring

### Low Priority
- Additional tool integrations
- Proxy geolocation features
- Statistics and reporting
- Plugin architecture

## 🤔 Questions?

- Open an issue for questions
- Check existing discussions
- Review documentation first
- Be respectful and constructive

## 📜 Code of Conduct

### Be Respectful
- Use inclusive language
- Respect different viewpoints
- Accept constructive criticism
- Focus on what's best for the community

### Be Professional
- Keep discussions on-topic
- Avoid personal attacks
- Provide helpful feedback
- Follow project guidelines

---

Thank you for contributing to Pr0Xy-chaIN! 🔗⚡

**Remember**: This tool is for educational and authorized security testing only.
Always follow responsible disclosure practices and comply with applicable laws.
