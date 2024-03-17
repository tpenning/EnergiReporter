import altair as alt
import pandas as pd
import streamlit as st

# Page title
st.set_page_config(page_title="Single Measurement", page_icon="📈")

# Page information/text
st.markdown("# Single Data Measurement")
st.sidebar.header("Single Measurement")
st.write("""
    This page visualizes the energy data from a single measurement. 
    Upload your csv file with columns TIME and ENERGY to generate the charts.
    """)


# Generate the chart tabs
def generate_et_charts(tdf):
    # Rename the columns
    energy_time_df = tdf.rename(columns={"TIME": "Time (s)", "ENERGY": "Energy (J)"})

    # Create a tab element with the different chart variations
    st.subheader("Energy data over time:")
    tab_line, tab_area, tab_bar = st.tabs(["📈 Chart", "Area Chart", "Bar Chart"])

    tab_line.line_chart(energy_time_df, x="Time (s)", y="Energy (J)", use_container_width=True)
    tab_area.area_chart(energy_time_df, x="Time (s)", y="Energy (J)", use_container_width=True)
    tab_bar.bar_chart(energy_time_df, x="Time (s)", y="Energy (J)", use_container_width=True)


def generate_power_boxplot_chart(tdf):
    # Calculate the power values at all time intervals
    power_values = []
    for i in range(len(df.values) - 1):
        power_values.append(df.values[i][1] / (df.values[i+1][0] - df.values[i][0]))
    pdf = pd.DataFrame(data={"Power (W)": power_values})

    # Create the boxplot chart
    st.subheader("Energy data over time:")
    chart = alt.Chart(pdf).mark_boxplot(extent="min-max").encode(y="Power (W)").interactive()
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Generate the energy over time chart tabs and the power intervals boxplot
    generate_et_charts(df)
    generate_power_boxplot_chart(df)
