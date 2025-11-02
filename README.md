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


Installation & Setup
1. Clone the Repository
