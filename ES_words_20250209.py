#pip install pandas plotly

import os
import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import interact_manual
import streamlit as st
import plotly.graph_objects as go

# 📂 Folder containing CSV files
folder_path = "data"

# Load all CSV files and combine them into a single DataFrame
data = []
files_loaded = 0

for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path)
            
            # Ensure necessary columns exist
            if 'word' in df.columns and 'count' in df.columns:
                # Extract date from filename (assumed format: 'word_counts_YYYYMMDD_YYYYMMDD.csv')
                try:
                    date_str = file.split('_')[2]  # Extract YYYYMMDD from filename
                    date = pd.to_datetime(date_str, format='%Y%m%d')
                    df['date'] = date
                    data.append(df)
                    files_loaded += 1
                except Exception as e:
                    st.warning(f"Skipping {file}: Incorrect date format. Error: {e}")
            else:
                st.warning(f"Skipping {file}: Missing required columns.")
        except Exception as e:
            st.error(f"Error loading {file}: {e}")

# Check if any data was loaded
if not data:
    st.error("❌ No valid data was loaded. Please check your CSV files.")

# Combine all dataframes
df_all = pd.concat(data, ignore_index=True) if data else pd.DataFrame()

# Function to plot word popularity
def plot_word_popularity(word):
    df_word = df_all[df_all['word'].str.lower() == word.lower()]  # Case-insensitive match
    
    if not df_word.empty:
        # 🛠️ Aggregate counts to remove duplicate points
        df_word = df_word.groupby('date', as_index=False)['count'].sum()

        # 🛠️ Ensure dates are sorted properly
        df_word = df_word.sort_values(by="date")

        # 📈 Create the main line chart
        fig = px.line(df_word, x='date', y='count', 
                      title=f'📊 Popularity of "{word}" Over Time', 
                      markers=True)

        # 🔹 Add a dashed trend line (7-month moving average)
        df_word['trend'] = df_word['count'].rolling(window=12, min_periods=1).mean()

        fig.add_trace(
            go.Scatter(
                x=df_word['date'], 
                y=df_word['trend'], 
                mode='lines', 
                name="Trend (12-Month Avg)", 
                line=dict(dash='dash', color='red', width=2)  # Dashed red line
            )
        )

        # 🎯 Show the updated plot in Streamlit
        st.plotly_chart(fig)

    else:
        st.warning(f"❌ The word '{word}' was not found in the dataset.")

# 🎨 Streamlit UI
st.title("📊 Spanish Word Popularity ")

word = st.text_input("🔍 Enter a word to view results:")

if word:
    plot_word_popularity(word)

#-------------------------------------
# Show a summary table
# Compute the Most Popular Words Summary
# -------------------------------------
# Show a summary table
if not df_all.empty:
    st.subheader("📈 Most Popular Words Summary (Last 4 Months + Total)")

    # 🛠️ Ensure 'date' column is in datetime format
    df_all["date"] = pd.to_datetime(df_all["date"], errors="coerce")

    # 🎯 Find the latest date in the dataset
    latest_date = df_all["date"].max()

    # 📆 Determine the three most recent months
    three_months_ago = latest_date - pd.DateOffset(months=3)

    # 📌 Filter data to keep only the last 3 months
    df_recent = df_all[df_all["date"] >= three_months_ago]

    # 🏆 Aggregate total counts for each word in the last 3 months
    recent_counts = df_recent.pivot_table(
        index="word",
        columns=df_recent["date"].dt.to_period("M"),  # Group by month
        values="count",
        aggfunc="sum",
        fill_value=0  # Fill missing months with 0 count
    )

    # Compute the monthly average count for each word
    num_months = len(recent_counts.columns) - 1  # Exclude "Total" column
    recent_counts["Average"] = recent_counts.iloc[:, :-1].sum(axis=1) / num_months  # Compute average over recent mon
    
    # Add a "Total" column summing **ALL MONTHS** from the full dataset
    total_counts = df_all.groupby("word")["count"].sum()
    recent_counts["Total"] = total_counts

    # Sort by the total count across all months
    recent_counts = recent_counts.sort_values(by="Total", ascending=False)

    # 📌 Show only the top 20 words
    top_20_recent = recent_counts.head(20)

    # 🔹 Reset index so "word" is a column
    top_20_recent = top_20_recent.reset_index()

    # ✅ Fix: Remove `.style` and use `st.dataframe()`
    # ✅ Apply formatting ONLY to numeric columns
    st.dataframe(
        top_20_recent.style.format({
            "Total": "{:,}",  # Apply comma formatting
            "Average": "{:,.0f}",  # Format average with two decimal places
            **{col: "{:,}" for col in top_20_recent.columns if col not in ["word", "Average"]}
        }),
        height=(len(top_20_recent) + 1) * 35  # Adjust row height dynamically
    )


else:
    st.warning("No data available to display.")
