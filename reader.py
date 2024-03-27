import pandas as pd

# Easy to use/rename variables for the columns used
TIME = "Time (s)"
POWER = "Power (W)"


def read_uploaded_files(uploaded_files):
    # Initialize the values to (intermediately) store the data
    total_energies = []
    pdfs = []
    names = []

    # Iterate over the uploaded files
    for uploaded_file in uploaded_files:
        # Read the CSV file and store the name
        df = pd.read_csv(uploaded_file)
        names.append(uploaded_file.name[:-4])

        # Extract the time-power DataFrame and the total energy used
        power_tdf, total_energy = extract_df(df)

        # Add the total energy to the list
        total_energies.append(total_energy)

        # Index the pdf over time and add the power column to the pdfs list
        power_tdf.set_index(TIME, inplace=True)
        pdfs.append(power_tdf[POWER])

    # Concatenate the DataFrames along the POWER columns and calculate the mean data across the DataFrames
    power_df = pd.concat(pdfs, axis=1, keys=names)
    mean_df = power_df.mean(axis=1).to_frame().rename(columns={0: POWER})

    # Create a pdfs copy without the time indexing for the data statistics
    stat_pdfs = [df.reset_index(drop=True) for df in pdfs]

    # Return the retrieved data formats and information
    return power_df, mean_df, total_energies, names, stat_pdfs


def extract_df(df):
    # The variables used to retrieve the energy and power
    total_time = 0
    time = []
    total_energy = 0
    power = []

    # Extract the power and energy corresponding to the data column available
    if "CPU_POWER (Watts)" in df.columns or "SYSTEM_POWER (Watts)" in df.columns:
        # Get the column key and the power immediately
        key = "CPU_POWER (Watts)" if "CPU_POWER (Watts)" in df.columns else "SYSTEM_POWER (Watts)"
        power = df[key].tolist()

        # Calculate the time and total energy
        for index, row in df.iloc[2:].iterrows():
            # Update the total time and add the 0.1s rounded time to the list
            delta = (row["Time"] - df.at[index - 1, "Time"]) / 1000
            total_time += delta
            time.append(round(total_time, 1))

            # Calculate the energy used over the last delta and add it to the total
            total_energy += row[key] * delta
    elif "CPU_ENERGY (J)" in df.columns or "PACKAGE_ENERGY (J)" in df.columns:
        # Get the column key
        key = "CPU_ENERGY (J)" if "CPU_ENERGY (J)" in df.columns else "PACKAGE_ENERGY (J)"

        # Calculate the time, energy, and power
        for index, row in df.iloc[2:].iterrows():
            # Update the total time and add the 0.1s rounded time to the list
            delta = (row["Time"] - df.at[index - 1, "Time"]) / 1000
            total_time += delta
            time.append(round(total_time, 1))

            # Calculate the energy used in the delta from the difference and add it to the total
            energy = row[key] - df.at[index - 1, key]
            total_energy += energy

            # Calculate the power consumed used over the last delta and add it to the list
            power.append(energy / delta)
    else:
        raise ValueError("None of the specified energy data columns are present in the CSV file")

    # Create a DataFrame for the time and power
    power_tdf = pd.DataFrame(data={TIME: time, POWER: power})

    # Return the time-power DataFrame and the total energy consumption
    return power_tdf, total_energy
