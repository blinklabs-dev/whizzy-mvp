# Text2SOQL MVP

Convert natural language queries to SOQL and execute them against Salesforce through an MCP server.

## Features

- **MCP Server**: Exposes `sf.query` and `health` tools
- **Natural Language Processing**: Converts business questions to SOQL
- **Salesforce Integration**: Direct querying with simple-salesforce
- **Seeding Script**: Placeholder for test data setup
- **Cursor Chat Integration**: Ready-to-use configuration

## Quick Start

1. **Setup Environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e .
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Salesforce credentials
   ```

3. **Run MCP Server**:
   ```bash
   python -m mcp_server.main
   ```

4. **Test in Cursor Chat**:
   Use the provided MCP configuration to call `sf.query` directly.

## Project Structure

```
text2soql-mvp/
├── mcp_server/          # MCP server implementation
├── salesforce/          # Salesforce integration
├── utils/              # Shared utilities
├── scripts/            # Seeding and setup scripts
├── tests/              # Test files
├── .env.example        # Environment template
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## MCP Configuration

Add this to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "text2soql": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Environment Variables

- `SALESFORCE_USERNAME`: Your Salesforce username
- `SALESFORCE_PASSWORD`: Your Salesforce password
- `SALESFORCE_SECURITY_TOKEN`: Your Salesforce security token
- `SALESFORCE_DOMAIN`: Salesforce domain (e.g., 'login' for production, 'test' for sandbox)
- `OPENAI_API_KEY`: OpenAI API key for natural language processing

## Usage Examples

```python
# Query Salesforce directly
result = sf.query("SELECT Id, Name FROM Account LIMIT 5")

# Health check
status = health()
```

## Development

- **Formatting**: `black . && isort .`
- **Type Checking**: `mypy .`
- **Testing**: `pytest`
