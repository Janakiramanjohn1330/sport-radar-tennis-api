import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px

# Connect to the SQL database
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="Janakiramanjohn1330@",
    database="Tennis"
) 
mycursor = conn.cursor()

# Sidebar - Navigation
st.sidebar.title("Dashboard")
menu = st.sidebar.selectbox(
    "Go to:",
    ["Homepage Dashboard", "Search Competitors", "Competitor Details", "Country Analysis", "Leaderboards"]
)

# Homepage Dashboard
if menu == "Homepage Dashboard":
    st.write("# SPORTS RADAR API")
    st.subheader('*Summary about the title:*')
    st.markdown("""
    SportRadar's API provides comprehensive tennis data, including match stats, player performance, and tournament insights, enabling advanced analytics and predictive modeling. It empowers users to track trends, optimize strategies, and gain actionable insights for sports analysis. :trophy: :tennis:
    """)

    # Metrics
    mycursor.execute("SELECT COUNT(*) FROM competitors")
    total_competitors = mycursor.fetchone()[0]
    st.metric("TOTAL COMPETITORS", total_competitors)

    mycursor.execute("SELECT COUNT(DISTINCT country) FROM competitors")
    countries_represented = mycursor.fetchone()[0]
    st.metric("COUNTRY REPRESENTED", countries_represented)

    mycursor.execute("SELECT MAX(points) FROM competitor_rankings")
    highest_points = mycursor.fetchone()[0]
    st.metric("HIGHEST POINTS", highest_points)

# Search Competitors
elif menu == "Search Competitors":
    st.header("Search Competitors")

    # Search filters
    competitor_name = st.text_input("SEARCH COMPETITOR BY NAME")
    rank_range = st.slider("FILTER BY RANK RANGE", 1, 500, (1, 50))
    points_threshold = st.number_input("POINTS THRESHOLD", min_value=0, step=1)

    # Query
    query1 = f"""
    SELECT c.competitor_id, c.name_comp, c.country, r.ranks, r.points
    FROM competitors c
    JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
    WHERE c.name_comp LIKE '%{competitor_name}%'
    AND r.ranks BETWEEN {rank_range[0]} AND {rank_range[1]}
    AND r.points >= {points_threshold}
    ORDER BY r.points DESC
    """
    mycursor.execute(query1)
    competitors = mycursor.fetchall()

    # Display results
    if competitors:
        df_competitors = pd.DataFrame(
            competitors, 
            columns=["Competitor ID", "Name", "Country", "Rank", "Points"]
        )
        st.dataframe(df_competitors)
    else:
        st.write("No competitors found.")

# Competitor Details
elif menu == "Competitor Details":
    st.header("Competitor Details Viewer")

    # Dropdown to select a competitor
    mycursor.execute("SELECT name_comp FROM competitors")
    competitors_list = [row[0] for row in mycursor.fetchall()]
    selected_competitor = st.selectbox("Select a competitor:", competitors_list)

    # Query competitor details
    if selected_competitor:
        query2 = f"""
        SELECT r.ranks,movement, r.competitions_played, c.country
        FROM competitors c
        JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
        WHERE c.name_comp = '{selected_competitor}'
        """
        mycursor.execute(query2)
        details = mycursor.fetchone()

        if details:
            rank, movement, competitions_played, country = details
            st.subheader(f"Details for {selected_competitor}")
            st.write(f"**Rank:** {rank}")
            st.write(f"**Movement:** {movement}")
            st.write(f"**Competitions Played:** {competitions_played}")
            st.write(f"**Country:** {country}")
        else:
            st.error("No details found for the selected competitor.")

# Country Analysis
elif menu == "Country Analysis":
    st.header("Country-Wise Analysis")

    # Query to list countries with total competitors and average points
    query3 = """
    SELECT c.country, COUNT(c.competitor_id) AS total_competitors, AVG(r.points) AS avg_points
    FROM competitors c
    JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
    GROUP BY c.country
    ORDER BY total_competitors DESC
    """
    mycursor.execute(query3)
    country_data = mycursor.fetchall()

    # Display results
    df_country = pd.DataFrame(country_data, columns=["Country", "Total Competitors", "Average Points"])
    st.dataframe(df_country)

    # Visualization
    fig = px.bar(df_country, x="Country", y="Total Competitors", color="Average Points", title="Country-Wise Analysis")
    st.plotly_chart(fig)

# Leaderboards
elif menu == "Leaderboards":
    st.header("Leaderboards")

    # Top-ranked competitors
    query4 = """
    SELECT c.name_comp, c.country, r.ranks
    FROM competitors c
    JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
    ORDER BY r.ranks ASC
    LIMIT 10
    """
    mycursor.execute(query4)
    top_ranked = mycursor.fetchall()
    df_top_ranked = pd.DataFrame(top_ranked, columns=["Name", "Country", "Rank"])
    st.subheader("Top-Ranked Competitors")
    st.dataframe(df_top_ranked)

    # Competitors with the highest points
    query5 = """
    SELECT c.name_comp, c.country, r.points
    FROM competitors c
    JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
    ORDER BY r.points DESC
    LIMIT 10
    """
    mycursor.execute(query5)
    top_points = mycursor.fetchall()
    df_top_points = pd.DataFrame(top_points, columns=["Name", "Country", "Points"])
    st.subheader("Competitors with the Highest Points")
    st.dataframe(df_top_points)
