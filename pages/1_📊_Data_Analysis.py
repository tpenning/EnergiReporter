import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import statistics
import streamlit as st
from streamlit_modal import Modal

from help_texts import *
from reader import read_uploaded_files, POWER, TIME

st.set_page_config(page_title="Data Analysis", page_icon="📊")

# Page information/text
st.markdown("# Data Analysis")
st.markdown("""
    This page visualizes the energy data average over a single measurement or an average of measurements. 
    Upload your CSV file(s) adhering to the format specified on the home page to generate the charts.
    """)


def show_mean_charts(single, mean_df, names, total_energies):
    """
    This method shows the mean power consumption of all the files in various chart formats. Along with this
    it displays extra information about the average energy usage and the totals of each file.

    :param single: Whether a single file was uploaded
    :param mean_df: The DataFrame with the mean data
    :param names: The names of the uploaded files
    :param total_energies: The list of total energy usage of each file
    """
    # Retrieve the time column from the index
    mean_tdf = mean_df.reset_index()

    # Set the columns for the subheader and information icon
    header, help_modal = st.columns([10, 1])

    # Show the header of this chart and information
    header.subheader(f"Power consumption {'' if single else 'average '}over time:")

    # Create help modal
    mean_chart_modal = Modal("Power mean charts", key="mean_chart_modal")
    open_modal = help_modal.button("❔", key="mean_chart_modal")
    if open_modal:
        with mean_chart_modal.container():
            st.markdown(help_text_mean_chart_modal)

    # Show the (average) total energy used and average power consumption
    st.info(f"{'Total' if single else 'Average total'} energy usage: {round(statistics.mean(total_energies), 2)}J")

    # Create a tab element with the different chart variations
    tab_line, tab_area, tab_bar = st.tabs(["Line Chart", "Area Chart", "Bar Chart"])
    tab_line.line_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_area.area_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)
    tab_bar.bar_chart(mean_tdf, x=TIME, y=POWER, use_container_width=True)

    # Show a DataFrame with the total energy consumption for each file, if there are multiple
    if not single:
        st.markdown("Total energy consumption of all the uploaded files:")
        energy_usage_df = pd.DataFrame(data={"FILE": names,
                                             "TOTAL ENERGY": [f"{round(te, 2)}J" for te in total_energies]})
        st.dataframe(energy_usage_df, hide_index=True)
    st.markdown("---")


def show_errorband_charts(single, mean_df, power_df):
    """
    This method shows the mean power consumption of all the files with std and confidence intervals in
    various chart formats.

    :param single: Whether a single file was uploaded
    :param mean_df: The DataFrame with the mean data
    :param power_df: The DataFrame with all the files' data
    """
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

        # Set the columns for the subheader and information icon
        header, help_modal = st.columns([10, 1])

        # Show the header of this chart and information
        header.subheader(f"Power consumption average over time with error bands:")

        # Create help modal
        errorband_chart_modal = Modal("Power errorband charts", key="errorband_chart_modal")
        open_modal = help_modal.button("❔", key="errorband_chart_modal")
        if open_modal:
            with errorband_chart_modal.container():
                st.markdown(help_text_errorband_chart_modal)

        # Create a tab element with the different errorband metrics
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
        st.markdown("---")


def normality_check(names, orv_pdfs_values):
    """
    Perform the normality checks of the individual data files and all files combined and display them.

    :param names: The names of the uploaded files
    :param orv_pdfs_values: The outlier removed values of all the files
    """
    # Calculate the p values and get the corresponding normality values
    p_values = list(map(lambda data: stats.shapiro(data).pvalue, orv_pdfs_values))
    normality_values = list(map(lambda pval: str(pval > 0.05), p_values))

    # Display the p and normality values in a DataFrame
    normality_df = pd.DataFrame(data={"FILE": names, "NORMAL": normality_values, "P-VALUE": p_values})
    st.dataframe(normality_df, hide_index=True)


def generate_power_violin_charts(names, orv_pdfs_values):
    """
    Generate the violin charts of the individual data files and all files combined and display them.

    :param names: The names of the uploaded files
    :param orv_pdfs_values: The outlier removed values of all the files
    """
    # Create the violin plots of the data files
    plt.violinplot(dataset=orv_pdfs_values, showmedians=True)
    plt.ylabel("Power (W)")
    plt.xlabel("File")
    plt.xticks(range(1, len(names) + 1), labels=names)

    st.pyplot(plt.gcf())
    st.markdown("---")


# The main script to run but scoped now
def main():
    """
    The file uploader with some help information is displayed. Then when one or more files is uploaded all
    the data analysis charts and information is called to be displayed.
    """
    # Upload multiple files
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    # Create help modal
    insert_files_modal = Modal("Inserting files", key="insert_files_modal")
    open_modal = st.button("❔", key="insert_files_modal")
    if open_modal:
        with insert_files_modal.container():
            st.markdown(help_text_insert_files_analysis)

    # Process the uploaded files
    if uploaded_files:
        st.markdown("---")
        # Retrieve the useful data formats and information from the uploaded files
        power_df, mean_df, total_energies, names, stat_pdfs = read_uploaded_files(uploaded_files)

        # Whether a single file was uploaded, this is handled in each chart for all changes
        single = len(uploaded_files) == 1

        # Show the power data analysis charts
        show_mean_charts(single, mean_df, names, total_energies)
        show_errorband_charts(single, mean_df, power_df)

        # Set the columns for the subheader and information icon
        header, help_modal = st.columns([10, 1])
        header.subheader("Data distribution of Power")

        # Create help modal
        boxplot_modal = Modal("Power data distribution", key="boxplot_modal")
        open_modal = help_modal.button("❔", key="boxplot_modal")
        if open_modal:
            with boxplot_modal.container():
                st.markdown(help_text_boxplot_modal)

        # Perform outlier removal for the data statistics
        st.markdown("""
            The information below reports statistics about the power data. 
            A common convention is to apply outlier removal on the data which we provide below.
            Set the number of standard deviations to keep included (default 3).
            """)
        orv = st.number_input("Outlier removal:", value=3, step=1, min_value=1)
        orv_pdfs_values = [stat_pdf[(np.abs(stats.zscore(stat_pdf)) < orv)].tolist() for stat_pdf in stat_pdfs]

        orv_pdfs_values.append([x for xs in orv_pdfs_values for x in xs])
        names.append("Total")

        # Show the data statistics charts
        normality_check(names, orv_pdfs_values)
        generate_power_violin_charts(names, orv_pdfs_values)


# Run the main script
main()
