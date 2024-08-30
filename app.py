import streamlit as st
import pandas as pd
from predictions import preprocess_and_predict
from meeting_scheduler import schedule_meetings
from helper import process_drive_links  # Import the text extraction function

# Streamlit App
st.title("AI-Powered Recruitment Assistant")

# User inputs
uploaded_file = st.file_uploader("Upload CSV File with Candidate ID and Resume Links", type=["csv"])
job_id = st.text_input("Enter Job ID")
job_name = st.text_input("Enter Job Name")

if uploaded_file is not None and job_id and job_name:
    # Read CSV file
    df = pd.read_csv(uploaded_file)

    # Convert Google Drive PDF links to plain text
    df = process_drive_links(df)  # This function adds a 'Extracted Text' column to the DataFrame

    # Use the extracted text for further processing
    processed_df = preprocess_and_predict(df[['Candidate ID', 'Extracted Text']])

    # Display selectable table
    selected_candidates = st.multiselect(
        "Select candidates for interview", processed_df['Name'].tolist()
    )

    if st.button("Schedule Interviews"):
        if selected_candidates:
            selected_df = processed_df[processed_df['Name'].isin(selected_candidates)]
            schedule_meetings(selected_df, job_id, job_name)
            st.success("Interviews scheduled and emails sent!")
        else:
            st.warning("Please select at least one candidate.")
