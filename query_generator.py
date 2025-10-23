import os
import re
import mysql.connector
import logging
from groq import Groq
from dotenv import load_dotenv
from database import get_schema  # assumes your database.py defines get_schema()


# ---------------------- ENVIRONMENT SETUP ----------------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


print("🔍 MYSQL_USER:", os.getenv("MYSQL_USER"))
print("🔍 MYSQL_PASSWORD:", os.getenv("MYSQL_PASSWORD"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------- 1. CLEAN SQL OUTPUT ----------------------
def clean_sql_output(response_text: str) -> str:
    """
    Removes Markdown formatting and extracts valid SQL statements.
    Handles multiple statements and removes GPT explanations.
    """
    clean_text = re.sub(r"```(?:sql)?\s*(.*?)```", r"\1", response_text, flags=re.DOTALL)
    clean_text = clean_text.replace("`", "")
    clean_text = re.sub(r"(?i)^(here is .*?:|the sql query is:)\s*", "", clean_text.strip())
    statements = [stmt.strip() for stmt in clean_text.split(";") if stmt.strip()]
    formatted_statements = []
    for stmt in statements:
        # Uppercase keywords manually to avoid dependency on sqlparse
        stmt = re.sub(r"\b(select|from|where|join|on|group by|order by|and|or|limit)\b",
                      lambda m: m.group(0).upper(), stmt, flags=re.I)
        formatted_statements.append(stmt)
    return ";\n\n".join(formatted_statements) + (";" if formatted_statements else "")


# ---------------------- 2. SQL VALIDATION ----------------------
def validate_sql_query(sql_query: str):
    """
    Minimal SQL syntax validation.
    Returns (True, None) if valid, else (False, error_message).
    """
    if not sql_query.strip().lower().startswith(("select", "insert", "update", "delete", "explain")):
        return False, "Invalid SQL — must start with SELECT/INSERT/UPDATE/DELETE."
    if ";" not in sql_query:
        return False, "SQL missing semicolon."
    return True, None


# ---------------------- 3. GENERATE SQL USING GROQ ----------------------
def generate_sql_query(n1_query: str) -> str:
    """
    Converts a natural language query into an optimized MySQL query using Groq API.
    Uses schema info for accuracy.
    """
    try:
        schema = get_schema()
        schema_text = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in schema.items()])

        prompt = f"""
        You are an expert MySQL query generator.
        Convert the following natural language query into an optimized SQL statement.

        Rules:
        - Use correct MySQL syntax.
        - Use JOINs, GROUP BY, and indexes efficiently.
        - Return ONLY the SQL query — no explanation or comments.
        - End with a semicolon.

        Database Schema:
        {schema_text}

        Natural Language Query: "{n1_query}"
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a MySQL expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        raw_sql_query = response.choices[0].message.content.strip()
        clean_query = clean_sql_output(raw_sql_query)
        return clean_query

    except Exception as e:
        logging.error(f"Error generating SQL query: {e}")
        return None


# ---------------------- 4. SUGGEST INDEX ----------------------
def suggest_index(sql_query: str, db_config: dict) -> str:
    """
    Runs EXPLAIN on the query to suggest potential indexing improvements.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {sql_query}")
        plan = cursor.fetchall()
        print("\nQuery Execution Plan:")
        for row in plan:
            print(row)
        cursor.close()
        conn.close()
        return "Consider adding indexes on columns used in WHERE, JOIN, or ORDER BY clauses."
    except Exception as e:
        return f"Could not generate execution plan: {e}"


# ---------------------- 5. EXECUTE SQL QUERY ----------------------
def execute_query(sql_query: str, db_config: dict):
    """
    Executes validated SQL query and returns results or error details.
    """
    is_valid, error_msg = validate_sql_query(sql_query)
    if not is_valid:
        logging.error(f"SQL Validation Error: {error_msg}")
        raise ValueError(error_msg)

    try:
        logging.info(f"Connecting to DB with config: {db_config}")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        logging.info(f"Executing SQL: {sql_query}")
        cursor.execute(sql_query)

        if sql_query.strip().lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()
            results = f"{cursor.rowcount} rows affected."

        cursor.close()
        conn.close()
        return results

    except mysql.connector.Error as e:
        logging.error(f"MySQL Error: {e}")
        raise Exception(f"MySQL Error: {e}")
    except Exception as e:
        logging.error(f"General Error executing query: {e}")
        raise

# ---------------------- 6. MAIN (LOCAL TESTING) ----------------------
if __name__ == "__main__":
    db_config = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "sakila"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "auth_plugin": "mysql_native_password"
}


    user_input = input("Enter your natural language query: ")
    sql_query = generate_sql_query(user_input)

    if sql_query:
        print(f"\nGenerated SQL Query:\n{sql_query}")
        results = execute_query(sql_query, db_config)
        if results:
            print("\nQuery Results:")
            if isinstance(results, list):
                for row in results:
                    print(row)
            else:
                print(results)

            tips = suggest_index(sql_query, db_config)
            print("\nOptimization Tips:", tips)
        else:
            print("No results found or error executing query.")
    else:
        print("Failed to generate SQL query.")

def explain_sql_query(sql_query: str) -> str:
    """
    Uses Groq API to explain the given SQL query in simple English.
    """
    try:
        prompt = f"""
        You are a SQL expert. Explain in simple English what the following SQL query does:
        {sql_query}

        Include:
        - Which tables are used
        - What conditions are applied
        - What the result represents
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful SQL expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        explanation = response.choices[0].message.content.strip()
        return explanation

    except Exception as e:
        logging.error(f"Error explaining SQL query: {e}")
        return "Could not generate explanation."
