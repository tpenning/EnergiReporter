import altair as alt
import matplotlib.pyplot as plt
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

    # Set the columns for the subheader and information icon
    header, help_modal = st.columns([10, 1])

    # Show the header of this chart and information
    header.subheader(f"Power consumption {'' if singles[0] and singles[1]  else 'averages '}over time:")

    # Create help modal
    boxplot_mean_chart_modal = Modal("Inserting files", key="boxplot_mean_chart_modal_comparison")
    open_modal = help_modal.button("❔", key="boxplot_mean_chart_modal_comparison")
    if open_modal:
        with boxplot_mean_chart_modal.container():
            st.markdown(help_text_mean_chart_modal)

    # Create a tab element with the different chart variations
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

    # Show DataFrames with the total energy consumption for each file
    st.markdown("Total energy consumption of all the uploaded files:")
    energy_usage_dfs = st.columns(2)
    for i in range(2):
        energy_usage_df = pd.DataFrame(data={"FILE": name_lists[i],
                                             "TOTAL ENERGY": [f"{round(te, 2)}J" for te in all_total_energies[i]]})
        energy_usage_dfs[i].dataframe(energy_usage_df, hide_index=True)
    st.markdown("---")


def normality_check(names, orv_pdfs_values):
    # Calculate the p values and get the corresponding normality values
    p_values = list(map(lambda data: stats.shapiro(data).pvalue, orv_pdfs_values))
    normality_values = list(map(lambda pval: str(pval > 0.05), p_values))

    # Display the p and normality values in a DataFrame
    normality_df = pd.DataFrame(data={"FILE": names, "NORMAL": normality_values, "P-VALUE": p_values})
    st.dataframe(normality_df, hide_index=True)


def generate_power_boxplot_charts(string, names, orv_pdfs_values):
    # Set the columns for the subheader and information icon
    header, help_modal = st.columns([10, 1])

    # Show the header of this chart and information
    header.subheader("Data distribution of Power: " + string)

    # Create help modal
    boxplot_modal = Modal("Inserting files", key="boxplot_modal_"+string)
    open_modal = help_modal.button("❔", key="boxplot_modal_"+string)
    if open_modal:
        with boxplot_modal.container():
            st.markdown(help_text_boxplot_modal)

    # Information about the charts
    st.markdown("""
                The information below reports statistics about the power data. 
                A common convention is to apply outlier removal on the data which we provide below.
                Set the number of standard deviations to keep included (default 3).
                """)
    orv = st.number_input("Outlier removal:", value=3, step=1, min_value=1, key=string)
    orv_pdfs_values = [stat_pdf[(np.abs(stats.zscore(stat_pdf)) < orv)].tolist() for stat_pdf in orv_pdfs_values]

    orv_pdfs_values.append([x for xs in orv_pdfs_values for x in xs])
    names.append("Total of " + string)

    normality_check(names, orv_pdfs_values)

    # Create the violin plots of the data files
    plt.figure()
    plt.violinplot(dataset=orv_pdfs_values, showmedians=True)
    plt.ylabel("Power (W)")
    plt.xlabel("File")
    plt.xticks(range(1, len(names) + 1), labels=names)

    st.pyplot(plt.gcf())
    st.markdown("---")


def compare(data1, data2):
    st.subheader("Compare")

    data1 = [x for xs in data1 for x in xs]
    data2 = [x for xs in data2 for x in xs]

    _, pvalue = stats.ttest_ind(data1, data2, alternative="two-sided")

    if pvalue >= 0.05:
        st.write("According to Welch\'s t-test the difference is **NOT SIGNIFICANT** (with p-value " + str(pvalue) + " )")
    else:
        st.write("According to Welch\'s t-test the difference is **SIGNIFICANT** (with p-value " + str(pvalue) + " )")

    _, pvalue = stats.mannwhitneyu(data1, data2, alternative="two-sided")

    if pvalue >= 0.05:
        st.write("According to the MannWhitneyU-test the difference is **NOT SIGNIFICANT** (with p-value " + str(pvalue) + " )")
    else:
        st.write("According to the MannWhitneyU-test the difference is **SIGNIFICANT** (with p-value " + str(pvalue) + " )")

    data1higher = min(100, 100 * len(list(filter(lambda s: s[0] > s[1], zip(data1, data2)))) / min(len(data1), len(data2)))
    st.write("According to the Percentage of Pairs test, the first set has a higher power than the second set "
             "in " + str(data1higher) + "% of the measurements")


# The main script to run but scoped now
def main():
    # File uploaders for both sets of files
    upload_columns = st.columns(2)
    uploaded_files1 = upload_columns[0].file_uploader("Upload first set of CSV files",
                                                      type=["csv"], accept_multiple_files=True)
    uploaded_files2 = upload_columns[1].file_uploader("Upload second set of CSV files",
                                                      type=["csv"], accept_multiple_files=True)

    # Create help modal
    boxplot_insert_files_comparison = Modal("Inserting files", key="boxplot_insert_files_comparison")
    open_modal = st.button("❔", key="boxplot_mean_chart_modal")
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

        compare(stat_pdfs[0], stat_pdfs[1])


# Run the main script
main()
