#pip install pandas plotly

import os
import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import interact_manual
import streamlit as st

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
        fig = px.line(df_word, x='date', y='count', 
                      title=f'Popularity of "{word}" Over Time', 
                      markers=True)
        st.plotly_chart(fig)  # ✅ Streamlit-friendly way to show graphs
    else:
        st.warning(f"❌ The word '{word}' was not found in the dataset.")

# 🎨 Streamlit UI
st.title("📊 Word Popularity Over Time")

word = st.text_input("🔍 Enter a word to track:")

if word:
    plot_word_popularity(word)

# Show a summary table
if not df_all.empty:
    st.subheader("📈 Most Popular Words Summary")
    popular_words = df_all.groupby("word")["count"].sum().reset_index()
    popular_words = popular_words.sort_values(by="count", ascending=False)
    
    st.write(popular_words)  # ✅ Use st.write() instead of print()

