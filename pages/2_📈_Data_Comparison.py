import altair as alt
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from scipy import stats
import streamlit as st
from streamlit_modal import Modal

from help_texts import *
from reader import read_uploaded_files, POWER, TIME

st.set_page_config(page_title="Data Comparison", page_icon="📈")

# Page information/text
st.markdown("# Data Comparison")
st.markdown("""
    This page compares the energy data between two single or sets sets of measurements.
    Upload your (sets of) CSV files adhering to the format specified on the home page to generate the charts.
    """)


def show_mean_charts(singles, means_df, name_lists, all_total_energies):
    # Retrieve the time column from the index
    means_tdf = means_df.reset_index()

    # Melt the dataframe to have a column for the power value and another for the power number
    melted_means_tdf = means_tdf.melt(id_vars=[TIME], var_name="Set", value_name=POWER)

    # Create a tab element with the different chart variations
    st.subheader(f"Power consumption {'' if singles[0] and singles[1]  else 'averages '}over time:")
    tab_line, tab_area = st.tabs(["Line Chart", "Area Chart"])

    # Assign the tabs altair charts (using with notation) to label the axis and indicate set colors
    with tab_line:
        st.altair_chart(alt.Chart(melted_means_tdf).mark_line()
                        .encode(x=TIME, y=POWER, color="Set:N", tooltip=["Set", POWER]),
                        use_container_width=True)
    with tab_area:
        st.altair_chart(alt.Chart(melted_means_tdf).mark_area(opacity=0.7)
                        .encode(x=TIME, y=POWER, color="Set:N", tooltip=["Set", POWER]),
                        use_container_width=True)

    # Create help modal
    boxplot_mean_chart_modal = Modal("Inserting files", key="boxplot_mean_chart_modal_comparison")
    open_modal = st.button("Help", key="boxplot_mean_chart_modal_comparison")

    # Open modal if clicked
    if open_modal:
        with boxplot_mean_chart_modal.container():
            st.markdown(help_text_mean_chart_modal)

    # Show DataFrames with the total energy consumption for each file
    st.markdown("Total energy consumption of all the uploaded files:")
    energy_usage_dfs = st.columns(2)
    for i in range(2):
        energy_usage_df = pd.DataFrame(data={"FILE": name_lists[i],
                                             "TOTAL ENERGY": [f"{round(te, 2)}J" for te in all_total_energies[i]]})
        energy_usage_dfs[i].dataframe(energy_usage_df, hide_index=True)
    st.markdown("---")


# TODO: Fix this as it is currently incorrect
def normality_check(names, orv_pdfs_values):
    # Calculate the p values and get the corresponding normality values
    p_values = list(map(lambda data: stats.shapiro(data).pvalue, orv_pdfs_values))
    normality_values = list(map(lambda pval: str(pval > 0.05), p_values))

    # Display the p and normality values in a DataFrame
    normality_df = pd.DataFrame(data={"FILE": names, "NORMAL": normality_values, "P-VALUE": p_values})
    st.dataframe(normality_df, hide_index=True)


def generate_power_boxplot_charts(string, names, orv_pdfs_values):
    # Information about the charts
    st.subheader("Data distribution of Power: " + string)
    st.markdown("""
                The information below reports statistics about the power data. 
                A common convention is to apply outlier removal on the data which we provide below.
                Set the number of standard deviations to keep included (default 3).
                """)
    orv = st.number_input("Outlier removal:", value=3, step=1, min_value=1, key=string)
    orv_pdfs_values = [stat_pdf[(np.abs(stats.zscore(stat_pdf)) < orv)].tolist() for stat_pdf in orv_pdfs_values]

    normality_check(names, orv_pdfs_values)

    # Create the violin plots of the data files
    plt.figure()
    orv_pdfs_values.append([x for xs in orv_pdfs_values for x in xs])
    plt.violinplot(dataset=orv_pdfs_values, showmedians=True)
    plt.ylabel("Power (W)")
    plt.xlabel("File")
    names.append("Total of " + string)
    plt.xticks(range(1, len(names) + 1), labels=names)

    st.pyplot(plt.gcf())

    # Create help modal
    boxplot_modal = Modal("Inserting files", key="boxplot_modal_"+string)
    open_modal = st.button("Help", key="boxplot_modal_"+string)

    # Open modal if clicked
    if open_modal:
        with boxplot_modal.container():
            st.markdown(help_text_boxplot_modal)
    st.markdown("---")


# The main script to run but scoped now
def main():
    # File uploaders for both sets of files
    uploaded_files1 = st.file_uploader("Upload first set of CSV files", type=["csv"], accept_multiple_files=True)
    uploaded_files2 = st.file_uploader("Upload second set of CSV files", type=["csv"], accept_multiple_files=True)

    # Create help modal
    boxplot_insert_files_comparison = Modal("Inserting files", key="boxplot_insert_files_comparison")
    open_modal = st.button("Help", key="boxplot_mean_chart_modal")

    # Open modal if clicked
    if open_modal:
        with boxplot_insert_files_comparison.container():
            st.markdown(help_text_insert_files_comparison)

    # Process the uploaded sets of files
    if uploaded_files1 and uploaded_files2:
        st.markdown("---")

        # Initialize the lists to store the dataframes and additional information
        power_dfs = []
        stat_pdfs = []
        name_lists = []
        mean_dfs = []
        all_total_energies = []
        singles = []

        # Iterate over the uploaded sets of files
        for i, uploaded_files in enumerate([uploaded_files1, uploaded_files2]):
            # Retrieve the useful data formats and information from the uploaded files and set it in the lists
            power_df, mean_df, total_energies, names, stat_pdf = read_uploaded_files(uploaded_files)
            power_dfs.append(power_df)
            stat_pdfs.append(stat_pdf)
            mean_dfs.append(mean_df)
            name_lists.append(names)
            all_total_energies.append(total_energies)
            singles.append(len(uploaded_files) == 1)

        # Concatenate the DataFrames power columns indicated by which set they belong to
        means_df = pd.concat([mean_df[POWER] for mean_df in mean_dfs], axis=1, keys=["Set #1", "Set #2"])

        # Show the data analysis charts (single indicated changes handled internally to easily keep the charts order)
        show_mean_charts(singles, means_df, name_lists, all_total_energies)

        generate_power_boxplot_charts("First dataset", name_lists[0], stat_pdfs[0])
        generate_power_boxplot_charts("Second dataset", name_lists[1], stat_pdfs[1])


# Run the main script
main()
