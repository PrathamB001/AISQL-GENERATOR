import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI SQL Assistant", layout="wide")
st.title("🧠 AI SQL Assistant (Groq + MySQL)")

# ================================================
# Sidebar — Database Explorer
# ================================================
st.sidebar.header("🗄️ Database Explorer")

# Fetch available databases
try:
    db_response = requests.get(f"{BASE_URL}/list_databases/")
    if db_response.status_code == 200:
        databases = db_response.json().get("databases", [])
    else:
        databases = []
        st.sidebar.error("Could not fetch databases.")
except Exception as e:
    databases = []
    st.sidebar.error(f"Error fetching databases: {e}")

# Select a database
selected_db = st.sidebar.selectbox("Select Database", databases, index=0 if databases else None)

# Display tables inside the selected database
if selected_db:
    try:
        table_response = requests.get(f"{BASE_URL}/list_tables/{selected_db}")
        if table_response.status_code == 200:
            tables = table_response.json().get("tables", [])
        else:
            tables = []
            st.sidebar.warning("No tables found in this database.")
    except Exception as e:
        tables = []
        st.sidebar.error(f"Error fetching tables: {e}")

    selected_table = st.sidebar.selectbox("Select Table", tables, index=0 if tables else None)

    # Display columns for the selected table
    if selected_table:
        try:
            column_response = requests.get(f"{BASE_URL}/list_columns/{selected_db}/{selected_table}")
            if column_response.status_code == 200:
                columns = column_response.json().get("columns", [])
                if columns:
                    st.sidebar.markdown("**📋 Columns:**")
                    for col in columns:
                        st.sidebar.markdown(f"- {col}")
                else:
                    st.sidebar.info("No columns found.")
            else:
                st.sidebar.error("Error fetching columns.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# ================================================
# Tabs for clarity
# ================================================
tab1, tab2 = st.tabs(["🤖 Generate SQL from Natural Language", "📝 Execute SQL Directly"])

# ================================================
# TAB 1 — AI Query Generator
# ================================================
# ================================================
# TAB 1 — AI Query Generator with Live Suggestions
# ================================================
with tab1:
    st.subheader("Enter Natural Language Query")

    # Initialize session state for query and suggestions
    if "user_query" not in st.session_state:
        st.session_state.user_query = ""
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = []

    # Callback to fetch suggestions from backend
    def fetch_suggestions():
        user_input = st.session_state.user_query
        if user_input.strip():
            try:
                response = requests.post(f"{BASE_URL}/suggest_queries/", json={"query": user_input})
                if response.status_code == 200:
                    st.session_state.suggestions = response.json().get("suggestions", [])
                else:
                    st.session_state.suggestions = []
            except:
                st.session_state.suggestions = []

    # Input box with live suggestion callback
    st.text_input(
        "Type your query...",
        key="user_query",
        placeholder="Example: Show top 5 customers who rented the most movies",
        on_change=fetch_suggestions
    )

    # Display suggestions dynamically below the input
    if st.session_state.suggestions:
        st.markdown("**💡 Suggestions:**")
        for s in st.session_state.suggestions:
            if st.button(s, key=f"suggest_{s}"):
                st.session_state.user_query = s
                st.session_state.suggestions = []

    # Generate SQL button
    if st.button("Generate SQL Query"):
        if not st.session_state.user_query.strip():
            st.warning("Please enter a query.")
        else:
            try:
                with st.spinner("Generating SQL using Groq..."):
                    response = requests.post(f"{BASE_URL}/generate_sql/", json={"query": st.session_state.user_query})
                if response.status_code == 200:
                    sql_query = response.json()["sql_query"]
                    st.code(sql_query, language="sql")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# ================================================
# TAB 2 — Manual SQL Executor
# ================================================
# ================================================
# TAB 2 — Manual SQL Executor with Explanation
# ================================================
# ================================================
# TAB 2 — Manual SQL Executor
# ================================================
# ================================================
# TAB 2 — Manual SQL Executor
# ================================================
with tab2:
    st.subheader("Execute SQL Query Directly")

    # ---------------- Initialize session state ----------------
    if "sql_input" not in st.session_state:
        st.session_state.sql_input = ""
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "last_results" not in st.session_state:
        st.session_state.last_results = []
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "vis_column" not in st.session_state:
        st.session_state.vis_column = None
    if "chart_type" not in st.session_state:
        st.session_state.chart_type = "Pie Chart"
    if "load_query_flag" not in st.session_state:
        st.session_state.load_query_flag = False

    # ---------------- Query History Sidebar ----------------
    st.sidebar.subheader("🕘 Query History")
    history_options = (
        ["No previous queries"]
        + [f"{ts} | {q}" for ts, q in st.session_state.query_history]
        if st.session_state.query_history else ["No previous queries"]
    )
    selected_query = st.sidebar.selectbox("Select a past query to load:", options=history_options)

    if st.sidebar.button("Load Query") and selected_query != "No previous queries":
        st.session_state.last_query = selected_query.split(" | ", 1)[1]
        st.session_state.load_query_flag = True

    # ---------------- Text Area ----------------
    if st.session_state.load_query_flag:
        st.session_state.sql_input = st.session_state.last_query
        # Execute loaded query automatically
        try:
            with st.spinner("Loading previous query results..."):
                response = requests.post(f"{BASE_URL}/execute_sql/", json={"query": st.session_state.last_query})
            if response.status_code == 200:
                data = response.json().get("results", [])
                st.session_state.last_results = data
            else:
                st.error(f"❌ Error executing previous query: {response.text}")
        except Exception as e:
            st.error(f"Error executing previous query: {e}")
        st.session_state.load_query_flag = False

    sql_input = st.text_area(
        "Enter your SQL query below",
        value=st.session_state.sql_input,
        height=150,
        placeholder="SELECT * FROM actor LIMIT 5;"
    )
    st.session_state.sql_input = sql_input

    # ---------------- Execute SQL ----------------
    if st.button("Execute SQL Query"):
        if not sql_input.strip():
            st.warning("Please enter a valid SQL query.")
        else:
            try:
                with st.spinner("Executing query..."):
                    response = requests.post(f"{BASE_URL}/execute_sql/", json={"query": sql_input})
                if response.status_code == 200:
                    data = response.json().get("results", [])
                    tips = response.json().get("optimization_tips", "")

                    st.session_state.last_query = sql_input
                    st.session_state.last_results = data

                    # Add to history with timestamp
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.query_history.insert(0, (timestamp, sql_input))
                    if len(st.session_state.query_history) > 20:
                        st.session_state.query_history.pop()

                    if data and isinstance(data, list) and isinstance(data[0], dict):
                        st.success("✅ Query executed successfully.")
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.write(data)

                    if tips:
                        st.info(tips)
                else:
                    st.error(f"❌ Error executing query: {response.text}")
            except Exception as e:
                st.error(f"Error executing query: {e}")

    # ---------------- Explanation ----------------
    if st.checkbox("Explain SQL Query") and st.session_state.last_query:
        try:
            with st.spinner("Generating explanation..."):
                explain_resp = requests.post(
                    f"{BASE_URL}/explain_sql/",
                    json={"query": st.session_state.last_query}
                )
            if explain_resp.status_code == 200:
                explanation = explain_resp.json().get("explanation", "")
                st.markdown("**📝 Explanation:**")
                st.info(explanation)
            else:
                st.error(f"Error explaining SQL: {explain_resp.text}")
        except Exception as e:
            st.error(f"Error fetching explanation: {e}")

    # ---------------- Visualization ----------------
    if st.checkbox("Show Pie Chart / Bar Graph for Last Result") and st.session_state.last_results:
        df = pd.DataFrame(st.session_state.last_results)
        st.subheader("📊 Visualization")

        if st.session_state.vis_column not in df.columns:
            st.session_state.vis_column = df.columns[0]
        column_to_plot = st.selectbox(
            "Select Column for Visualization",
            df.columns,
            index=list(df.columns).index(st.session_state.vis_column)
        )
        st.session_state.vis_column = column_to_plot

        chart_type = st.radio(
            "Chart Type",
            ["Pie Chart", "Bar Chart"],
            index=0 if st.session_state.chart_type == "Pie Chart" else 1
        )
        st.session_state.chart_type = chart_type

        if chart_type == "Pie Chart":
            st.pyplot(df[column_to_plot].value_counts().plot.pie(autopct='%1.1f%%').figure)
        else:
            st.bar_chart(df[column_to_plot].value_counts())
