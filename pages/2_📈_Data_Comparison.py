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

# Category colors for the compare plots
category_colors = alt.Color("Set:N", scale=alt.Scale(
    domain=["Set #1", "Set #2"],
    range=["#1f77b4", '#ff7f0e']
))


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
                        .encode(x=TIME, y=POWER, color=category_colors, tooltip=["Set", POWER]),
                        use_container_width=True)
    with tab_area:
        st.altair_chart(alt.Chart(melted_means_tdf).mark_area(opacity=0.7)
                        .encode(x=TIME, y=POWER, color=category_colors, tooltip=["Set", POWER]),
                        use_container_width=True)

    # Show DataFrames with the total energy consumption for each file
    st.markdown("Total energy consumption of all the uploaded files:")
    energy_usage_dfs = st.columns(2)
    for i in range(2):
        energy_usage_df = pd.DataFrame(data={"FILE": name_lists[i],
                                             "TOTAL ENERGY": [f"{round(te, 2)}J" for te in all_total_energies[i]]})
        energy_usage_dfs[i].dataframe(energy_usage_df, hide_index=True)
    st.markdown("---")


def show_errorband_charts(singles, mean_dfs, power_dfs):
    if not any(singles):
        # Create the list to add the chart information in
        mean_tdfs = []
        std_dfs = []
        conf_dfs = []

        # Get the mean and errorband DataFrames for each set
        for i, mean_df in enumerate(mean_dfs):
            # Get the current power df as well and the set indication to add everywhere
            power_df = power_dfs[i]
            set_indicator = f"Set #{i+1}"

            # Get the mean time restored DataFrame, with its set indication added and add it to the list
            mean_tdf = mean_df.reset_index()
            mean_tdf["Set"] = set_indicator
            mean_tdfs.append(mean_tdf)

            # Calculate the mean, std, and conf data across the DataFrames, all time indexed
            mean_pdf = mean_df[POWER]
            std_data = power_df.std(axis=1)
            conf_data = std_data * 2

            # Combine the data into one time, mean, std/conf DataFrame
            std_df = pd.concat([mean_pdf, std_data], axis=1, keys=["MEAN", "STD"]).reset_index()
            std_df["Set"] = set_indicator
            std_dfs.append(std_df)
            conf_df = pd.concat([mean_pdf, conf_data], axis=1, keys=["MEAN", "CONF"]).reset_index()
            conf_df["Set"] = set_indicator
            conf_dfs.append(conf_df)

        # Concatenate the chart information to get all the entries into one list
        means_tdf = pd.concat(mean_tdfs, ignore_index=True)
        stds_df = pd.concat(std_dfs, ignore_index=True)
        confs_df = pd.concat(conf_dfs, ignore_index=True)

        # Set the columns for the subheader and information icon
        header, help_modal = st.columns([10, 1])

        # Show the header of this chart and information
        header.subheader(f"Power consumption averages over time with error bands:")

        # Create help modal
        errorband_chart_modal = Modal("Inserting files", key="errorband_chart_modal")
        open_modal = help_modal.button("❔", key="errorband_chart_modal")
        if open_modal:
            with errorband_chart_modal.container():
                st.markdown(help_text_errorband_chart_modal)

        # Create a tab element with the different errorband metrics
        tab_std, tab_conf = st.tabs(["STD Chart", "Conf Chart"])

        # Add the tab charts with the error bands
        tab_std.altair_chart(alt.Chart(means_tdf)
                             .mark_line().interactive()
                             .encode(x=TIME, y=POWER, color=category_colors, tooltip=["Set", POWER]) +
                             alt.Chart(stds_df).mark_errorband(extent="ci")
                             .encode(x=TIME, y=alt.Y("MEAN", title=POWER), yError="STD", color="Set:N"),
                             use_container_width=True)
        tab_conf.altair_chart(alt.Chart(means_tdf)
                              .mark_line().interactive()
                              .encode(x=TIME, y=POWER, color=category_colors, tooltip=["Set", POWER]) +
                              alt.Chart(confs_df).mark_errorband(extent="ci")
                              .encode(x=TIME, y=alt.Y("MEAN", title=POWER), yError="CONF", color="Set:N"),
                              use_container_width=True)
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


def compare_statistical_analysis(data1, data2):
    # The header and the arrays
    st.subheader("Comparing the data with statistical analysis")
    data1 = [x for xs in data1 for x in xs]
    data2 = [x for xs in data2 for x in xs]

    # Show the Welch's t-test results
    _, p_value1 = stats.ttest_ind(data1, data2, alternative="two-sided")
    st.markdown(f"According to [Welch\'s t-test](https://en.wikipedia.org/wiki/Welch%27s_t-test) "
                f"the difference is **{'NOT ' if p_value1 >= 0.05 else ''}SIGNIFICANT** "
                f"(with p-value {round(p_value1, 4)})")

    # Show the MannWhitneyU-test results
    _, p_value2 = stats.mannwhitneyu(data1, data2, alternative="two-sided")
    st.markdown(f"According to the [MannWhitneyU-test](https://en.wikipedia.org/wiki/Mann%E2%80%93Whitney_U_test) "
                f"the difference is **{'NOT ' if p_value2 >= 0.05 else ''}SIGNIFICANT** "
                f"(with p-value {round(p_value2, 4)})")

    # Show the Percentage of Pairs test results
    data1higher = round(min(100, 100 * len(list(filter(lambda s: s[0] > s[1], zip(data1, data2)))) /
                            min(len(data1), len(data2))), 2)
    st.markdown(f"According to the Percentage of Pairs test, the first set has a higher power than the second set "
                f"in {data1higher}% of the measurements")


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

        # Show the data analysis charts
        show_mean_charts(singles, means_df, name_lists, all_total_energies)
        show_errorband_charts(singles, mean_dfs, power_dfs)

        # Show the power statistic charts
        generate_power_boxplot_charts("First dataset", name_lists[0], stat_pdfs[0])
        generate_power_boxplot_charts("Second dataset", name_lists[1], stat_pdfs[1])

        # Show the statistical analysis comparison information
        compare_statistical_analysis(stat_pdfs[0], stat_pdfs[1])


# Run the main script
main()
