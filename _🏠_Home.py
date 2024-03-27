import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.write("# Welcome to EnergiReporter!")
st.markdown("""
    EnergiReporter is an open-source app built for analyzing energy data files, 
    specifically those of [EnergiBridge](https://github.com/tdurieux/energibridge).
    EnergiReporter offers data analysis reports and data comparison reports 
    for single or multiple files. Select a data visualization option from the sidebar to start 
    generating your report!
    
    Currently, EnergiReporter was designed with the energy data file format of EnergiBridge in mind. 
    The uploaded file must be a CSV file with either one of the following columns reporting the 
    total energy or power usage: "CPU_POWER (Watts)", "SYSTEM_POWER (Watts)", "CPU_ENERGY (J)", 
    or "PACKAGE_ENERGY (J)". Additionally, it should provide the "Delta" and "Time" columns which 
    are required to correctly convert and display the data.
    
    Any energy data file with the specified columns can be used to generate reports. If you wish 
    to use a different file format, the code is publicly available 
    [here](https://github.com/tpenning/EnergiReporter). There you can specify a different total 
    energy/power column and indicate how it should be interpreted.
    """)
