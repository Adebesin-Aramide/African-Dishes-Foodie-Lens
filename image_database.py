import streamlit as st
from PIL import Image
import pandas as pd
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# Authenticate and initialize the Google Drive API using Streamlit Secrets
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials_info = st.secrets["google_credentials"]
creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Folder ID where images and CSV will be saved in Google Drive
FOLDER_ID = '1Ye3_tBZaC-W-i05LDl9OEl1ujJTB77Wq'  # Replace with your actual folder ID

# Function to get the file ID of africa-dishes_data.csv if it exists
def get_file_id(file_name):
    query = f"name='{file_name}' and '{FOLDER_ID}' in parents and mimeType='text/csv'"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    return files[0]['id'] if files else None

# Function to download the existing CSV from Google Drive, or create a new DataFrame if it doesn’t exist
def download_csv(file_id):
    if file_id:
        # Download the CSV from Google Drive
        request = drive_service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_stream.seek(0)
        # Read the CSV into a DataFrame
        return pd.read_csv(file_stream)
    else:
        # If no file exists, return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=["Food Name", "Description", "Country", "State", "Tribe"])

# Function to upload or update files on Google Drive
def upload_to_drive(file_stream, file_name, mime_type, file_id=None):
    media = MediaIoBaseUpload(file_stream, mimetype=mime_type)
    if file_id:
        # Update existing file
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Create new file
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Function to save image and data to Google Drive
def save_image_to_drive(image, food_name, description, country, state, tribe):
    # Convert image to byte stream and upload to Google Drive
    image_stream = io.BytesIO()
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)
    upload_to_drive(image_stream, f"{food_name}.jpg", 'image/jpeg')

    # Prepare data to append to CSV
    new_data = pd.DataFrame({
        "Food Name": [food_name], "Description": [description],
        "Country": [country], "State": [state], "Tribe": [tribe]
    })

    # Get the file ID of africa-dishes_data.csv on Google Drive
    csv_file_id = get_file_id('africa-dishes_data.csv')

    # Download existing CSV data or start with an empty DataFrame if it doesn't exist
    existing_data = download_csv(csv_file_id)

    # Append the new data to the existing DataFrame
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Convert the updated DataFrame to a byte stream for upload
    file_stream = io.BytesIO()
    updated_data.to_csv(file_stream, index=False)
    file_stream.seek(0)

    # Upload or update the CSV file on Google Drive
    upload_to_drive(file_stream, 'africa-dishes_data.csv', 'text/csv', file_id=csv_file_id)

# Streamlit interface (same as before, no changes)
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", ["Introduction", "Upload"])

# Introduction Section
if selection == "Introduction":
    st.title("Welcome to the African Dishes Collection Project for Foodie Lens")
    st.write("""
    ### About the Project
    This project aims to create a comprehensive database of African dishes by gathering images and 
    descriptions of various traditional foods. By contributing to this project, you help preserve 
    the culinary heritage of African cultures and enable the development of AI models that recognize 
    African foods.
    
    ### How It Works
    You can upload an image of a dish, enter its name, and provide a brief description. The image 
    and details will be saved securely to our database on Google Drive. This database will eventually 
    help in building an image classification model to identify African dishes accurately.
    
    ### Get Involved
    - Share images of traditional African dishes.
    - Provide accurate names and descriptions.
    - Help create a resource for culinary and cultural preservation!
    
    Select **Upload** from the sidebar to start uploading images!
    """)

# Upload Section
elif selection == "Upload":
    st.title("African Dishes Image Collection")

    # Example image and guidance for users
    st.subheader("Example of Submission")
    example_image_path = "DALAS-SEMO-EFO.jpg"  # Replace with the path to your example image
    st.image(example_image_path, caption="Example: Semo, eforiro, ponmo, saki", use_column_width=True)

    st.write("""
    **Guidelines for Submission**:
    - **Food Name Format**: Use clear and traditional names, such as eforiro, ekuru..."
    - **Image Quality**: The image should be of good quality, with clear visibility of the dish.
    - **Original Images Only**: Please upload only original photos you took yourself. Images from the internet are not allowed.
    """)

    # Upload image field
    uploaded_image = st.file_uploader("Upload an image of the food", type=["jpg", "png", "jpeg"])

    # Input fields for food name and description
    food_name = st.text_input("Food Name")
    description = st.text_area("Description (Optional)")
    country = st.text_input("Country (Required)")
    state = st.text_input("State (Required)")
    tribe = st.text_input("Tribe (Required)")

    # Display uploaded image
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption=food_name, use_column_width=True)

    # Save data when Submit button is clicked, with required fields validation
    if st.button("Submit"):
        # Check if all required fields are filled
        if uploaded_image and food_name and country and state and tribe:
            save_image_to_drive(image, food_name, description, country, state, tribe)
            st.success("Data saved successfully to Google Drive!")
        else:
            st.warning("Please upload an image and fill in the Food Name, Country, State, and Tribe fields.")

