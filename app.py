import streamlit as st
import cv2
import mediapipe as mp

st.set_page_config(page_title="Coach Alan Wu", layout="wide")
USERS = {
    "alan": "coachingstart",
    "judge": "demo"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

def show_login():
    left, center, right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True):
            st.title("🏸 Coach Alan Wu")
            st.write("Sign in to use the badminton swing coach.")

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", use_container_width=True)

            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

def show_logout():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.write(f"Logged in as: **{st.session_state.username}**")
    with col2:
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

if not st.session_state.logged_in:
    show_login()
    st.stop()
    
st.title("Coach Alan Wu")
feedback = {
    "elbow_angle": 145,
    "shoulder_ok": False,
    "wrist_snapped": True,
    "overall": "bad"
}

