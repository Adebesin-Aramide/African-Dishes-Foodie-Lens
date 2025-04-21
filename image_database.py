import streamlit as st
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Define scopes and authenticate using Google credentials from Streamlit secrets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials_info = st.secrets["google_credentials"]
creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

# Define your Google Sheets ID (replace with the actual Sheet ID)
SHEET_ID = '1TECYbn54os4zIosi9nk8YHr3owAwDJPqDqyBlEDV_I0'  # Replace with your Google Sheet ID
SHEET_RANGE = '1:1000'  # Adjust the range based on your sheet's structure


# Google Drive setup
FOLDER_ID = '1Ye3_tBZaC-W-i05LDl9OEl1ujJTB77Wq'  # Replace with your actual Google Drive folder ID

# Function to append data to Google Sheets
def append_to_google_sheet(food_name, description, country, state, tribe, image_url):
    values = [[food_name, description, country, state, tribe, image_url]]
    body = {
        'values': values
    }
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

# Function to upload an image to Google Drive and return the image URL
def upload_image_to_drive(image, image_name):
    image_stream = io.BytesIO()
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)

    file_metadata = {
        'name': f"{image_name}.jpg",
        'parents': [FOLDER_ID]
    }
    media = MediaIoBaseUpload(image_stream, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Generate and return the public URL for the uploaded image
    file_id = file.get('id')
    drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?id={file_id}"

# Streamlit interface
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
    and details will be saved securely to our database on Google Sheets and Google Drive. This database will eventually 
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
    st.image(example_image_path, caption="Example: Semo, Efo Riro, Ponmo, Saki", use_container_width=True)

    st.write("""
    **Guidelines for Submission**:
    - **Food Name Format**: Use clear and traditional names, such as "Iyan" instead of "Pounded Yam", "Efo Riro" instead of "Vegetable Soup."
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
            # Upload image to Google Drive and get the URL
            image_url = upload_image_to_drive(image, food_name)
            # Append data to Google Sheets
            append_to_google_sheet(food_name, description, country, state, tribe, image_url)
            st.success("Data saved successfully to Google Sheets and Google Drive!")
        else:
            st.warning("Please upload an image and fill in the Food Name, Country, State, and Tribe fields.")
