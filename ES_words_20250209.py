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
else:
    st.success(f"✅ Successfully loaded {files_loaded} CSV files.")

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

        # 🔹 Add a dashed trend line (7-day moving average)
        df_word['trend'] = df_word['count'].rolling(window=7, min_periods=1).mean()

        fig.add_trace(
            go.Scatter(
                x=df_word['date'], 
                y=df_word['trend'], 
                mode='lines', 
                name="Trend (7-day Avg)", 
                line=dict(dash='dash', color='red', width=2)  # Dashed red line
            )
        )

        # 🎯 Show the updated plot in Streamlit
        st.plotly_chart(fig)

    else:
        st.warning(f"❌ The word '{word}' was not found in the dataset.")

# 🎨 Streamlit UI
st.title("📊 Word Popularity Over Time")

word = st.text_input("🔍 Enter a word to track:")

if word:
    plot_word_popularity(word)

#-------------------------------------
# Show a summary table
# Compute the Most Popular Words Summary


if not df_all.empty:
    st.subheader("📈 Most Popular Words Summary (Last 3 Months + Total)")

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

    # 🔢 Add a "Total" column summing **ALL MONTHS** from the full dataset
    total_counts = df_all.groupby("word")["count"].sum()
    recent_counts["Total"] = total_counts

    # 🎯 Sort by the total count across all months
    recent_counts = recent_counts.sort_values(by="Total", ascending=False)

    # 📌 Show only the top 20 words
    top_20_recent = recent_counts.head(20)

    # 🎨 Custom Styling Function
    def custom_style(styler):
        # Set styles for the whole dataframe
        styler.set_properties(**{
            'background-color': '#E3F2FD',  # Light blue background for all cells
            'color': '#000000',  # Black text for contrast
            'border-color': '#DDDDDD'  # Light border
        })

        # Apply a blue color to the "word" column
        styler.applymap(lambda _: 'background-color: #1f77b4; color: white;', subset=pd.IndexSlice[:, ['word']])

        # Apply a blue header color for month columns and total
        header_cols = top_20_recent.columns.tolist()
        styler.applymap(lambda _: 'background-color: #1f77b4; color: white;', subset=pd.IndexSlice[:, header_cols])

        return styler

    # 📊 Apply Styling and Display
    styled_df = top_20_recent.style \
        .format("{:,}") \
        .pipe(custom_style)

    st.dataframe(styled_df)

else:
    st.warning("No data available to display.")

 

