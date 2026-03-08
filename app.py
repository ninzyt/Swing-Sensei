import os
import streamlit as st
import cv2
import mediapipe as mp
from dotenv import load_dotenv
from supabase import create_client, Client

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
for key, default in {
    "logged_in": False,
    "username": "",
    "supabase_session": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Auth helpers ──────────────────────────────────────────────────────────────
def sign_in(email: str, password: str):
    """Attempt Supabase email/password sign-in. Returns (success, error_message)."""
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if response.session:
            st.session_state.logged_in = True
            st.session_state.username = response.user.email
            st.session_state.supabase_session = response.session
            return True, None
        return False, "Sign-in failed — no session returned."
    except Exception as e:
        return False, str(e)


def sign_up(email: str, password: str):
    """Create a new Supabase account. Returns (success, error_message)."""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        # If email confirmation is disabled, a session is returned immediately
        if response.session:
            st.session_state.logged_in = True
            st.session_state.username = response.user.email
            st.session_state.supabase_session = response.session
            return True, None
        # Email confirmation required — user exists but no active session yet
        if response.user:
            return True, "confirm_email"
        return False, "Sign-up failed — no user returned."
    except Exception as e:
        return False, str(e)


def sign_out():
    """Sign out from Supabase and clear local session state."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # sign-out errors are non-critical
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

            # ── Sign In tab ───────────────────────────────────────────────────
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

            # ── Create Account tab ────────────────────────────────────────────
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
                                st.error(
                                    "⚠️ Too many sign-up attempts. Please wait a minute and try again."
                                )
                            elif err and "already registered" in err.lower():
                                st.error(
                                    "An account with this email already exists. "
                                    "Please sign in using the **Sign In** tab."
                                )
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


# ── Gate: show login if not authenticated ─────────────────────────────────────
if not st.session_state.logged_in:
    show_login()
    st.stop()

# ── Main app (only reached when logged in) ────────────────────────────────────
show_logout()
st.title("Coach Alan Wu")

feedback = {
    "elbow_angle": 170,
    "shoulder_ok": True,
    "wrist_snapped": True,
    "overall": "bad"
}

st.markdown("""
<style>
    .stApp {
        background-color: #040c29;
    }
</style>
""", unsafe_allow_html=True)


def draw_feedback(frame, feedback):
    h, w = frame.shape[:2]

    # semi-transparent panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    # elbow
    elbow_color = (0, 255, 0) if feedback['elbow_angle'] > 160 else (0, 0, 255)
    cv2.putText(frame, f"Elbow: {feedback['elbow_angle']}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, elbow_color, 2)

    # shoulder
    shoulder_color = (0, 255, 0) if feedback['shoulder_ok'] else (0, 0, 255)
    cv2.putText(frame,
                "Shoulder: Good!" if feedback['shoulder_ok'] else "Rotate more!",
                (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, shoulder_color, 2)

    # overall
    overall_color = (0, 255, 0) if feedback['overall'] == 'good' else (0, 0, 255)
    cv2.putText(frame,
                "Great swing!" if feedback['overall'] == 'good' else "Keep practicing!",
                (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, overall_color, 3)

    return frame


# webcam loop inside streamlit
frame_window = st.empty()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = draw_feedback(frame, feedback)

    # streamlit needs RGB not BGR
    frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
