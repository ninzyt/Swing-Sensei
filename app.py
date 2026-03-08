import os
import streamlit as st
import cv2
import mediapipe as mp
from dotenv import load_dotenv
from supabase import create_client, Client
import math
import threading
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from state import SwingState
import texttospeech
import calculations
import phases
import main
import gemini_api

# ── Load environment variables from .env ──────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error(
        "⚠️ Supabase credentials are missing. "
        "Copy .env.example → .env and fill in your SUPABASE_URL and SUPABASE_ANON_KEY."
    )
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Coach Alan Wu", layout="wide")

# ── Session state defaults ────────────────────────────────────────────────────
AUTH_KEYS = {"logged_in": False, "username": "", "supabase_session": None}
for key, default in AUTH_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Auth helpers ──────────────────────────────────────────────────────────────
def sign_in(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            st.session_state.logged_in = True
            st.session_state.username = response.user.email
            st.session_state.supabase_session = response.session
            return True, None
        return False, "Sign-in failed — no session returned."
    except Exception as e:
        return False, str(e)


def sign_up(email: str, password: str):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.session:
            st.session_state.logged_in = True
            st.session_state.username = response.user.email
            st.session_state.supabase_session = response.session
            return True, None
        if response.user:
            return True, "confirm_email"
        return False, "Sign-up failed — no user returned."
    except Exception as e:
        return False, str(e)


def sign_out():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.supabase_session = None


# ── Login UI ──────────────────────────────────────────────────────────────────
def show_login():
    left, center, right = st.columns([1, 2, 1])
    with center:
        with st.container(border=True):
            st.title("🏸 Coach Alan Wu")
            st.write("Sign in or create an account to use the badminton swing coach.")
            tab_signin, tab_signup = st.tabs(["Sign In", "Create Account"])

            with tab_signin:
                with st.form("login_form"):
                    email = st.text_input("Email", key="signin_email")
                    password = st.text_input("Password", type="password", key="signin_password")
                    submitted = st.form_submit_button("Log in", use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        with st.spinner("Signing in…"):
                            ok, err = sign_in(email, password)
                        if ok:
                            st.success(f"Welcome, {st.session_state.username}!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {err}")

            with tab_signup:
                with st.form("signup_form"):
                    new_email = st.text_input("Email", key="signup_email")
                    new_password = st.text_input("Password", type="password", key="signup_password")
                    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
                    signup_submitted = st.form_submit_button("Create Account", use_container_width=True)
                if signup_submitted:
                    if not new_email or not new_password or not confirm_password:
                        st.error("Please fill in all fields.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        with st.spinner("Creating account…"):
                            ok, err = sign_up(new_email, new_password)
                        if ok and err == "confirm_email":
                            st.success(
                                "✅ Account created! Check your email to confirm your address, "
                                "then sign in using the **Sign In** tab."
                            )
                        elif ok:
                            st.success(f"Welcome, {st.session_state.username}!")
                            st.rerun()
                        else:
                            if err and "rate limit" in err.lower():
                                st.error("⚠️ Too many sign-up attempts. Please wait a minute and try again.")
                            elif err and "already registered" in err.lower():
                                st.error("An account with this email already exists. Please sign in using the **Sign In** tab.")
                            else:
                                st.error(f"Sign-up failed: {err}")


# ── Logout bar ────────────────────────────────────────────────────────────────
def show_logout():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.write(f"Logged in as: **{st.session_state.username}**")
    with col2:
        if st.button("Log out"):
            sign_out()
            st.rerun()


# ── Gate ──────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
    st.stop()

# ── Main app ──────────────────────────────────────────────────────────────────
show_logout()

st.markdown("""
<style>
    .stApp { background-color: #040c29; }
    header[data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem; }
    .stSelectbox label, .stSelectbox label p { color: white !important; }
    .stSelectbox [data-baseweb="select"] span { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>Meet Coach Alan!</h1>", unsafe_allow_html=True)


def draw_feedback(frame, feedback):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    elbow_color = (0, 255, 0) if feedback['elbow_angle'] > 160 else (0, 0, 255)
    cv2.putText(frame, f"Elbow: {feedback['elbow_angle']}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, elbow_color, 2)
    shoulder_color = (0, 255, 0) if feedback['shoulder_ok'] else (0, 0, 255)
    cv2.putText(frame, "Shoulder: Good!" if feedback['shoulder_ok'] else "Rotate more!", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, shoulder_color, 2)
    overall_color = (0, 255, 0) if feedback['overall'] == 'good' else (0, 0, 255)
    cv2.putText(frame, "Great swing!" if feedback['overall'] == 'good' else "Keep practicing!", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, overall_color, 3)
    return frame


# ── Camera session keys (safe to reset without touching auth) ─────────────────
CAMERA_KEYS = ["state", "detector", "start_time", "last_timestamp", "video_holder"]

move = st.selectbox("Feedback timing", ["on hit", "pre hit"])
mode = st.selectbox("Metric", ["elbow", "arm"])

if "state" not in st.session_state:
    st.session_state.state = SwingState()
if "detector" not in st.session_state:
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(base_options=base_options, num_poses=1, running_mode=vision.RunningMode.VIDEO)
    st.session_state.detector = vision.PoseLandmarker.create_from_options(options)
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.last_timestamp = 0

start_time = st.session_state.start_time
state = st.session_state.state
detector = st.session_state.detector

# ── session_done tracks whether camera is running or finished ─────────────────
if "session_done" not in st.session_state:
    st.session_state.session_done = False

# ── If session is done, skip camera and show results ──────────────────────────
if st.session_state.session_done:
    if st.session_state.get("gemini_result"):
        st.markdown(f"<div style='color: white;'>{st.session_state.gemini_result}</div>", unsafe_allow_html=True)

    if st.button("🔄 New Session"):
        for key in CAMERA_KEYS + ["gemini_result", "session_done"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.stop()

# ── Camera loop ───────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if "video_holder" not in st.session_state:
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    st.session_state.video_holder = cv2.VideoWriter("session.mp4", fourcc, 30, (w, h))

video_holder = st.session_state.video_holder
frame_holder = st.empty()
stop_placeholder = st.empty()
stop = stop_placeholder.button("Stop")

while not stop:
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    timestamp = int((time.time() - start_time) * 1000)
    detection_result = detector.detect_for_video(mp_image, timestamp)

    if len(detection_result.pose_landmarks) > 0:
        current_wrist = detection_result.pose_landmarks[0][15]
    else:
        current_wrist = None

    current_time = time.time()

    if state.prev_wrist is None:
        state.prev_wrist = current_wrist

    if state.prev_wrist is not None and current_wrist is not None:
        current_velocity = calculations.calculate_wrist_velocity(state.prev_wrist, current_wrist, current_time - state.prev_time, w, h)
    else:
        current_velocity = (0, 0)

    if state.prev_velocity is None:
        state.prev_velocity = current_velocity

    annotated_frame = main.handle_frame_landmarks(rgb_frame, detection_result, state, move, mode, current_velocity)
    video_holder.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
    frame_holder.image(annotated_frame, channels="RGB", width='stretch')

    state.prev_wrist = current_wrist
    state.prev_time = current_time
    state.prev_velocity = current_velocity

# ── Cleanup ───────────────────────────────────────────────────────────────────
stop_placeholder.empty()
frame_holder.empty()
cap.release()
video_holder.release()
del st.session_state.video_holder

# ── Get Gemini result, mark session done, rerun to show results cleanly ───────
st.session_state.gemini_result = gemini_api.get_gemini()
st.session_state.session_done = True
st.rerun()