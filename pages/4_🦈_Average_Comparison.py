import pandas as pd
import streamlit as st

st.set_page_config(page_title="Average Comparison", page_icon="🦈")

# Page information/text
st.markdown("# Average Data Comparison")
st.sidebar.header("Average Comparison")
st.write("""
    This page compares the energy data between 2 sets of measurements. 
    Upload your csv files with columns TIME and ENERGY to generate the charts.
    """)


# Generate the compare mean chart tabs
def generate_compare_mean_charts(means_df):
    # Restore the TIME from index and rename it
    means_tdf = means_df.reset_index().rename(columns={"TIME": "Time (s)"})

    # Create a tab element with the different chart variations
    st.subheader("Data means chart:")
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])

    tab_line.line_chart(means_tdf, x="Time (s)", use_container_width=True)
    tab_area.area_chart(means_tdf, x="Time (s)", use_container_width=True)


# File uploaders for both sets of files
uploaded_files1 = st.file_uploader("Upload first set of CSV files", type=["csv"], accept_multiple_files=True)
uploaded_files2 = st.file_uploader("Upload second set of CSV files", type=["csv"], accept_multiple_files=True)

# Process the uploaded sets of files
if uploaded_files1 and uploaded_files2:
    # Initialize a list to store the all datas and mean datas
    all_datas = []
    mean_datas = []

    # Iterate over the uploaded sets of files
    for uploaded_files in [uploaded_files1, uploaded_files2]:
        # Initialize a list to store the DataFrames
        dfs = []

        # Iterate over the uploaded files
        for uploaded_file in uploaded_files:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)

            # Index by TIME and add the ENERGY column to the list
            df.set_index("TIME", inplace=True)
            dfs.append(df["ENERGY"])

        # Concatenate the DataFrames along the ENERGY columns and calculate the mean data across the DataFrames
        all_data = pd.concat(dfs, axis=1, keys=[f"ENERGY{i}" for i in range(1, len(dfs) + 1)])
        all_datas.append(all_data)
        mean_datas.append(all_data.mean(axis=1))

    # Concatenate the DataFrames along the ENERGY columns and generate the compare mean chart tabs with it
    mean_dfs = pd.concat(dfs, axis=1, keys=[f"ENERGY{i}" for i in range(1, len(dfs) + 1)])
    generate_compare_mean_charts(mean_dfs)
