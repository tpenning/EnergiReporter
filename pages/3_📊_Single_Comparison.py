import pandas as pd
import streamlit as st

st.set_page_config(page_title="Single Comparison", page_icon="📊")

# Page information/text
st.markdown("# Single Data Comparison")
st.sidebar.header("Single Comparison")
st.write("""
    This page compares the energy data between 2 measurements. 
    Upload your csv files with columns TIME and ENERGY to generate the charts.
    """)


# Function to generate comparison charts
def generate_compare_charts(compare_df):
    # Restore the TIME from index and rename it
    compare_tdf = compare_df.reset_index().rename(columns={"TIME": "Time (s)"})

    # Create a tab element with the different chart variations
    st.subheader("Energy data over time comparison:")
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])

    tab_line.line_chart(compare_tdf, x="Time (s)", use_container_width=True)
    tab_area.area_chart(compare_tdf, x="Time (s)", use_container_width=True)


# File uploaders for both files
uploaded_file1 = st.file_uploader("Upload first CSV file", type=["csv"])
uploaded_file2 = st.file_uploader("Upload second CSV file", type=["csv"])

if uploaded_file1 is not None and uploaded_file2 is not None:
    # Read CSV files into DataFrames
    df1 = pd.read_csv(uploaded_file1).set_index("TIME")
    df2 = pd.read_csv(uploaded_file2).set_index("TIME")
    dfs = pd.concat([df1["ENERGY"], df2["ENERGY"]], axis=1, keys=["ENERGY1", "ENERGY2"])

    # Generate the chart tabs
    generate_compare_charts(dfs)
