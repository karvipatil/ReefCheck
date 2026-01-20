import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Dict
import base64
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import streamlit as st

from prompt import SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS, FISH_SLATE_IMAGE_INSTRUCTIONS


# importing secrets from secrets.toml
os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["llm"]["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["llm"]["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["llm"]["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["llm"]["LANGCHAIN_PROJECT"]
os.environ["OPENAI_API_KEY"] =  st.secrets["llm"]["OPENAI_API_KEY"]


# constants
MODEL = "gpt-4o"

# set the openai model
llm = ChatOpenAI(model=MODEL, temperature=0)


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


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def image_label_generator(image_local_path: str, prompt: str = SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS):
    image_data = encode_image(image_local_path)
    # set up the message
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"},
            },
        ],
    )
    # create a structured output
    structured_llm = llm.with_structured_output(SegmentationLabels)
    # invoke the llm to generatr an query
    invoke_image_query = structured_llm.invoke([message])

    return invoke_image_query


def image_label_generator_fish_invert(image_local_path: str, prompt: str = FISH_SLATE_IMAGE_INSTRUCTIONS):
    image_data = encode_image(image_local_path)
    # set up the message
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            },
        ],
    )
    # create a structured output
    structured_llm = llm.with_structured_output(SegmentationLabelsFishInvert)
    # invoke the llm to generatr an query
    invoke_image_query = structured_llm.invoke([message])

    return invoke_image_query