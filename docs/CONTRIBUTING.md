# 🤝 Contributing Guide

Thank you for your interest in contributing to the Shopify Returns Chat Agent! This guide will help you get started with contributing effectively.

## 🎯 **Quick Start for Contributors**

1. **🍴 Fork the repository** on GitHub
2. **📥 Clone your fork** locally
3. **🔧 Set up development environment** (see [Development Setup](#development-setup))
4. **🌿 Create a feature branch** for your changes
5. **💻 Make your changes** following our guidelines
6. **🧪 Test your changes** thoroughly
7. **📝 Submit a pull request** with clear description

## 🛠️ **Development Setup**

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv or conda)

### Local Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/shopify-returns-chat-agent.git
cd shopify-returns-chat-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
cd shopify_returns_chat_agent
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Set up pre-commit hooks (optional but recommended)
pre-commit install
```

### Environment Configuration

```bash
# Copy example environment file
cp shopify_returns_chat_agent/env.example shopify_returns_chat_agent/.env

# Add your test credentials (use test store/sandbox keys)
# Edit .env with your development API keys
```

## 🎨 **Contribution Levels**

We've designed the project to welcome contributors of all experience levels:

### 🟢 **Beginner-Friendly Contributions**

Perfect for first-time contributors or those new to the project:

**🐛 Bug Fixes**
- Fix typos in documentation
- Improve error messages
- Add missing input validation
- Fix CLI help text

**📚 Documentation**
- Add code examples
- Improve API documentation
- Translate documentation
- Add troubleshooting sections

**🧪 Testing**
- Add test cases for edge scenarios
- Improve test coverage
- Add integration tests
- Test different environment setups

**⚙️ Configuration & Setup**
- Docker containerization
- CI/CD improvements
- Environment validation
- Setup scripts

**Example beginner issues:**
- Add validation for email format in order lookup
- Improve CLI help messages with examples
- Add unit tests for PolicyChecker edge cases
- Create Docker container for easy deployment

### 🟡 **Intermediate Contributions**

For developers comfortable with the tech stack:

**🔧 Feature Development**
- New tools and integrations
- CLI enhancements
- API improvements
- Performance optimizations

**🌐 Web Interface (Phase 1 - Tasks 21-25)**
- FastAPI web service wrapper
- RESTful API endpoints
- Web-based chat interface
- Admin dashboard

**📧 Integrations**
- Email notification system
- Webhook processors
- Third-party API integrations
- Database storage options

**Example intermediate issues:**
- Build FastAPI wrapper around CLI agent (Task 21)
- Add email notifications for return confirmations
- Implement database storage for conversation logs
- Create admin dashboard for return analytics

### 🔴 **Advanced Contributions**

For experienced developers ready for complex challenges:

**🧠 AI/ML Features**
- RAG system for dynamic policy understanding
- Advanced conversation flow optimization
- Multi-language support with AI translation
- Fraud detection patterns

**🏢 Enterprise Features**
- Multi-tenant architecture
- Advanced analytics and reporting
- Custom integration framework
- Performance at scale

**🚀 Platform Integrations**
- Shopify App Store submission
- WooCommerce/BigCommerce adapters
- Enterprise API marketplace
- White-labeling capabilities

**Example advanced issues:**
- Implement RAG system for dynamic policy learning
- Build Shopify App Store integration
- Create multi-language conversation support
- Develop AI-powered fraud detection

## 📝 **Development Guidelines**

### Code Style

We follow Python PEP 8 with some project-specific conventions:

```python
# File naming: snake_case
# Class naming: PascalCase
# Function/variable naming: snake_case
# Constants: UPPER_SNAKE_CASE

# Example class structure:
class NewTool:
    """Tool description with clear purpose."""
    
    def __init__(self, config: dict):
        """Initialize with type hints."""
        self.config = config
    
    def process_request(self, data: dict) -> dict:
        """Clear method documentation."""
        # Implementation
        return {"result": "success"}
```

### Testing Requirements

All contributions must include appropriate tests:

```bash
# Run the full test suite
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_your_feature.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

**Test Categories:**
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test tool interactions with mocked APIs
- **End-to-end tests**: Test complete conversation flows
- **Performance tests**: Test response times and API limits

### Documentation Requirements

All new features must include:

1. **Docstrings** for all public functions and classes
2. **Type hints** for function parameters and returns
3. **Example usage** in docstrings or separate examples
4. **README updates** if adding new functionality
5. **API documentation** updates for new endpoints/tools

### Git Workflow

We use GitHub Flow for all contributions:

```bash
# Start from main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes with good commit messages
git add .
git commit -m "feat: add email notification system

- Add EmailNotifier tool for return confirmations
- Integrate with SMTP configuration
- Add tests for email sending functionality"

# Push to your fork
git push origin feature/your-feature-name

# Open Pull Request on GitHub
```

### Commit Message Convention

We use conventional commits for clear change tracking:

```
type(scope): brief description

Detailed description if needed

- Bullet points for multiple changes
- Reference issues with #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

## 🧪 **Testing Guidelines**

### Writing Tests

```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch
from tools.new_tool import NewTool

class TestNewTool:
    """Test suite for NewTool functionality."""
    
    @pytest.fixture
    def mock_config(self):
        return {
            'API_KEY': 'test_key',
            'ENDPOINT': 'test_endpoint'
        }
    
    @pytest.fixture
    def new_tool(self, mock_config):
        return NewTool(mock_config)
    
    def test_successful_request(self, new_tool):
        """Test successful API request processing."""
        result = new_tool.process_request({"test": "data"})
        assert result['success'] is True
    
    @patch('requests.post')
    def test_api_failure_handling(self, mock_post, new_tool):
        """Test graceful handling of API failures."""
        mock_post.side_effect = Exception("API Error")
        
        result = new_tool.process_request({"test": "data"})
        assert result['success'] is False
        assert 'error' in result
```

### Test Data

Use fixtures for consistent test data:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_order():
    return {
        "id": "gid://shopify/Order/1001",
        "name": "#1001",
        "email": "test@example.com",
        # ... complete order data
    }

@pytest.fixture
def sample_customer():
    return {
        "email": "test@example.com",
        "id": "gid://shopify/Customer/123"
    }
```

## 📋 **Pull Request Process**

### Before Submitting

**✅ Checklist:**
- [ ] Tests pass locally (`python -m pytest tests/`)
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No merge conflicts with main branch
- [ ] Commit messages follow convention
- [ ] Changes are focused and atomic

### Pull Request Template

When opening a PR, use this template:

```markdown
## Description
Brief description of what this PR accomplishes.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally

## Related Issues
Closes #123
References #456
```

### Review Process

1. **Automated checks** run on all PRs (tests, linting, etc.)
2. **Code review** by maintainers or experienced contributors
3. **Testing feedback** if additional testing is needed
4. **Approval and merge** once all requirements are met

## 🏗️ **Architecture Guidelines**

### Adding New Tools

New tools should follow the established pattern:

```python
from tools.base_tool import BaseTool

class YourNewTool(BaseTool):
    """Clear description of tool purpose."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "your_new_tool"
        # Tool-specific initialization
    
    def process(self, **kwargs) -> dict:
        """Main processing method called by the agent."""
        try:
            # Your implementation
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        # Validation logic
        return True
```

### Integration with LLM Agent

Tools are automatically discovered and integrated:

```python
# In llm_returns_chat_agent.py
from tools.your_new_tool import YourNewTool

def _initialize_tools(self):
    """Register all available tools."""
    self.tools['your_new_tool'] = YourNewTool(self.config)
```

### Function Calling Schema

Define OpenAI function calling schema:

```python
def get_function_schema(self) -> dict:
    """Return OpenAI function calling schema."""
    return {
        "name": "your_new_tool",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
```

## 🎯 **Current Priorities**

### Immediate Needs (Next 30 days)
- **Docker containerization** for easy deployment
- **FastAPI web service** wrapper (Task 21)
- **Frontend chat interface** (Task 23)
- **Production monitoring** improvements

### Medium-term Goals (Next 90 days)
- **Shopify webhook integration**
- **Email notification system**
- **Database storage for conversations**
- **Admin analytics dashboard**

### Long-term Vision (6+ months)
- **RAG system for dynamic policies**
- **Multi-platform e-commerce support**
- **Enterprise features and scaling**
- **AI-powered fraud detection**

## 🆘 **Getting Help**

### For New Contributors

1. **Start with issues labeled** `good first issue` or `beginner-friendly`
2. **Ask questions** in GitHub Discussions
3. **Join our community** for real-time help
4. **Review existing PRs** to understand our process

### Technical Support

- **📚 Documentation**: Check the [docs/](.) directory first
- **🐛 Bug Reports**: Open detailed GitHub issues
- **💡 Feature Requests**: Start with GitHub Discussions
- **❓ Questions**: Use GitHub Discussions Q&A

### Mentorship Program

We offer mentorship for:
- **First-time open source contributors**
- **Developers new to AI/ML integration**
- **Students working on related projects**
- **Anyone wanting to learn e-commerce automation**

## 🏆 **Recognition**

We value all contributions! Contributors get:

- **🎉 Recognition** in our README and release notes
- **🏷️ GitHub badges** for significant contributions
- **📢 Social media shoutouts** for major features
- **🎁 Swag and rewards** for sustained contributions
- **💼 LinkedIn recommendations** for standout work

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

## 🚀 **Ready to Contribute?**

1. **Browse our [issues](https://github.com/your-username/shopify-returns-chat-agent/issues)**
2. **Start with a `good first issue`**
3. **Fork the repository and get started**
4. **Ask questions if you get stuck**

**Thank you for making the Shopify Returns Chat Agent better for everyone!** 🎉

---

*For more technical details, see our [Architecture Guide](ARCHITECTURE.md) and [API Reference](API_REFERENCE.md).* 