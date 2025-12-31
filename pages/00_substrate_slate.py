import streamlit as st
import io
from io import BytesIO
import os
from utils import handle_image_orientation
from llm import create_image_labels
from utils import extract_data_from_dataframe, create_substrate_dataframe, create_substrate_excel_file
from PIL import Image
import uuid
from s3_utils import upload_to_s3, upload_bucket_path
from db_utils import adding_record
from utils import load_and_prepare_excel_for_substrate

# taking environment variables
os.environ['ENV'] = st.secrets["aws"]["ENV"]
# database table name
DB_TABLE_NAME = f"{os.environ['ENV']}-reefcheck"



# constants
SUBSTRATE_IMAGE = "substrate.png"
SUBSTRATE_CSV = "substrate.csv"

if "dataframe" not in st.session_state:
    st.session_state.dataframe = False

if "button" not in st.session_state:
    st.session_state.button = False

if "file_name" not in st.session_state:
    st.session_state.file_name = False

if "image" not in st.session_state:
    st.session_state.image = None

if "substrate_dataframe" not in st.session_state:
    st.session_state.substrate_dataframe = None

def user_off_editable_dataframe():
    st.session_state.dataframe = False
    st.session_state.image = None

def user_editable_dataframe():
    st.session_state.dataframe = True

def save_uploaded_image(image, target_name):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    image.save(target_name)

def save_button():
    st.session_state.button = True

def file_name_input():
    st.session_state.file_name = True

def substrate_slate():
    if not st.user.is_logged_in:
        st.error("Please log in.")
        return

        
    st.header("Substrate Slate")
    # substrate uploader
    uploaded_substrate = st.file_uploader("Choose a file", 
                                          type=["jpg", "jpeg", "png"],
                                          key="substrate_uploader",
                                          on_change= user_off_editable_dataframe
                                          )
    
    # save the uploaded substrate in session_state
    if uploaded_substrate is not None:
        # if not st.session_state.substrate_dataframe:
        if not st.session_state.dataframe and not st.session_state.button and not st.session_state.file_name:
            # store copy of the substrate in session_state
            image = handle_image_orientation(Image.open(uploaded_substrate))
            st.session_state.image = image
            save_uploaded_image(image, SUBSTRATE_IMAGE)

            with st.spinner("Generating Substrate Labels", show_time=True):
                substrate_labels = create_image_labels(SUBSTRATE_IMAGE)
                st.toast("Your edited image was saved!", icon="😍")
                substrate_dataframe = create_substrate_dataframe(substrate_labels.model_dump(), SUBSTRATE_CSV)
                st.session_state.substrate_dataframe = substrate_dataframe
        try:
            st.sidebar.image(st.session_state.image, caption="User uploaded substrate image")
        except Exception as error:
            print(str(error))
            st.error("We couldn't display your image!")
            st.stop()
        

       # st.dataframe(st.session_state.substrate_dataframe)
        edited_dataframe = st.data_editor(st.session_state.substrate_dataframe, on_change = user_editable_dataframe)

        file_name = st.text_input("File Name to be Saved", value=None, on_change=file_name_input)
        if not file_name:
            st.error("You must enter a file name to save an image.")
            st.stop()


        save_image_name = file_name + ".png"
        save_excel_name = file_name + ".xlsx"
        if st.button("Save files", on_click= save_button):
            download_capability = True
            with st.spinner("Saving"):
                # taking csv data and creating excel file
                extracted_substrate_data = extract_data_from_dataframe(edited_dataframe)
                create_substrate_excel_file(extracted_substrate_data, save_excel_name)
                # creating a unique id
                data_id = str(uuid.uuid4())
                # save excel files
                excel_url = upload_to_s3(save_excel_name, upload_bucket_path(st.user["name"], st.user["sub"], "excel", "substrate", f"{data_id}_{file_name}") )
                if excel_url:
                    st.toast("Excel uploading is complete!", icon="🟩")
                else:
                    download_capability = False
                # save image files
                image_url = upload_to_s3(SUBSTRATE_IMAGE, upload_bucket_path(st.user["name"], st.user["sub"], "image", "substrate", f"{data_id}_{file_name}") )
                if image_url:
                    st.toast("Image uploading is complete!", icon="🟢")
                else:
                    download_capability = False
                # add record
                if download_capability:
                    db_response = adding_record(DB_TABLE_NAME, data_id, st.user["sub"], st.user["name"], image_url, excel_url, "success")  
                    print(db_response)           
                    if db_response["success"]:
                        st.toast("Record Saved", icon="✅")
                    else:
                        download_capability = False
            if not download_capability:
                st.error("Upload failed.")
                st.stop()
            

            st.download_button(
                label="Download as Excel",
                data=load_and_prepare_excel_for_substrate(save_excel_name),
                file_name=save_excel_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                on_click="ignore"
            )
                
            
                
if __name__ == "__main__":
    substrate_slate()



    
