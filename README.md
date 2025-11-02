# AI SQL Assistant (Groq + MySQL + Streamlit)

**AI SQL Assistant** is a full-stack AI-powered SQL generator and executor built with **FastAPI**, **Groq LLM**, and **Streamlit**.  
It converts **natural language queries** into optimized **MySQL commands**, executes them directly, and provides **human-readable explanations** and **visualizations** of query results.

---

## Key Features

- **Natural Language to SQL**: Generate SQL queries using the Groq API (`llama-3.3-70b-versatile`)
- **Query Execution**: Run generated or manual SQL queries securely against a MySQL database
- **Query Explanation**: Translate complex SQL into plain English
- **Database Explorer**: Browse databases, tables, and columns interactively
- **Optimization Tips**: Get automatic indexing and performance suggestions
- **Visualization**: Display query results as interactive tables, pie charts, or bar graphs
- **Query History**: Re-run and review past SQL queries

---

## Tech Stack

| Layer                      | Technology                                      |
|----------------------------|-------------------------------------------------|
| **Frontend**               | Streamlit                                       |
| **Backend API**            | FastAPI                                         |
| **LLM**                    | Groq (Llama 3.3 70B Versatile)                  |
| **Database**               | MySQL (via SQLAlchemy + mysql-connector-python) |
| **Environment Management** | python-dotenv                                   |
| **Logging**                | loguru / logging                                |
| **Testing**                | pytest                                          |

---

## Project Structure

<details>
<summary>Click to expand</summary>

```bash
ai-sql-assistant/
│
├── app.py                 # FastAPI entry point – routes for SQL generation, execution & schema
├── ui.py                  # Streamlit UI – interactive chat, explorer, results & charts
├── query_generator.py     # LLM prompts, SQL cleaning, execution, explanation & optimisation tips
├── database.py            # DB connection (SQLAlchemy), schema extraction, list-databases/tables/columns
├── .env                   # Secrets – GROQ_API_KEY, MySQL credentials (never commit!)
├── requirements.txt       # Pip dependencies (FastAPI, Streamlit, Groq, SQLAlchemy, …)
└── README.md              # You are here!




---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/ai-sql-assistant.git
cd ai-sql-assistant

2. Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the root directory:
GROQ_API_KEY=your_groq_api_key_here
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=root456
MYSQL_DATABASE=sakila
MYSQL_PORT=3306
Note: Ensure your MySQL server is running and accessible with the above credentials.

Running the Application
Step 1 — Start FastAPI Backend

uvicorn app:app --reload

API available at: http://127.0.0.1:8000
Step 2 — Start Streamlit Frontend
In a new terminal:

streamlit run ui.py

Web app opens at: http://localhost:8501

1. Generate SQL from Natural Language
2. Execute Query
3. Explain Query

Troubleshooting
Issue,Cause,Fix
Error generating SQL,Invalid API key or no schema context,Verify .env and DB access
MySQL connection refused,Wrong credentials or inactive MySQL server,Check MySQL service and credentials
CORS error,Streamlit not allowed to call FastAPI,Add CORS middleware in app.py
No tables/columns listed,Missing database selection,Ensure correct MYSQL_DATABASE in .env

License
MIT License
Free for personal and educational use.


Contributing
Contributions are welcome! Feel free to:

Open issues
Submit pull requests
Improve documentation
