import numpy as np
import pandas as pd
from scipy import stats

# Easy to use/rename variables for the columns used
POWER = "Power (W)"
TIME = "Time (s)"


# TODO: Test with scripts that have different time intervals (especially power extraction)
def read_uploaded_files(uploaded_files):
    # Initialize the values to (intermediately) store the data
    total_energy = 0
    pdfs = []
    names = []

    # Iterate over the uploaded files
    for uploaded_file in uploaded_files:
        # Read the CSV file and store the name
        df = pd.read_csv(uploaded_file)
        names.append(uploaded_file.name[:-4])

        # Add the total energy of this data file
        total_energy += df["ENERGY"].sum()

        # Create the power DataFrame, index it over time and add the power column to the list
        pdf = pd.DataFrame(data={"Time (s)": df["TIME"],
                                 "POWER": [0] + [df.values[i][1] / (df.values[i + 1][0] - df.values[i][0])
                                                 for i in range(len(df.values) - 1)]})
        pdf.set_index("Time (s)", inplace=True)
        pdfs.append(pdf["POWER"])

    # Concatenate the DataFrames along the POWER columns and calculate the mean data across the DataFrames
    power_df = pd.concat(pdfs, axis=1, keys=names)
    mean_df = power_df.mean(axis=1).to_frame().rename(columns={0: "Power (W)"})

    # Average the total energy over all files
    total_energy = round(total_energy / len(uploaded_files), 2)

    # Create a pdfs copy without the time indexing for the data statistics
    stat_pdfs = [df.reset_index(drop=True) for df in pdfs]

    # Return the retrieved data formats and information
    return power_df, mean_df, total_energy, names, stat_pdfs


def outlier_removal_stat_pdfs(names, stat_pdfs, orv):
    # Apply outlier removal on each power DataFrame
    orv_pdfs = [stat_pdf[(np.abs(stats.zscore(stat_pdf)) < orv)] for stat_pdf in stat_pdfs]

    # Concatenate the orv stat pdfs in an orv power DataFrame
    orv_power_df = pd.concat(orv_pdfs, axis=1, keys=names)

    # Convert the orv stat pdfs to value lists
    orv_pdfs_values = [orv_pdf.tolist() for orv_pdf in orv_pdfs]

    # Return the created orv data structures
    return orv_power_df, orv_pdfs_values
