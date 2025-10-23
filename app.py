from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from query_generator import execute_query, generate_sql_query, explain_sql_query
from database import list_databases, list_tables, list_columns

# Initialize app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Define DB config — make sure these are correct for your system
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root456",
    "database": "sakila",
    "port": 3306
}

# ==============================
# MODELS
# ==============================
class QueryRequest(BaseModel):
    query: str


# ==============================
# ROUTES: SQL GENERATION & EXECUTION
# ==============================
@app.post("/generate_sql/")
async def generate_sql_endpoint(request: QueryRequest):
    """Generate SQL query using the AI model."""
    try:
        sql_query = generate_sql_query(request.query)
        if not sql_query:
            raise HTTPException(status_code=500, detail="Error generating SQL query")
        return {"sql_query": sql_query}
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")


@app.post("/execute_sql/")
async def execute_sql_endpoint(request: QueryRequest):
    """Execute user-provided SQL query."""
    try:
        sql_query = request.query
        results = execute_query(sql_query, db_config)

        if results is None:
            raise HTTPException(status_code=500, detail="Error executing query")

        response = {
            "results": results if isinstance(results, list) else [results],
            "optimization_tips": "Consider adding indexes on frequently used WHERE or JOIN columns."
        }
        return response
    except Exception as e:
        logging.error(f"Error executing SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")


# ==============================
# ROUTES: DATABASE INSPECTION
# ==============================
@app.get("/list_databases/")
async def list_databases_endpoint():
    """List all databases available on the MySQL server."""
    try:
        databases = list_databases()
        if not databases:
            raise HTTPException(status_code=404, detail="No databases found")
        return {"databases": databases}
    except Exception as e:
        logging.error(f"Error listing databases: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing databases: {str(e)}")


@app.get("/list_tables/{database_name}")
async def list_tables_endpoint(database_name: str):
    """List all tables in a given database."""
    try:
        tables = list_tables(database_name)
        if not tables:
            raise HTTPException(status_code=404, detail=f"No tables found in database '{database_name}'")
        return {"tables": tables}
    except Exception as e:
        logging.error(f"Error listing tables for {database_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")


@app.get("/list_columns/{database_name}/{table_name}")
async def list_columns_endpoint(database_name: str, table_name: str):
    """List all columns for a specific table in a database."""
    try:
        columns = list_columns(database_name, table_name)
        if not columns:
            raise HTTPException(
                status_code=404,
                detail=f"No columns found for table '{table_name}' in database '{database_name}'"
            )
        return {"columns": columns}
    except Exception as e:
        logging.error(f"Error listing columns for {database_name}.{table_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing columns: {str(e)}")

@app.post("/explain_sql/")
async def explain_sql_endpoint(request: QueryRequest):
    """
    Takes an SQL query and returns a natural language explanation.
    """
    try:
        explanation = explain_sql_query(request.query)
        return {"explanation": explanation}
    except Exception as e:
        logging.error(f"Error explaining SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error explaining query: {str(e)}")
    
