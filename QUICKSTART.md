# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Environment
```bash
# Run the setup script (already done!)
python setup.py
```

### 2. Configure Salesforce Credentials
Edit the `.env` file with your Salesforce credentials:
```bash
# Edit .env file
SALESFORCE_USERNAME=your_username@example.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
SALESFORCE_DOMAIN=login  # or 'test' for sandbox
```

### 3. Test the MCP Server
```bash
# Activate virtual environment
source venv/bin/activate

# Test the server
python -m mcp_server.main
```

### 4. Configure Cursor Chat
Add this to your Cursor MCP configuration (usually in `~/.cursor/mcp.json` or similar):

```json
{
  "mcpServers": {
    "text2soql": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "PYTHONPATH": "/Users/naveenjain/Projects/text2soql-mvp"
      }
    }
  }
}
```

### 5. Query Salesforce from Cursor Chat!

Now you can use these commands in Cursor Chat:

- **Query Salesforce**: `sf.query("SELECT Id, Name FROM Account LIMIT 5")`
- **Health Check**: `health()`

## Example Queries

Try these in Cursor Chat:

```
sf.query("SELECT Id, Name, Type FROM Account LIMIT 10")
```

```
sf.query("SELECT Id, Name, StageName, Amount FROM Opportunity WHERE StageName = 'Closed Won'")
```

```
sf.query("SELECT Id, FirstName, LastName, Email FROM Contact LIMIT 5")
```

## Troubleshooting

### Connection Issues
- Verify your Salesforce credentials in `.env`
- Check if you're using the correct domain (`login` for production, `test` for sandbox)
- Ensure your security token is correct

### MCP Server Issues
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Check that all dependencies are installed: `pip list`
- Verify the PYTHONPATH in your MCP configuration

### Common Errors
- **"Not connected to Salesforce"**: Check your credentials
- **"SOQL query must start with SELECT"**: Ensure your query starts with SELECT
- **"Module not found"**: Activate the virtual environment

## Next Steps

1. **Seed Test Data**: Run `python scripts/seed_data.py` to create sample data
2. **Add Natural Language Processing**: Integrate OpenAI for NL-to-SOQL conversion
3. **Extend with Snowflake**: Add data warehousing capabilities
4. **Add Slack Integration**: Create automated reporting

## Support

- Check the main [README.md](README.md) for detailed documentation
- Review the code in `mcp_server/main.py` for implementation details
- Test with the provided test files in `tests/`
