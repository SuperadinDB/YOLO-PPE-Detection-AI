# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


datas = [
    ("app.py", "."),
    ("models/sh17_model.pt", "models"),
    ("samples/ppe_sample.mp4", "samples"),
    ("src", "src"),
    ("ui", "ui"),
]

hiddenimports = []
binaries = []


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
# PANDAS
# ============================================================

pd_datas, pd_binaries, pd_hiddenimports = collect_all(
    "pandas"
)

datas += pd_datas
binaries += pd_binaries
hiddenimports += pd_hiddenimports


# ============================================================
# PIL / PILLOW
# ============================================================

pil_datas, pil_binaries, pil_hiddenimports = collect_all(
    "PIL"
)

datas += pil_datas
binaries += pil_binaries
hiddenimports += pil_hiddenimports


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
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure
)


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