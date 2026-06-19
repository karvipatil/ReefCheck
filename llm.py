import os
import io
from pydantic import BaseModel, Field
import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict

from prompt import SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS, FISH_SLATE_IMAGE_INSTRUCTIONS


os.environ["GEMINI_API_KEY"] = st.secrets["gemini"]["GEMINI_API_KEY"]

# constants
MODEL = "gemini-2.5-flash"
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


class LabelRecordings(BaseModel):
    distance: str
    label: str
    label_status: bool
    
class InfoRecordings(BaseModel):
  site_name: str
  country_island: str
  team_leader: str
  data_recorded_by: str
  depth: str
  date: str
  time: str
  

class SegmentationLabels(BaseModel):
  info_segment: List[InfoRecordings]
  segment_one: List[LabelRecordings]
  segment_two: List[LabelRecordings]
  segment_three: List[LabelRecordings]
  segment_four: List[LabelRecordings]


class LabelRecordingsFishInvert(BaseModel):
    name: str = Field(None, description = "Species Name")
    distance_one: int
    distance_one_clear: bool 
    distance_two: int 
    distance_two_clear: bool 
    distance_three: int 
    distance_three_clear: bool 
    distance_four: int 
    distance_four_clear: bool


class SegmentationLabelsFishInvert(BaseModel):
    fish: List[LabelRecordingsFishInvert]
    invertebrates: List[LabelRecordingsFishInvert]
    impacts: List[LabelRecordingsFishInvert]
    coral_disease: List[LabelRecordingsFishInvert]
    rare_animals: List[LabelRecordingsFishInvert]




def image_label_generator(image_path: str, prompt: str = SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS):

    img = PIL.Image.open(image_path)
    
    # Convert image to bytes for the new SDK
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=img.format or "PNG")
    img_bytes = img_byte_arr.getvalue()

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            prompt,
            types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SegmentationLabels,  # Pydantic models are supported natively
        ),
    )

    structured_output = SegmentationLabels.model_validate_json(response.text)
    return structured_output

def image_label_generator_fish_invert(image_path: str, prompt: str = FISH_SLATE_IMAGE_INSTRUCTIONS):
    img = PIL.Image.open(image_path)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=img.format or "PNG")
    img_bytes = img_byte_arr.getvalue()

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            prompt,
            types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SegmentationLabelsFishInvert,
        ),
    )

    structured_output = SegmentationLabelsFishInvert.model_validate_json(response.text)
    return structured_output


