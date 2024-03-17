import streamlit as st
import pandas as pd

st.set_page_config(page_title="Average Measurement", page_icon="🌍")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Generate the energy over time line-chart
    st.subheader("Data Visualization:")
    chart_data = df.set_index(df.columns[0])
    st.line_chart(chart_data)
