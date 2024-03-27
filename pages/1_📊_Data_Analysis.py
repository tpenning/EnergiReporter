import altair as alt
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st
import streamlit.components.v1 as components
from streamlit_modal import Modal

from help_texts import *
from reader import read_uploaded_files, POWER, TIME

st.set_page_config(page_title="Data Analysis", page_icon="📊")

# Page information/text
st.markdown("# Data Analysis")
st.write("""
    This page visualizes the energy data average over a single measurement or an average of measurements. 
    Upload your CSV file(s) adhering to the format specified on the home page to generate the charts.
    """)


# TODO: Add a table of total energy consumptions
def show_mean_charts(single, mean_df, total_energy):
    # Retrieve the time column from the index
    mean_tdf = mean_df.reset_index()

    # Show the header of this chart and information
    st.subheader(f"Power consumption {'' if single else 'average '}over time:")

    # Show the (average) total energy used and average power consumption
    st.info(f"{'Total' if single else 'Average total'} energy usage: {total_energy}J")

    # Create a tab element with the different chart variations
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])
    tab_line.line_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_area.area_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_bar.bar_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)

    # Create help modal
    mean_chart_modal = Modal("Inserting files", key="mean_chart_modal")
    open_modal = st.button("Help", key="mean_chart_modal")

    # Open modal if clicked
    if open_modal:
        with mean_chart_modal.container():
            st.markdown(helptekst_mean_chart_modal)

    st.markdown("---")


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

        # Create help modal
        errorband_chart_modal = Modal("Inserting files", key="errorband_chart_modal")
        open_modal = st.button("Help", key="errorband_chart_modal")

        # Open modal if clicked
        if open_modal:
            with errorband_chart_modal.container():
                st.markdown(helptekst_errorband_chart_modal)

        st.markdown("---")


def normality_check(names, orv_pdfs_values):
    # Calculate the p values and get the corresponding normality values
    p_values = list(map(lambda data: stats.shapiro(data).pvalue, orv_pdfs_values))
    normality_values = list(map(lambda pval: str(pval > 0.05), p_values))

    # Display the p and normality values in a DataFrame
    normality_df = pd.DataFrame(data={"NAME": names, "NORMAL": normality_values, "P-VALUE": p_values})
    st.dataframe(normality_df, hide_index=True)


# TODO: Add the average (so total) boxplot,
#  Or for average power boxplot (like in our blogpost)
def generate_power_boxplot_charts(names, orv_pdfs_values):
    # TODO: Add name and title
    # Create the violin plots of the data files
    fig = plt.figure()
    plt.violinplot(dataset=orv_pdfs_values, showmedians=True)
    plt.xticks(range(1, len(names) + 1), names)

    components.html(mpld3.fig_to_html(fig), height=600)

    # Create help modal
    boxplot_modal = Modal("Inserting files", key="boxplot_modal")
    open_modal = st.button("Help", key="boxplot_modal")

    # Open modal if clicked
    if open_modal:
        with boxplot_modal.container():
            st.markdown(helptekst_boxplot_modal)
    st.markdown("---")


# TODO: Information icon for the plots
# The main script to run but scoped now
def main():
    # Upload multiple files
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    # Create help modal
    insert_files_modal = Modal("Inserting files", key="insert_files_modal")
    open_modal = st.button("Help", key="insert_files_modal")

    # Open modal if clicked
    if open_modal:
        with insert_files_modal.container():
            st.markdown(helptekst_insert_files_analysis)

    # Process the uploaded files
    if uploaded_files:
        st.markdown("---")
        # Retrieve the useful data formats and information from the uploaded files
        power_df, mean_df, total_energy, names, stat_pdfs = read_uploaded_files(uploaded_files)

        # Whether a single file was uploaded, this is handled in each chart for all changes
        single = len(uploaded_files) == 1

        # Show the power data analysis charts
        show_mean_charts(single, mean_df, total_energy)
        show_errorband_charts(single, mean_df, power_df)

        # Perform outlier removal for the data statistics
        st.markdown("""
            The information below reports statistics about the power data. 
            A common convention is to apply outlier removal on the data which we provide below.
            Set the number of standard deviations to keep included (default 3).
            """)
        orv = st.number_input("Outlier removal:", value=3, step=1, min_value=1)
        orv_pdfs_values = [stat_pdf[(np.abs(stats.zscore(stat_pdf)) < orv)].tolist() for stat_pdf in stat_pdfs]

        # Show the data statistics charts
        normality_check(names, orv_pdfs_values)
        generate_power_boxplot_charts(names, orv_pdfs_values)


# Run the main script
main()
