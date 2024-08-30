## pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pypdf2



import os
import io
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import PyPDF2

# Setup Google Drive API
SERVICE_ACCOUNT_FILE = 'path/to/your/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)


# Function to download PDF from Google Drive
def download_pdf(file_id, destination):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    fh.close()


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text


def process_drive_links(df):
    texts = []

    for link in df['Google Drive Links']:
        # Extract file ID from the link
        file_id = link.split('/')[5]

        # Set destination file path
        destination = f'{file_id}.pdf'

        # Download the PDF
        download_pdf(file_id, destination)

        # Extract text from the downloaded PDF
        text = extract_text_from_pdf(destination)
        texts.append(text)

        # Clean up: remove the downloaded PDF file
        os.remove(destination)

    df['Extracted Text'] = texts
    return df


# Process the DataFrame
processed_df = process_drive_links(df)
print(processed_df[['Google Drive Links', 'Extracted Text']])
