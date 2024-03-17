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
    # Rename the columns and add a subheader
    energy_time_df = tdf.rename(columns={"TIME": "Time (s)", "ENERGY": "Energy (J)"})
    st.subheader("Energy data over time:")

    # Create a tab element with the different chart variations
    tab_line, tab_area, tab_bar = st.tabs(["📈 Chart", "Area Chart", "Bar Chart"])

    tab_line.subheader("A tab with a line chart")
    tab_line.line_chart(energy_time_df, x="Time (s)", y="Energy (J)")

    tab_area.subheader("A tab with an area chart")
    tab_area.area_chart(energy_time_df, x="Time (s)", y="Energy (J)")

    tab_bar.subheader("A tab with a bar chart")
    tab_bar.bar_chart(energy_time_df, x="Time (s)", y="Energy (J)")


def generate_boxplot_chart(df):
    # source = data.population.url

    print(df.values)

    l = []
    for i in range(len(df.values) - 1):
        l.append(df.values[i][1] / (df.values[i+1][0] - df.values[i][0]))

    pdf = pd.DataFrame(l, columns=['Power (W)'])

    chart = alt.Chart(pdf).mark_boxplot(extent='min-max').encode(y="Power (W)").interactive()

    st.altair_chart(chart, theme="streamlit", use_container_width=True)

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Generate the energy over time chart tabs
    generate_et_charts(df)

    generate_boxplot_chart(df)
