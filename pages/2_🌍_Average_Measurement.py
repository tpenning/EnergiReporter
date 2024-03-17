import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Average Measurement", page_icon="🌍")

# Page information/text
st.markdown("# Average Data Measurement")
st.sidebar.header("Average Measurement")
st.write("""
    This page visualizes the energy data average over multiple measurements. 
    Upload your csv files with columns TIME and ENERGY to generate the charts.
    """)


# Generate the mean chart tabs
def generate_mean_charts(mean_df):
    # Restore the TIME from index and rename it
    mean_tdf = mean_df.reset_index().rename(columns={"TIME": "Time (s)", 0: "Energy (J)"})

    # Create a tab element with the different chart variations
    st.subheader("Energy data averages over time:")
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])

    tab_line.line_chart(mean_tdf, x="Time (s)", y="Energy (J)", use_container_width=True)
    tab_area.area_chart(mean_tdf, x="Time (s)", y="Energy (J)", use_container_width=True)
    tab_bar.bar_chart(mean_tdf, x="Time (s)", y="Energy (J)", use_container_width=True)


# Generate the errorband charts
def generate_errorband_charts(mean_data_df, all_data_df):
    # Calculate the std and conf data across the DataFrames
    std_data = all_data_df.std(axis=1)
    conf_data = std_data * 2

    # Combine the data into one time, mean, std/conf DataFrame
    std_combined_data = pd.concat([mean_data_df, std_data], axis=1, keys=["MEAN", "STD"]).reset_index()
    conf_combined_data = pd.concat([mean_data_df, conf_data], axis=1, keys=["MEAN", "CONF"]).reset_index()

    # Create a tab element with the different errorband metrics
    tab_std, tab_conf = st.tabs(["STD Chart", "Conf Chart"])

    tab_std.subheader("Standard deviation chart")
    tab_std.altair_chart(alt.Chart(mean_data_df.reset_index())
                         .mark_line().interactive()
                         .encode(x="TIME", y="0") +
                         alt.Chart(std_combined_data).mark_errorband(extent="ci")
                         .encode(x="TIME", y=alt.Y("MEAN", title="Mean with std"), yError="STD"),
                         use_container_width=True)

    tab_conf.subheader("Confidence intervals chart")
    tab_conf.altair_chart(alt.Chart(mean_data_df.reset_index())
                          .mark_line().interactive()
                          .encode(x="TIME", y="0") +
                          alt.Chart(conf_combined_data).mark_errorband(extent="ci")
                          .encode(x="TIME", y=alt.Y("MEAN", title="Mean with conf"), yError="CONF"),
                          use_container_width=True)


# Upload multiple files
uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

# Process the uploaded files
if uploaded_files:
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
    mean_data = all_data.mean(axis=1)

    # Generate the mean chart tabs and the errorband charts tabs
    generate_mean_charts(mean_data)
    generate_errorband_charts(mean_data, all_data)
