import streamlit as st

def uploadFile():
    with st.form("extended_form"):
        uploaded_file = st.file_uploader("Choose Upload File")
        submit_button = st.form_submit_button("Submit")
    
    if submit_button and uploaded_file is not None:
        fileUp = open("./Uploaded_File/" + str(uploaded_file.name), "wb")
        fileUp.write(uploaded_file.read())

uploadFile()