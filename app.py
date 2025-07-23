
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL connection string (adjust as needed)
engine = create_engine('postgresql+psycopg2://postgres:Hari%4096%24@localhost:5432/foodwastemanagement')

# Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["Introduction", "Load Tables", "SQL Queries 🔎", "Creator"])

# ---------------------- Introduction ----------------------
if page == "Introduction":
    st.title("🍽️ Food Waste Management System")
    st.markdown("""
### 🌍 Why Food Waste Management?

Food waste is a global issue with local solutions. This app connects **providers** (restaurants, grocery stores) with **receivers** (NGOs, shelters) to reduce waste and redistribute surplus food.

It supports:
- Viewing real-time data  
- Running smart analytics  
- Empowering communities through food recovery  

Let's create a sustainable, hunger-free world! 🌾
""")

# ---------------------- Load Tables ----------------------
elif page == "Load Tables":
    st.title("📊 View All Tables")

    def load_table(table_name):
        try:
            return pd.read_sql_table(table_name, con=engine)
        except Exception as e:
            st.error(f"Failed to load {table_name}: {e}")
            return pd.DataFrame()

    tables = {
        "Providers": "providers_data",
        "Receivers": "receivers_data",
        "Food Listings": "food_listings_data",
        "Claims": "claims_data"
    }

    for name, table in tables.items():
        st.subheader(f"📋 {name} Table")
        df = load_table(table)
        st.dataframe(df)

# ---------------------- SQL Queries ----------------------
elif page == "SQL Queries 🔎":
    st.title("🧠 Predefined SQL Queries")

    queries = {
        "How many food providers and receivers are there in each city?":
            """SELECT 
                COALESCE(p."City", r."City") AS "City", 
                COALESCE(p.provider_count, 0) AS provider_count,
                COALESCE(r.receiver_count, 0) AS receiver_count
            FROM (
                SELECT "City", COUNT(*) AS provider_count 
                FROM providers_data 
                GROUP BY "City"
            ) p 
            FULL OUTER JOIN (
                SELECT "City", COUNT(*) AS receiver_count 
                FROM receivers_data 
                GROUP BY "City"
            ) r 
            ON p."City" = r."City"
            ORDER BY "City";""",

        "Which type of food provider contributes the most food?":
            """SELECT "Type", COUNT(*) AS provider_count 
               FROM providers_data 
               GROUP BY "Type" 
               ORDER BY provider_count DESC 
               LIMIT 1;""",

        "What is the contact information of food providers in a specific city?": 
            """SELECT "Name", "Type", "City", "Contact" 
               FROM providers_data 
               WHERE "City" = 'East Sheena';""",

        "Which receivers have claimed the most food?":
            """SELECT r."Name", COUNT(c."Claim_ID") AS total_claims 
               FROM claims_data c 
               JOIN receivers_data r ON c."Receiver_ID" = r."Receiver_ID" 
               GROUP BY r."Name" 
               ORDER BY total_claims DESC;""",

        "What is the total quantity of food available from all providers?":
            """SELECT SUM("Quantity") AS total_food_quantity 
               FROM food_listings_data;""",

        "Which city has the highest number of food listings?":
            """SELECT "Location", COUNT(*) AS listing_count 
               FROM food_listings_data 
               GROUP BY "Location" 
               ORDER BY listing_count DESC 
               LIMIT 1;""",

        "What are the most commonly available food types?":
            """SELECT "Food_Type", COUNT(*) AS food_type_count 
               FROM food_listings_data 
               GROUP BY "Food_Type" 
               ORDER BY food_type_count DESC;""",

        "How many food claims have been made for each food item?":
            """SELECT "Food_ID", COUNT(*) AS claim_count 
               FROM claims_data 
               GROUP BY "Food_ID" 
               ORDER BY claim_count DESC;""",

        "Which provider has had the highest number of successful food claims?":
            """SELECT P."Name" AS Provider_Name, COUNT(C."Claim_ID") AS Successful_Claims_Count
               FROM claims_data AS C
               JOIN food_listings_data AS FL ON C."Food_ID" = FL."Food_ID"
               JOIN providers_data AS P ON FL."Provider_ID" = P."Provider_ID"
               WHERE C."Status" = 'Completed'
               GROUP BY P."Name"
               ORDER BY Successful_Claims_Count DESC
               LIMIT 1;""",

        "What percentage of food claims are completed vs. pending vs. canceled?":
            """SELECT "Status", COUNT(*) AS status_count,
                      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
               FROM claims_data
               GROUP BY "Status"
               ORDER BY percentage DESC;""",

        "What is the average quantity of food claimed per receiver?":
            """SELECT C."Receiver_ID", ROUND(AVG(FL."Quantity"), 2) AS avg_quantity_claimed
               FROM claims_data AS C
               JOIN food_listings_data AS FL ON C."Food_ID" = FL."Food_ID"
               GROUP BY C."Receiver_ID"
               ORDER BY avg_quantity_claimed DESC;""",

        "Which meal type is claimed the most?":
            """SELECT "Meal_Type", SUM("Quantity") AS total_claimed 
               FROM claims_data, food_listings_data 
               GROUP BY "Meal_Type" 
               ORDER BY total_claimed DESC 
               LIMIT 1;""",

        "What is the total quantity of food donated by each provider?":
            """SELECT "Provider_ID", SUM("Quantity") AS total_quantity_donated
               FROM food_listings_data
               GROUP BY "Provider_ID"
               ORDER BY total_quantity_donated DESC;""",

        "Average quantity of food donated per listing by each provider:":
            """SELECT p."Name", AVG(f."Quantity") AS avg_quantity_per_listing
               FROM food_listings_data f
               JOIN providers_data p ON f."Provider_ID" = p."Provider_ID"
               GROUP BY p."Name"
               ORDER BY avg_quantity_per_listing DESC;""",

        "Which receiver has claimed the most quantity of food?":
            """SELECT r."Name" AS Receiver_Name, 
       SUM(fl."Quantity") AS total_claimed
FROM claims_data c
JOIN receivers_data r ON c."Receiver_ID" = r."Receiver_ID"
JOIN food_listings_data fl ON c."Food_ID" = fl."Food_ID"
WHERE c."Status" = 'Completed'
GROUP BY r."Name"
ORDER BY total_claimed DESC
LIMIT 1;
""",

        "Distribution of food listings by food type":
            """SELECT "Food_Type", COUNT(*) AS listing_count
               FROM food_listings_data
               GROUP BY "Food_Type"
               ORDER BY listing_count DESC;""",

        "Total listings still available (unclaimed)":
            """SELECT COUNT(*) AS available_listings
FROM food_listings_data f
LEFT JOIN claims_data c ON f."Food_ID" = c."Food_ID"
WHERE c."Food_ID" IS NULL;
""",

        "Provider with most active listings":
            """SELECT r."Name" AS Receiver_Name, COUNT(DISTINCT f."Provider_ID") AS unique_providers
FROM claims_data c
JOIN food_listings_data f ON c."Food_ID" = f."Food_ID"
JOIN receivers_data r ON c."Receiver_ID" = r."Receiver_ID"
GROUP BY r."Name"
ORDER BY unique_providers DESC
LIMIT 1;
""",

        "Average number of claims per listing":
            """SELECT ROUND(COUNT(*) * 1.0 / (SELECT COUNT(*) FROM food_listings_data), 2) AS avg_claims_per_listing
               FROM claims_data;""",

        "Receiver with claims from most different providers":
            """SELECT r."Name" AS Receiver_Name, COUNT(DISTINCT f."Provider_ID") AS unique_providers
FROM claims_data c
JOIN food_listings_data f ON c."Food_ID" = f."Food_ID"
JOIN receivers_data r ON c."Receiver_ID" = r."Receiver_ID"
GROUP BY r."Name"
ORDER BY unique_providers DESC
LIMIT 1;
;""",

        "Provider-wise claim success rate (%)":
            """SELECT 
  p."Name",
  ROUND(
    SUM(CASE WHEN c."Status" = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(c."Claim_ID"),
    2
  ) AS success_rate
FROM claims_data c
JOIN food_listings_data f ON c."Food_ID" = f."Food_ID"
JOIN providers_data p ON f."Provider_ID" = p."Provider_ID"
GROUP BY p."Name"
ORDER BY success_rate DESC;
""",


"Most Frequently Claimed Food Type":
"""SELECT f."Food_Type", COUNT(c."Claim_ID") AS total_claims
FROM claims_data c
JOIN food_listings_data f ON c."Food_ID" = f."Food_ID"
GROUP BY f."Food_Type"
ORDER BY total_claims DESC
LIMIT 1;""",

" City with Highest Number of Unique Receivers":
"""SELECT r."City", COUNT(DISTINCT r."Receiver_ID") AS total_receivers
FROM receivers_data r
GROUP BY r."City"
ORDER BY total_receivers DESC
LIMIT 1;"""

}

    selected_query_label = st.selectbox("Choose a predefined query to run:", list(queries.keys()) + ["📝 Custom Query"])

    selected = queries.get(selected_query_label, "")
    query_text = selected if isinstance(selected, str) else selected.get("query", "")
    query_input = st.text_area("Edit or enter your SQL query below:", value=query_text, height=200)

    if st.button("Execute Query"):
        try:
            df = pd.read_sql_query(query_input, con=engine)
            st.success("✅ Query executed successfully")
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Query Error: {e}")

# ---------------------- Creator ----------------------
elif page == "Creator":
    st.title("👨‍💻 Meet the Creator")

    st.markdown("""
### 👋 Hello! I'm **Harisankar M**

I'm passionate about using technology to solve real-world problems.  
This project was built to:

- Reduce food waste  
- Connect communities  
- Showcase database-driven data analysis with **Streamlit + PostgreSQL**

**Tech Stack:**
- 🐘 PostgreSQL  
- 🐍 Python + SQLAlchemy  
- 📊 Streamlit for UI

Thanks for visiting this app! 🙏
""")
