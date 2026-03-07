import streamlit as st
import cv2
import mediapipe as mp

st.title("Coach Alan Wu")
feedback = {
    "elbow_angle": 145,
    "shoulder_ok": False,
    "wrist_snapped": True,
    "overall": "bad"
}

