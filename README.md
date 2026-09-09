# Download AppImage for Linux
https://drive.google.com/file/d/1bNoOO-ofiaSJISXjjaq53gbLLUuVPetK/view?usp=sharing


# 🦺 EPP Detector — AI Safety Monitoring

EPP Detector is a Computer Vision application for detecting and monitoring **Personal Protective Equipment (PPE)** in images, recorded video and live camera feeds.

Built with **Python, Ultralytics YOLO, PyTorch, OpenCV and Streamlit**.

## ✨ Features

- 🖼️ Image analysis
- 🎞️ Recorded video analysis
- 📷 Real-time webcam detection
- ⚙️ Background video processing
- 🧠 YOLO-based PPE detection
- 🚀 CPU and NVIDIA CUDA processing
- 📊 PPE compliance monitoring
- 🚨 Sustained event detection
- 📄 CSV event export
- 🌐 English / Spanish interface
- 🎨 Multiple UI themes

## 🧠 Model

The application uses a custom object-detection model:

```text
models/sh17_model.pt
```

The model was trained using **Ultralytics YOLO11s** and the **SH17 Dataset for PPE Detection**.

The detector identifies people and PPE-related objects. EPP Detector adds an additional monitoring layer to evaluate PPE confirmation over time and record situations that may require review.

## ⚡ CPU / GPU

EPP Detector supports both processing modes:

- **CPU Compatibility Mode** — works without a dedicated GPU and includes video-processing optimizations.
- **NVIDIA CUDA** — enables GPU acceleration when a compatible NVIDIA device is detected.

If CUDA is unavailable, GPU processing is automatically disabled.

## 📊 Monitoring

The application combines YOLO detections with scene-level analysis to provide:

- Visible persons
- PPE confirmation
- People requiring review
- Current priority
- Sustained PPE events
- Event duration and visual evidence

Recorded events can be exported as **CSV**.

## 🛠️ Installation

```bash
git clone <repository-url>
cd YOLO-PPE-Detection-AI

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## 🐧 Linux AppImage

```bash
chmod +x EPPDetector-x86_64.AppImage
./EPPDetector-x86_64.AppImage
```

The CUDA-enabled AppImage also supports CPU mode from the application interface.

## 📁 Project Structure

```text
YOLO-PPE-Detection-AI/
├── app.py
├── launcher.py
├── epp_detector.spec
├── requirements.txt
├── models/
│   └── sh17_model.pt
├── samples/
├── src/
│   ├── detector.py
│   └── risk.py
└── ui/
    └── theme.py
```

## 📚 Dataset & Attribution

The model was trained using:

**SH17 Dataset for PPE Detection**  
Dataset creator/publisher: **Mughees Ahmad et al.**  
Source: **Kaggle — SH17 Dataset for PPE Detection**

https://www.kaggle.com/datasets/mugheesahmad/sh17-dataset-for-ppe-detection

The dataset contains images representing industrial environments and multiple PPE-related object classes.

### Dataset License

The SH17 dataset is distributed under:

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International  
(CC BY-NC-SA 4.0)**

https://creativecommons.org/licenses/by-nc-sa/4.0/

This license requires:

- **Attribution** to the original dataset authors/source.
- **NonCommercial use** — the dataset may not be used for commercial purposes under this license.
- **ShareAlike** — adaptations covered by the license must be distributed under the same or a compatible license.

EPP Detector does **not claim ownership of the SH17 dataset**.

The trained model in this repository was produced using SH17 data. Users intending to redistribute, sublicense or commercially deploy the model should independently review the dataset license and obtain additional permission from the dataset rights holders when necessary.

## ⚠️ Disclaimer

EPP Detector is an **AI-assisted safety monitoring tool**.

Detection accuracy can be affected by lighting, occlusion, image quality, camera position and model limitations. Results should not be considered a substitute for professional safety supervision or certified HSE/EHS procedures.

## 🧰 Technologies

Python · PyTorch · Ultralytics YOLO · OpenCV · Streamlit · WebRTC · Pandas · PyAV

---

**EPP Detector**  
AI-powered Personal Protective Equipment monitoring.