import altair as alt
import pandas as pd
import streamlit as st
from streamlit_modal import Modal
from Helpteksten import *

from reader import read_uploaded_files

st.set_page_config(page_title="Data Comparison", page_icon="📈")

# Page information/text
st.markdown("# Data Comparison")
st.sidebar.header("Data Comparison")
st.write("""
    This page compares the energy data between two single or sets sets of measurements.
    Upload your (sets of) csv files with columns TIME and ENERGY to generate the charts.
    """)

# Easy to use/rename variables
TIME = "Time (s)"
POWER = "Power (W)"


def show_mean_charts(singles, means_df):
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
            st.markdown(helptekst_mean_chart_modal)

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
            st.markdown(helptekst_insert_files_comparison)

    # Process the uploaded sets of files
    if uploaded_files1 and uploaded_files2:
        st.markdown("---")

        # Initialize the lists to store the dataframes and additional information
        power_dfs = []
        mean_dfs = []
        total_energies = []
        singles = []

        # Iterate over the uploaded sets of files
        for i, uploaded_files in enumerate([uploaded_files1, uploaded_files2]):
            # Retrieve the useful data formats and information from the uploaded files and set it in the lists
            power_df, mean_df, total_energy = read_uploaded_files(uploaded_files)
            power_dfs.append(power_df)
            mean_dfs.append(mean_df)
            total_energies.append(total_energy)
            singles.append(len(uploaded_files) == 1)

        # Concatenate the DataFrames power columns indicated by which set they belong to
        means_df = pd.concat([mean_df[POWER] for mean_df in mean_dfs], axis=1, keys=["Set #1", "Set #2"])

        # Show the data analysis charts (single indicated changes handled internally to easily keep the charts order)
        show_mean_charts(singles, means_df)


# Run the main script
main()
