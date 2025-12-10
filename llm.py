import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Dict
import base64
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import streamlit as st

from prompt import SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS


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

# creating structured outputs for SUBSTRATE_SLATE
class LabelRecordings(BaseModel):
  distance: str
  label: str
  label_status: bool

class SegmentationLabels(BaseModel):
  segment_one: List[LabelRecordings]
  segment_two: List[LabelRecordings]
  segment_three: List[LabelRecordings]
  segment_four: List[LabelRecordings]


# converting image to base64
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

# for SUBSTRATE_SLATE
def create_image_labels(image_path: str, human_prompt: str = SUBSTRATE_SLATE_IMAGE_INSTRUCTIONS):
  image_data = encode_image(image_path)
  message = HumanMessage(
        content=[
            {"type": "text", "text": human_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"},
            },
        ],
    )
  # create a structured output
  structured_llm = llm.with_structured_output(SegmentationLabels)
  # invoke the llm to generate a query
  invoke_image_query = structured_llm.invoke([message])
  return invoke_image_query



