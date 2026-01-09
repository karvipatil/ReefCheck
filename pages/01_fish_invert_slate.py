import streamlit as st
import io
from io import BytesIO
import os
from utils import handle_image_orientation
from llm import create_fish_slate_labels
from utils import extract_data_from_dataframe, create_fish_slate_dataframe, create_substrate_excel_file
from PIL import Image
import uuid
from s3_utils import upload_to_s3, upload_bucket_path
from db_utils import adding_record
from utils import load_and_prepare_excel_for_substrate, extract_fish_data_from_dataframe, create_fish_slate_excel_file, load_and_prepare_excel_for_fish_slate

# taking environment variables
os.environ['ENV'] = st.secrets["aws"]["ENV"]
# database table name
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"


# constants
FISH_INVERT_IMAGE = "fish_invert_image.png"
FISH_INVERT_CSV = "fish_invert.csv"

if "fish_invert_file_name" not in st.session_state:
    st.session_state.fish_invert_file_name = False

if "fish_dataframe" not in st.session_state:
    st.session_state.fish_dataframe = False

if "fish_invert_button" not in st.session_state:
    st.session_state.fish_invert_button = False

# if "file_name" not in st.session_state:
#     st.session_state.file_name = False

if "fish_invert_image" not in st.session_state:
    st.session_state.fish_invert_image = None

if "fish_invert_dataframe" not in st.session_state:
    st.session_state.fish_invert_dataframe = None

def user_off_editable_dataframe():
    st.session_state.fish_dataframe = False
    st.session_state.fish_invert_image = None

def user_editable_dataframe():
    st.session_state.fish_dataframe = True

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
        st.error("Please log in.")
        return
    

    st.header("Fish Slate")
    # fish_slate uploader
    uploaded_fish_slate = st.file_uploader("Choose a file", 
                                          type=["jpg", "jpeg", "png"],
                                          key="fish_slate_uploader",
                                          on_change= user_off_editable_dataframe
                                          )

    if uploaded_fish_slate is not None:
        if not st.session_state.fish_dataframe and not st.session_state.fish_invert_button and not st.session_state.fish_invert_file_name:
            # store copy of the fish slate in session_state
            image = handle_image_orientation(Image.open(uploaded_fish_slate))
            st.session_state.fish_invert_image = image
            save_uploaded_image(image, FISH_INVERT_IMAGE) 

            with st.spinner("Generating Fish Slate Labels", show_time=True):
                fish_slate_labels = create_fish_slate_labels(FISH_INVERT_IMAGE)
                st.toast("Your edited fish image was saved!", icon="😍")
                fish_dataframe = create_fish_slate_dataframe(fish_slate_labels.model_dump(), FISH_INVERT_CSV)
                st.session_state.fish_invert_dataframe = fish_dataframe
        try:
            st.sidebar.image(st.session_state.fish_invert_image, caption="User uploaded fish slate image")
        except Exception as error:
            print(str(error))
            st.error("We couldn't display your image!")
            st.stop()
    

    # st.dataframe(st.session_state.fish_slate_dataframe)
        edited_fish_dataframe = st.data_editor(st.session_state.fish_invert_dataframe, on_change = user_editable_dataframe)

        fish_file_name = st.text_input("File Name to be Saved", value=None, on_change=file_name_input)
        if not fish_file_name:
            st.error("You must enter a file name to save an image.")
            st.stop()
        

        save_fish_image_name = fish_file_name + ".png"
        save_fish_excel_name = fish_file_name + ".xlsx"
        if st.button("Save files", on_click= save_button):
            download_capability = True
            with st.spinner("Saving", show_time=True):
                # taking csv data and creating excel file
                extracted_fish_slate_data = extract_fish_data_from_dataframe(edited_fish_dataframe)
                create_fish_slate_excel_file(extracted_fish_slate_data, save_fish_excel_name)
                # creating a unique id
                fish_data_id = str(uuid.uuid4())
                # save excel files
                fish_excel_url = upload_to_s3(save_fish_excel_name, upload_bucket_path(st.user["name"], st.user["sub"], "excel", "fish_slate", f"{fish_data_id}_{fish_file_name}") )
                if fish_excel_url:
                    st.toast("Excel uploading is complete!")
                else:
                    download_capability = False
                # save image files
                fish_image_url = upload_to_s3(FISH_INVERT_IMAGE, upload_bucket_path(st.user["name"], st.user["sub"], "image", "fish_slate", f"{fish_data_id}_{fish_file_name}") )
                if fish_image_url:
                    st.toast("Image uploading is complete!")
                else:
                    download_capability = False
                # add record
                if download_capability:
                    st.toast("db_response")
                    db_response = adding_record(DB_TABLE_NAME, fish_data_id, st.user["sub"], st.user["name"], fish_image_url, fish_excel_url, "success")  
                    print(db_response)           
                    if db_response["Success"]:
                        st.toss("Record Saved")
                    else:
                        download_capability = False
            if not download_capability:
                st.error("Upload failed.")
                st.stop()
            

            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_fish_slate(save_fish_excel_name),
                file_name=save_fish_excel_name, 
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click="ignore"
            )
            
if __name__ == "__main__":
    fish_invert_slate()