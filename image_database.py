import streamlit as st
from PIL import Image
import pandas as pd
import os

# Set Google Drive directory
save_dir = "G:/My Drive/African Dishes"

# Ensure the save directory exists
os.makedirs(save_dir, exist_ok=True)

# Function to save image and data to Google Drive
def save_image_to_drive(image, food_name, description, country, state, tribe):
    # Define path to save the image with the food name as the filename
    image_path = os.path.join(save_dir, f"{food_name}.jpg")
    
    # Open and save the uploaded image to the specified path
    image = Image.open(image)
    image.save(image_path)

    # Append food data to CSV file in the Google Drive folder
    data = {"Food Name": [food_name], "Description": [description], 
            "Image Path": [image_path], "Country": [country], 
            "State": [state], "Tribe": [tribe]}
    df = pd.DataFrame(data)
    csv_path = os.path.join(save_dir, "food_data.csv")
    df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)

# Sidebar navigation
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
    st.image(example_image_path, caption="Example: semo, efo riro, ponmo, saki", use_column_width=True)

    st.write("""
    **Guidelines for Submission**:
    - **Food Name Format**: Use clear and traditional name, such as Iyan instead of pounded yam, eforiro instead of vegetable soup."
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
            save_image_to_drive(uploaded_image, food_name, description, country, state, tribe)
            st.success("Data saved successfully to Google Drive!")
        else:
            st.warning("Please upload an image and fill in the Food Name, Country, State, and Tribe fields.")
