import streamlit as st
import requests

st.title("CDP Support Chatbot")

cdp = st.selectbox("Select CDP", ["Segment", "mParticle", "Lytics", "Zeotap"])
question = st.text_input("Enter your question")

if st.button("Ask"):
    if cdp and question:
        response = requests.post("http://127.0.0.1:8000/ask", json={"question": f"{cdp.lower()} {question}"})
        if response.status_code == 200:
            answer = response.json().get("answer")
            st.write("Answer:", answer)
        else:
            st.write("Error:", response.json().get("detail"))
    else:
        st.write("Please select a CDP and enter a question.")

# For comparison functionality
compare_question = st.text_input("Enter your comparison question")
if st.button("Compare"):
    if compare_question:
        response = requests.post("http://127.0.0.1:8000/compare", json={"question": compare_question})
        if response.status_code == 200:
            comparison = response.json().get("comparison")
            st.write("Comparison:", comparison)
        else:
            st.write("Error:", response.json().get("detail"))
    else:
        st.write("Please enter a comparison question.")

# For advanced questions
advanced_question = st.text_input("Enter your advanced question")
if st.button("Advanced"):
    if advanced_question:
        response = requests.post("http://127.0.0.1:8000/advanced", json={"question": advanced_question})
        if response.status_code == 200:
            answer = response.json().get("answer")
            st.write("Answer:", answer)
        else:
            st.write("Error:", response.json().get("detail"))
    else:
        st.write("Please enter an advanced question.")