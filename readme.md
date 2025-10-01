# Minimal MCP server for interacting with a BigQuery SQL database

This MCP server enables an LLM such as Claude (via the desktop app) to list datasets, tables within a dataset, retrieve a table schema and run read only queries against a BigQuery database. Claude can write simple queries (such as returning the first 5 rows of a table) based on natural language requests. More complex queries may require additional context about the database to be supplied to the model. 

## Authentication
To use this server, you must supply a bigquery project id via the .env file and authenticate to GCP. The simplest method to connect with GCP is via Application Default Credentials. This can be set up in a terminal by installing the gcloud CLI and running the following in a terminal (replacing YOUR_PROJECT_ID and youremail@domain as required, using the email address linked to your GCP account). 
```
gcloud config configurations create YOUR_PROJECT_ID
gcloud config configurations activate YOUR_PROJECT_ID
gcloud config set project YOUR_PROJECT_ID
gcloud config set account youremail@domain
gcloud auth login
gcloud auth application-default login
```

To configure the required access permissions (again replacing YOUR_PROJECT_ID and youremail@domain), run the following:

```
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:youremail@domain" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:youremail@domain" \
    --role="roles/bigquery.jobUser"
```

This method has the advantage that access to multiple projects can be configured through the CLI; simply repeat the steps to create a new set of project credentials and activate the desired project as needed. For further guidance and alternative authentication mechanisms such as service accounts see https://cloud.google.com/docs/authentication/application-default-credentials. 

## Local set-up

To connect this MCP to Claude Desktop, add the following to the claude_desktop_config.json file (in Windows this is located at %USERPROFILE%/AppData/Roaming/Claude). Again, replacing both "/path/to/bigquery_mcp.py" and "YOUR_PROJECT_ID" as required:

```
{
"mcpServers": {
    "bigquery": {
    "command": "path/to/python.exe",
    "args": ["/path/to/bigquery_mcp.py"],
    "env": {
        "GCP_PROJECT_ID": "YOUR_PROJECT_ID"
    }
    }
}
}
```
Ensure you replace "path/to/python.exe" with the path to a python installation that has access to all the required libraries as specified in requirements.txt, for instance as part of a virtual environment. You can easily create such an environment (in the desired location) by running in the command line:

```cd path/to/desired-venv-location```

```python -m venv .venv```

To make the MCP available to Claude Desktop, restart the application after updating claude_desktop_config.json. You should see it available as a Local MCP server by navigating to Settings (accesible by clicking on your profile name in the bottom left corner) -> Developer. You should then be able to ask Claude questions about your database. The permissions granted above do not grant the ability to delete any data; but caution is advised when using this MCP to avoid any inadvertent data loss.

You can test each MCP function in turn using the Inspector tool by running (requires npx installation):

```npx @modelcontextprotocol/inspector python path/to/bq_mcp_server.py```

## Potential messages to pass to the agent

- Give me the names all available datasets.
- What tables are contained in {dataset name}?
- How many rows are in {table_name}?
- What columns are in  {dataset name}.{table_name}?
- Show me the first five rows of {table_name}


### Documentation for building MCP servers

https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/lowlevel/server.py

NB. All code in this repository is provided for educational purposes only, with absolutely no warranty explicit, implied, or otherwise.
