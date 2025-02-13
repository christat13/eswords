#pip install pandas plotly

import os
import pandas as pd
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display
from ipywidgets import interact_manual
import streamlit as st

# Folder containing CSV files
#folder_path = r"C:\\Users\\chris\\TLDz\\TLDz - Documents\\reg_word_analysis\\"
folder_path = r"data"

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
                # Extract date from filename format 'word_counts_YYYYMMDD_YYYYMMDD.csv'
                try:
                    date_str = file.split('_')[2]  # Extract YYYYMMDD from filename
                    date = pd.to_datetime(date_str, format='%Y%m%d')
                    df['date'] = date
                    data.append(df)
                    files_loaded += 1
                except Exception:
                    print(f"Skipping {file}, incorrect date format.")
            else:
                print(f"Skipping {file}, missing required columns.")
        except Exception as e:
            print(f"Error loading {file}: {e}")

# Check if any data was loaded
if not data:
    print("No valid data was loaded. Please check your CSV files.")
else:
    print(f"Loaded {files_loaded} CSV files successfully.")

# Combine all dataframes
df_all = pd.concat(data, ignore_index=True)

# Function to plot word popularity
def plot_word_popularity(word):
    df_word = df_all[df_all['word'] == word]
    if not df_word.empty:
        fig = px.line(df_word, x='date', y='count', title=f'Popularity of "{word}" Over Time', markers=True)
        fig.show()
    else:
        print("Word not found in dataset.")

# Use interact_manual() for dropdown selection
st.title("Word Popularity Over Time")

word = st.text_input("Enter a word to track:")
if word:
    plot_word_popularity(word)

# Show a summary table
print("Most Popular Words Summary:")
popular_words = df_all.groupby("word")["count"].sum().reset_index()
popular_words = popular_words.sort_values(by="count", ascending=False)
display(popular_words)
