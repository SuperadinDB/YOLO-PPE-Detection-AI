from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.detector import PPEDetector
from src.risk import evaluate_workers

import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"


# --------------------------------------------------
# Page
# --------------------------------------------------

st.set_page_config(
    page_title="YOLO PPE Detection",
    page_icon="🦺",
    layout="wide",
)

st.title("🦺 PPE Detection AI")
st.caption("Computer Vision system for Personal Protective Equipment detection")


# --------------------------------------------------
# Load model
# --------------------------------------------------

@st.cache_resource
def load_detector():
    return PPEDetector(
        model_path=MODEL_PATH,
        confidence=0.25,
    )


detector = load_detector()


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Configuration")

confidence = st.sidebar.slider(
    "Confidence",
    min_value=0.05,
    max_value=0.95,
    value=0.25,
    step=0.05,
)

source = st.sidebar.radio(
    "Input",
    [
        "Image",
        "Video",
        "Webcam",
    ],
)


detector.confidence = confidence


# --------------------------------------------------
# IMAGE
# --------------------------------------------------

if source == "Image":

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file:

        image = Image.open(uploaded_file).convert("RGB")

        frame = np.array(image)

        result = detector.predict(frame)

        annotated = detector.draw(frame, result)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original")
            st.image(frame, use_container_width=True)

        with col2:
            st.subheader("Detection")
            st.image(
                cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                use_container_width=True,
            )


# --------------------------------------------------
# VIDEO
# --------------------------------------------------

elif source == "Video":

    uploaded_file = st.file_uploader(
        "Upload a video",
        type=["mp4", "avi", "mov", "mkv"],
    )

    if uploaded_file:

        temp_path = PROJECT_ROOT / "temp_video.mp4"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        cap = cv2.VideoCapture(str(temp_path))

        frame_placeholder = st.empty()

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            result = detector.predict(frame)

            annotated = detector.draw(frame, result)

            frame_placeholder.image(
                cv2.cvtColor(
                    annotated,
                    cv2.COLOR_BGR2RGB,
                ),
                channels="RGB",
            )

        cap.release()


# --------------------------------------------------
# WEBCAM
# --------------------------------------------------

elif source == "Webcam":

    st.subheader("🎥 Real-time PPE Detection")

    def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        result = detector.predict(img)
        detections = detector.get_detections(result)
        annotated = detector.draw(img, result)

        return av.VideoFrame.from_ndarray(
            annotated,
            format="bgr24",
        )

    webrtc_streamer(
        key="ppe-webcam",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=video_frame_callback,
        media_stream_constraints={
            "video": True,
            "audio": False,
        },
        async_processing=True,
    )