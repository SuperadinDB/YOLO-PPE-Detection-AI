# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)


# ============================================================
# APPLICATION DATA
# ============================================================

datas = [
    ("app.py", "."),
    ("models/sh17_model.pt", "models"),
    ("samples/ppe_sample.mp4", "samples"),
    ("src", "src"),
    ("ui", "ui"),
]

binaries = []

hiddenimports = [
    "numpy",
    "pandas",
    "PIL",
    "PIL.Image",
]


# ============================================================
# STREAMLIT
# ============================================================

st_datas, st_binaries, st_hiddenimports = collect_all(
    "streamlit"
)

datas += st_datas
binaries += st_binaries
hiddenimports += st_hiddenimports


# ============================================================
# ULTRALYTICS
# ============================================================

ul_datas, ul_binaries, ul_hiddenimports = collect_all(
    "ultralytics"
)

datas += ul_datas
binaries += ul_binaries
hiddenimports += ul_hiddenimports


# ============================================================
# TORCH
# ============================================================

# Torch necesita sus librerías nativas para CPU/CUDA,
# pero evitamos collect_all("torch") para no meter
# contenido innecesario.

binaries += collect_dynamic_libs(
    "torch"
)

hiddenimports += collect_submodules(
    "torch"
)


# ============================================================
# TORCHVISION
# ============================================================

# Necesario para torchvision::nms y operaciones nativas.

tv_datas, tv_binaries, tv_hiddenimports = collect_all(
    "torchvision"
)

datas += tv_datas
binaries += tv_binaries
hiddenimports += tv_hiddenimports


# ============================================================
# PYAV
# ============================================================

av_datas, av_binaries, av_hiddenimports = collect_all(
    "av"
)

datas += av_datas
binaries += av_binaries
hiddenimports += av_hiddenimports


# ============================================================
# STREAMLIT WEBRTC
# ============================================================

webrtc_datas, webrtc_binaries, webrtc_hiddenimports = collect_all(
    "streamlit_webrtc"
)

datas += webrtc_datas
binaries += webrtc_binaries
hiddenimports += webrtc_hiddenimports


# ============================================================
# OPENCV
# ============================================================

cv2_datas, cv2_binaries, cv2_hiddenimports = collect_all(
    "cv2"
)

datas += cv2_datas
binaries += cv2_binaries
hiddenimports += cv2_hiddenimports


# ============================================================
# WEBRTC DEPENDENCIES
# ============================================================

for package in [
    "aiortc",
    "aioice",
    "pylibsrtp",
]:

    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(
        package
    )

    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports


# ============================================================
# PANDAS / PILLOW
# ============================================================

# No usamos collect_all() para evitar meter extras.
# PyInstaller ya tiene hooks adecuados para ambos.

datas += collect_data_files(
    "pandas"
)

datas += collect_data_files(
    "PIL"
)


# ============================================================
# ANALYSIS
# ============================================================

a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    excludes=[
        # Ya no usamos Excel.
        "openpyxl",

        # No usados por la app.
        "tensorflow",
        "tensorboard",
        "torchaudio",
        "seaborn",

        # Desarrollo / notebooks.
        "IPython",
        "ipykernel",
        "jupyter",
        "jupyterlab",
        "notebook",

        # GUI innecesaria.
        "tkinter",

        # Entrenamiento / tooling no necesario.
        "pytest",
        "sphinx",
    ],

    noarchive=False,
)


# ============================================================
# PYTHON ARCHIVE
# ============================================================

pyz = PYZ(
    a.pure
)


# ============================================================
# EXECUTABLE
# ============================================================

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="EPPDetector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)