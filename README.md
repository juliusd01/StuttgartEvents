# deccob
Analysing event data for Stuttgart

## Main Question to answer: Where in Stuttgart is a good place to go out at wednesdays?
Have fun playing with the dashboard!

## Quick Start Dashboard with conda
```sh
conda env create -f environment.yml
conda activate decoob
# To run dashboard with 2000 events
streamlit run dashboard_demo.py
# To run dashboard with all evenzs
streamlit run dashboard_all_events.py
```
Alternatively one could install all dependencies using pip.

## Reproduce Data Preparation
Include the stutgart_events.json into the deccob directory and run the **step-by-step-walkthrough.ipynb**. (And I know that deccob is spelled differently 😄)

## Content of the repository
```
📦Decoob
 ┣ 📂.streamlit
 ┃ ┗ 📜config.toml                                          # Configuration file for streamlite dashboard
 ┣ 📂archive                                                # The archive contains stale code, this can be ignored
 ┃ ┣ 📜NLP_cluster.py
 ┃ ┣ 📜data_preprocess.py
 ┃ ┣ 📜example.json
 ┃ ┣ 📜mood_classification.py
 ┃ ┣ 📜outdated_dashboard.py
 ┃ ┗ 📜test.py
 ┣ 📂data                                                   # The preprocessed data for the dashboards
 ┃ ┣ 📜2000_events_sample.csv
 ┃ ┗ 📜all_events_dashboard.csv
 ┣ 📂img                                                    # Various images to better understand the data
 ┃ ┣ 📜Cluster_Viz.png
 ┃ ┣ 📜Missing_values_all_events.png
 ┃ ┣ 📜Time_distribution_all_wednesdays.png
 ┃ ┣ 📜dashboard_start_page.png
 ┃ ┣ 📜dashboard_start_page2.png
 ┃ ┣ 📜distribution_of_activity_type_all_events.png
 ┃ ┣ 📜missing_values_after_cleaning_all_events.png
 ┃ ┣ 📜months_all_events.png
 ┃ ┣ 📜starting_hour_all_events.png
 ┃ ┣ 📜time_of_day_all_events.png
 ┃ ┣ 📜time_of_day_wednesdays.png
 ┃ ┗ 📜word_cloud_all_events.png
 ┣ 📂utils                                                  # These were the building blocks for the step-by-step-walkthrough
 ┃ ┣ 📜data_extraction.py
 ┃ ┗ 📜data_preprocessing.py
 ┣ 📜.gitignore
 ┣ 📜LICENSE
 ┣ 📜README.md
 ┣ 📜dashboard_all_events.py                                # dashboard with all events
 ┣ 📜dashboard_demo.py                                      # dashboard with only 2000 samled events
 ┣ 📜environment.yml
 ┣ 📜requirements.txt                                       # dependencies
 ┣ 📜step-by-step-walkthrough.ipynb                         # See most of our programming steps in one notebook
 ┗ 📜stuttgart_events.json                                  # This file should be inserted to be able to run the jupyter notebook above 
```