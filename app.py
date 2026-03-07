import streamlit as st
import cv2
import mediapipe as mp

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
        background-color: #102911;
    }
</style>
""", unsafe_allow_html=True)

def draw_feedback(frame, feedback):
    h, w = frame.shape[:2]
    
    # semi transparent panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    # elbow
    elbow_color = (0, 255, 0) if feedback['elbow_angle'] > 160 else (0, 0, 255)
    cv2.putText(frame, f"Elbow: {feedback['elbow_angle']}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, elbow_color, 2)
    
    # shoulder
    shoulder_color = (0, 255, 0) if feedback['shoulder_ok'] else (0, 0, 255)
    cv2.putText(frame, "Shoulder: Good!" if feedback['shoulder_ok'] else "Rotate more!", (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, shoulder_color, 2)

    # overall
    overall_color = (0, 255, 0) if feedback['overall'] == 'good' else (0, 0, 255)
    cv2.putText(frame, "Great swing!" if feedback['overall'] == 'good' else "Keep practicing!", (20, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, overall_color, 3)
    
    return frame

# webcam loop inside streamlit
# frame_window = st.image([])
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