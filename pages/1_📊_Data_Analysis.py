import altair as alt
import pandas as pd
import streamlit as st

from reader import read_uploaded_files

st.set_page_config(page_title="Data Analysis", page_icon="📊")

# Page information/text
st.markdown("# Data Analysis")
st.sidebar.header("Data Analysis")
st.write("""
    This page visualizes the energy data average over a single measurement or an average of measurements. 
    Upload your csv file(s) with columns TIME and ENERGY to generate the charts.
    """)

# Easy to use/rename variables
TIME = "Time (s)"
POWER = "Power (W)"


def show_mean_charts(single, mean_df, total_energy):
    # Retrieve the time column from the index
    mean_tdf = mean_df.reset_index()

    # Show the header of this chart and information
    st.subheader(f"Power consumption {'' if single else 'average '}over time:")

    # Show the (average) total energy used and average power consumption
    st.info(f"{'Total' if single else 'Average total'} energy usage: {total_energy}J")
    # TODO: Add average power consumption (requires more complex math than first intuition)
    # st.write(f"Average power consumption: {00000}W")

    # Create a tab element with the different chart variations
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])
    tab_line.line_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_area.area_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_bar.bar_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)


def show_errorband_charts(single, mean_df, power_df):
    # Only show these if not just a single file
    if not single:
        # Get a time column mean df and a time indexed power column
        mean_tdf = mean_df.reset_index()
        mean_pdf = mean_df[POWER]

        # Calculate the std and conf data across the DataFrames
        std_data = power_df.std(axis=1)
        conf_data = std_data * 2

        # Combine the data into one time, mean, std/conf DataFrame
        std_df = pd.concat([mean_pdf, std_data], axis=1, keys=["MEAN", "STD"]).reset_index()
        conf_df = pd.concat([mean_pdf, conf_data], axis=1, keys=["MEAN", "CONF"]).reset_index()

        # Create a tab element with the different errorband metrics
        st.subheader(f"Power consumption {'average ' if single else ''}over time with error bands:")
        tab_std, tab_conf = st.tabs(["STD Chart", "Conf Chart"])

        # Add the tab charts with the error bands
        tab_std.altair_chart(alt.Chart(mean_tdf)
                             .mark_line().interactive()
                             .encode(x=TIME, y=POWER) +
                             alt.Chart(std_df).mark_errorband(extent="ci")
                             .encode(x=TIME, y=alt.Y("MEAN", title=POWER), yError="STD"),
                             use_container_width=True)
        tab_conf.altair_chart(alt.Chart(mean_tdf)
                              .mark_line().interactive()
                              .encode(x=TIME, y=POWER) +
                              alt.Chart(conf_df).mark_errorband(extent="ci")
                              .encode(x=TIME, y=alt.Y("MEAN", title=POWER), yError="CONF"),
                              use_container_width=True)


# TODO: Add the average (so total) boxplot,
#  Or for average power boxplot (like in our blogpost)
def generate_power_boxplot_charts(power_df):
    # Drop the time index to only get the power data
    pdf = power_df.reset_index(drop=True)

    # Melt the dataframe to long format where each row is indicated by the run name
    melted_pdf = pdf.melt(var_name="File", value_name=POWER)

    # Create the boxplot chart
    st.subheader("Power intervals boxplots:")
    chart = alt.Chart(melted_pdf).mark_boxplot().interactive().encode(x="File:O", y=f"{POWER}:Q")
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


# TODO: Information icon for the plots
# The main script to run but scoped now
def main():
    # Upload multiple files
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    # Process the uploaded files
    if uploaded_files:
        # Retrieve the useful data formats and information from the uploaded files
        power_df, mean_df, total_energy = read_uploaded_files(uploaded_files)
        single = len(uploaded_files) == 1

        # Show the data analysis charts (single indicated changes handled internally to easily keep the charts order)
        show_mean_charts(single, mean_df, total_energy)
        show_errorband_charts(single, mean_df, power_df)
        generate_power_boxplot_charts(power_df)


# Run the main script
main()
