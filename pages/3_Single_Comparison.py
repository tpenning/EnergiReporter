import streamlit as st
import pandas as pd

st.set_page_config(page_title="Single Comparison", page_icon="📊")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Generate the energy over time line-chart
    st.subheader("Data Visualization:")
    st.line_chart(df, x="TIME", y="ENERGY")
