import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Part, Tool
from vertexai.preview.generative_models import grounding
import streamlit as st
import json
import re


def multiturn_generate_content():
    vertexai.init(project="genai-metalwork-dev-mscdirect", location="us-east4")
    tools = [
        Tool.from_retrieval(
            retrieval=grounding.Retrieval(
                source=grounding.VertexAISearch(datastore="projects/genai-metalwork-dev-mscdirect/locations/us/collections/default_collection/dataStores/kasc-tooling-u-program-assistant_1715879796905"),
            )
        ),
    ]
    
    generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0,
    }

    safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    ]
    
    system_instruction = '''
    You are a friendly, helpful chatbot for an industrial supply company. You assist the company's Key Account Sales Consultants (KASC) with metalworking knowledge. 
    You give a detailed response to the user's question when they ask one, using information from your data stores. 
    In addition to your response, please always provide the titles of your sources in a neatly formatted list.
    
    If the user's question is too complicated or there is no information found about the topic, state that this chat is only trained on basic metalworking topics. 
    Do not answer any questions that are unrelated to metalworking, and do not make up any answers.
    '''
    
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        tools=tools,
        system_instruction=system_instruction,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    chat = model.start_chat(response_validation=False)
    return chat

st.title('KASC Chatbot')

chat = multiturn_generate_content()

if "chat" not in st.session_state:
    st.session_state.chat = multiturn_generate_content()
else:
    chat = st.session_state.chat

if "history" not in st.session_state:
    st.session_state.history = st.session_state.chat.history

for message in st.session_state.history:
    with st.chat_message(message.role):
        st.markdown(message.parts[0].text)

# Accept user input
if prompt := st.chat_input("How can I help you?"):

    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = chat.send_message(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response.candidates[0].content.parts[0].text)
