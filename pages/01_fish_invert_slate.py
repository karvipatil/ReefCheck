import streamlit as st
import os
import uuid
from PIL import Image
import io

from utils import handle_image_orientation
from llm import image_label_generator_fish_invert
from utils import create_fish_slate_dataframe, fish_slate_excel_creation, load_and_prepare_excel_for_fish_slate
from utils import fish_excel_data_extractor
from s3_utils import upload_to_s3, upload_bucket_path
from db_utils import add_record
from session_records import init_slate_information

# enivironment variables
os.environ["ENV"] = st.secrets["aws"]["ENV"]

# db table name
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"

# constants
FISH_INVERT_IMAGE = "fish_and_invert.png"
FISH_INVERT_CSV = "fish_and_invert.csv"

if "fish_dataframe" not in st.session_state:
    st.session_state.fish_dataframe = False

if "fish_invert_df" not in st.session_state:
    st.session_state.fish_invert_df = None

if "fish_invert_image" not in st.session_state:
    st.session_state.fish_invert_image = None

if "fish_invert_button" not in st.session_state:
    st.session_state.fish_invert_button = False

if "fish_invert_file_name" not in st.session_state:
    st.session_state.fish_invert_file_name = False

init_slate_information()


def interacting_editable_df():
    st.session_state.fish_dataframe = True

def off_interacting_editable_df():
    st.session_state.fish_dataframe = False
    st.session_state.fish_invert_image = None

def save_button():
    st.session_state.fish_invert_button = True


def file_name_input():
    st.session_state.fish_invert_file_name = True


def save_uploaded_image(image, target_name):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    image.save(target_name)

def fish_invert_slate():
    if not st.user.is_logged_in:
        st.error("Please log in to access this page.")
        return
    
    st.header("Fish and Invert Slate")
    
    uploaded_fish_invert = st.file_uploader(
        "Upload Fish and Invert Image",
        type=["jpg", "jpeg", "png"],
        key="fish_invert_uploader",
        on_change=off_interacting_editable_df
    )
    
    if uploaded_fish_invert is not None:
        if not st.session_state.fish_dataframe and not st.session_state.fish_invert_button and not st.session_state.fish_invert_file_name:
            image = handle_image_orientation(Image.open(uploaded_fish_invert))
            st.session_state.fish_invert_image = image
            save_uploaded_image(image, FISH_INVERT_IMAGE)
            
            with st.spinner("Generating Fish and Invert Labels", show_time=True):
                fish_and_invert_labels = image_label_generator_fish_invert(FISH_INVERT_IMAGE)
                st.toast("Fish and Invert Labels Generated", icon='✅')
                fish_and_invert_df = create_fish_slate_dataframe(fish_and_invert_labels.model_dump(), FISH_INVERT_CSV)
                st.session_state.fish_invert_df = fish_and_invert_df
        # add the image to the sidebar
        try:
            st.sidebar.image(st.session_state.fish_invert_image, caption="Uploaded Fish and Invert Image")
        except Exception as error:
            st.error(f"Upload got corrupted! Please refresh the page and try again!")
            print(str(error))
            st.stop()
        # editable df 
        edited_df = st.data_editor(st.session_state.fish_invert_df, on_change=interacting_editable_df)
        # add the text input
        file_name = st.text_input("File Name to be Saved", value=None, on_change = file_name_input)
        if not file_name:
            st.error("Please enter a file name to save the files.")
            st.stop()
        # set the image extension
        save_image_name = file_name + ".png"
        save_excel_name = file_name + ".xlsx"
        if st.button("Save Files", on_click=save_button):
            download_capability = True
            with st.spinner("Saving Files", show_time=True):
                # initiate excel creation and file saving
                fish_response = fish_excel_data_extractor(edited_df)
                fish_slate_excel_creation(fish_response, st.session_state.slate_information,save_excel_name)
                # create the data id
                data_id = str(uuid.uuid4())
                # save files
                # save the excel
                excel_url = upload_to_s3(save_excel_name, upload_bucket_path(st.user['name'], st.user['sub'], 'excel', 'fish_and_invert', f"{data_id}_{file_name}"))
                if excel_url:
                    st.toast(f"Excel Uploaded", icon='✅')
                else:
                    download_capability = False
                    # save the image
                image_url = upload_to_s3(FISH_INVERT_IMAGE, upload_bucket_path(st.user['name'], st.user['sub'], 'image', 'fish_and_invert', f"{data_id}_{file_name}"))
                if image_url:
                    st.toast(f"Image Uploaded", icon='✅')
                else:
                    download_capability = False
                # add a record to the database
                if download_capability:
                    db_response = add_record(DB_TABLE_NAME, data_id, st.user['sub'], st.user['name'], image_url, excel_url, "success")
                    print(db_response)
                    if db_response['success']:
                        st.toast(f"Record Saved", icon='✅')
                    else:
                        download_capability = False
            # download the excel file
            if not download_capability:
                st.error(f"Error saving files. Please contact support for assistance.")
                st.stop()
            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_fish_slate(save_excel_name),
                file_name=save_excel_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click='ignore'
            )

if __name__ == "__main__":
    fish_invert_slate()
