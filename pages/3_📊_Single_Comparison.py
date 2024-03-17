import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Single Comparison", page_icon="📊")

# Page information/text
st.markdown("# Single Data Comparison")
st.sidebar.header("Single Comparison")
st.write("""
    This page compares the energy data between 2 measurements. 
    Upload your csv files with columns TIME and ENERGY to generate the plots.
    """)


# Function to generate comparison charts
def generate_compare_charts(data1, data2):
    st.subheader("Comparison Chart:")
    chart = alt.Chart(data1).mark_line(color="blue") \
                .encode(x="TIME", y="ENERGY") + \
                alt.Chart(data2).mark_line(color="red") \
                .encode(x="TIME", y="ENERGY")
    st.altair_chart(chart, use_container_width=True)


# File uploader for first file
uploaded_file1 = st.file_uploader("Upload first CSV file", type=['csv'])

# File uploader for second file
uploaded_file2 = st.file_uploader("Upload second CSV file", type=['csv'])

if uploaded_file1 is not None and uploaded_file2 is not None:
    # Read CSV files into DataFrames
    df1 = pd.read_csv(uploaded_file1)
    df2 = pd.read_csv(uploaded_file2)

    # Generate the chart tabs
    generate_compare_charts(df1, df2)
