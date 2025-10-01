from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from google.cloud import bigquery
from typing import Any
import os
from dotenv import load_dotenv


## Load GCP credentials and bigquery project ID
load_dotenv()
project_bigquery = os.environ['PROJECT_ID']

class BigQueryDatabase:
    def __init__(self):
        """Initialize a BigQuery database client"""

        self.client =  bigquery.Client(project=project_bigquery)

   
    def list_dataset_ids(self) -> list[str]:  
        """List all dataset_ids in a BigQuery project"""

        datasets = self.client.list_datasets()

        return [dataset.dataset_id for dataset in datasets]

    
    def list_table_ids(self, dataset_id: str) -> list[str]:
        """List all tables in a BigQuery dataset"""
        
        dataset_tables = self.client.list_tables(dataset_id)
        table_ids = [t.table_id for t in dataset_tables]

        print(f'Found {len(table_ids)} tables.')

        return table_ids

    def get_table_schema(self, dataset_id: str, table_id: str) -> list[str]:
        """Get the schema for a table in a BigQuery dataset"""
        
        table = self.client.get_table(f'{dataset_id}.{table_id}')  

        return table.schema
    

    def query_db(self, sql_query: str) -> list[dict]:
        """Run a SQL query against a BigQuery dataset"""

        bq_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=100000000,
        use_legacy_sql=False
        )

        cleaned_query = (
        sql_query
        .replace("\\n", " ")
        .replace("\n", " ")
        .replace("\\", " ")
        )
        
        bq_job = self.client.query(cleaned_query, bq_config)
        api_response = bq_job.result(timeout=60)
        result = [dict(row) for row in api_response]

        print(f'First 3 rows of result: {result[:min([3, len(result)])]}')

        return result

db = BigQueryDatabase()
server = Server("bigquery-manager")

# Register handlers
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="list-dataset-ids",
            description="List all datasets in a BigQuery project",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="list-table-ids",
            description="List all tables in the BigQuery database",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "dataset_id to specify which tables to return"},
                },
                "required": ["dataset_id"],
            },
        ),
        types.Tool(
            name="get-table-schema",
            description="Get the schema for a table in a BigQuery dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "dataset_id to specify which tables to return"},
                    "table_id": {"type": "string", "description": "table_id to specify which table schema to return"},
                },
                "required": ["dataset_id", "table_id"],
            },
        ),
        types.Tool(
            name="query-db",
            description="Run a SQL query against the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {"type": "string", "description": "sql statement to run against database"},
                },
                "required": ["sql_query"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

    try:
        if name == "list-dataset-ids":

            results = db.list_dataset_ids()
            return [types.TextContent(type="text", text=str(results))]
        
        if name == "list-table-ids":
            if not arguments or "dataset_id" not in arguments:
                raise ValueError("Missing dataset_id argument")
            results = db.list_table_ids(arguments["dataset_id"])
            return [types.TextContent(type="text", text=str(results))]
        
        if name == "get-table-schema":
            if not arguments or "dataset_id" not in arguments or "table_id" not in arguments:
                raise ValueError("Missing dataset_id and/or table_id arguments")
            results = db.get_table_schema(arguments["dataset_id"], arguments["table_id"])
            return [types.TextContent(type="text", text=str(results))]
        
        if name == "query-db":
            if not arguments or "sql_query" not in arguments:
                raise ValueError("Missing sql_query argument")
            results = db.query_db(arguments["sql_query"])
            return [types.TextContent(type="text", text=str(results))]

        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):

        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bigquery-manager",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
