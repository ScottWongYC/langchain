import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from langchain_code import LangchainCode

api_key = st.secrets.OPENAI
filename = st.secrets.DATAFILE
langchain = LangchainCode()
st.title("Financial Analyst System")

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    st.session_state['client_data'] = None
    st.session_state['client_data_loaded'] = False  
    st.session_state['previous_client_id'] = None  
    st.session_state['session_id'] = None  
    st.session_state['model_with_memory'] = None  

client_id = st.sidebar.text_input("Enter your client ID:")

if client_id:
    client_data = langchain.load_client_data(filename, client_id)
    if not client_data:
        st.session_state.messages.append({"role": "assistant", "content": "No client data found for this ID. Please try again."})
        st.session_state['client_data'] = None
        st.session_state['client_data_loaded'] = False  
    else:
        st.session_state['client_data'] = client_data
        if not st.session_state['client_data_loaded']:  
            st.session_state.messages.append({"role": "assistant", "content": "Client data loaded successfully. You can now ask questions."})
            st.session_state['client_data_loaded'] = True  

        if st.session_state['previous_client_id'] != client_id:
            llm = langchain.initialize_openai_llm(api_key)
            model_with_memory = langchain.setup_llm_chain(llm)
            st.session_state['model_with_memory'] = model_with_memory  
            st.session_state['session_id'] = str(uuid.uuid4())  
            st.session_state['previous_client_id'] = client_id  

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state['client_data'] is not None and st.session_state['model_with_memory'] is not None:
    if prompt := st.chat_input("What is your question?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()  
            try:
                response = st.session_state['model_with_memory'].invoke({
                    "client_data": st.session_state['client_data'],  
                    "user_query": prompt  
                }, {"configurable": {"session_id": st.session_state['session_id']}})
                
                response_str = response.content if hasattr(response, 'content') else str(response)
                response_placeholder.markdown("**Answer:** " + response_str)  
            except Exception as e:
                response_placeholder.markdown("An error occurred while getting a response.")

        st.session_state.messages.append({"role": "assistant", "content": response_str})

st.sidebar.markdown("### Instructions")
st.sidebar.markdown("1. Enter your client ID in the sidebar.")
st.sidebar.markdown("2. Ask questions once your client data is loaded.")
