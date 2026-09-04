from datetime import datetime
from hashlib import sha1
from io import BytesIO
from pathlib import Path
from queue import Empty, Queue
import base64
import html
import time

import openpyxl

import av
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from src.detector import PPEDetector
from src.risk import (
    DISPLAY_NAMES,
    REQUIRED_PPE,
    SceneEventMonitor,
    analyze_scene,
)
from ui.theme import apply_theme, particles

from threading import Lock, Thread
import uuid

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "sh17_model.pt"

SAMPLE_VIDEO = (
    PROJECT_ROOT
    / "samples"
    / "ppe_sample.mp4"
)

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="EPP Detector",
    page_icon="🦺",
    layout="centered",
)

apply_theme()
particles()


# ============================================================
# MODEL
# ============================================================

@st.cache_resource
def load_detector():
    return PPEDetector(
        model_path=MODEL_PATH,
        confidence=0.25,
    )


detector = load_detector()
detector.confidence = 0.25

camera_inference_lock = Lock()

@st.cache_resource
def get_background_jobs():

    return {
        "lock": Lock(),
        "jobs": {},
    }


background_jobs = get_background_jobs()

# ============================================================
# LANGUAGE
# ============================================================

lang_col1, lang_col2 = st.columns([8.5, 1])

with lang_col2:
    icon_col, select_col = st.columns(
        [0.25, 0.75],
        vertical_alignment="center",
        gap="small",
    )

    with icon_col:
        st.markdown(
            '<div class="language-icon">🌐</div>',
            unsafe_allow_html=True,
        )

    with select_col:
        language_label = st.selectbox(
            "Language",
            ["EN", "ES"],
            index=0,
            label_visibility="collapsed",
        )

language = (
    "en"
    if language_label == "EN"
    else "es"
)


# ============================================================
# TEXT
# ============================================================

TEXT = {
    "en": {
        "description": (
            "AI-powered Computer Vision for real-time "
            "Personal Protective Equipment detection. "
            "Select an image, video, or live camera feed to begin."
        ),
        "image": "🖼️ \n\nAnalyze an image",
        "video": "🎞️ \n\nAnalyze recorded video",
        "camera": "📷 \n\nReal-time detection",
        "upload_image": "Upload an image",
        "upload_video": "Upload a video",
        "original": "Original",
        "detection": "Detection",
        "ppe_title": "Define the applicable PPE",
        "ppe_intro": (
            "Select only PPE that is mandatory for this task or area. "
            "Unselected equipment is excluded from monitoring and event detection."
        ),
        "ppe_selector": "Required PPE for this analysis",
        "no_ppe": "Select at least one PPE item.",
        "monitor_title": "Dashboard",
        "monitor_note": (
            "Provides continuous visibility into PPE compliance, "
            "helping identify situations that require attention."
        ),
        "persons": "Persons visible",
        "compliance": "Current confirmation",
        "review": "People to review",
        "priority": "Current priority",
        "ppe_status": "Current PPE confirmation",
        "events": "Event Log",
        "events_intro": (
            "A history of situations detected during the analysis, "
            "including event details and visual evidence "
            "for easy reference and review."
        ),
        "no_events": "No sustained review events have been recorded.",
        "export": "Export events",
        "export_help": (
            "Download the session event log in CSV format "
            "for further analysis, documentation, and follow-up."
                ),
        "download_csv": "Download CSV",
        "pause": "⏸ Pause",
        "resume": "▶ Resume",
        "restart": "↻ Restart analysis",
        "finished": "Video analysis completed.",
        "reset": "Reset session",
        "background": "⚙️ \n\nProcess video in background",
        "background_upload": "Upload a video for background processing",
        "background_start": "Start processing",
        "background_processing": "Processing video...",
        "background_completed": "Background processing completed.",
        "sample_video": "Use sample video",
        "sample_video_missing": "Sample video not found.",
    },
    "es": {
        "description": (
            "Visión Artificial impulsada por IA para detectar "
            "Equipos de Protección Personal en tiempo real. "
            "Selecciona una imagen, video o cámara en vivo "
            "para comenzar."
        ),
        "image": "🖼️ \n\nAnalizar una imagen",
        "video": "🎞️ \n\nAnalizar un video",
        "camera": "📷 \n\nDetección en tiempo real",
        "upload_image": "Sube una imagen",
        "upload_video": "Sube un video",
        "original": "Original",
        "detection": "Detección",
        "ppe_title": "Selecciona el EPP",
        "ppe_intro": (
            "Selecciona únicamente el EPP obligatorio para este equipo o tarea. "
            "Los elementos no seleccionados quedarán fuera del monitoreo."
        ),
        "ppe_selector": "EPP requerido para este análisis",
        "no_ppe": "Selecciona al menos un EPP.",
        "monitor_title": "Dashboard",
        "monitor_note": (
            "Proporciona un análisis continuo del cumplimiento de uso de EPP, "
            "facilitando la identificación de situaciones que pudieran requieren atención."
        ),
        "persons": "Personas visibles",
        "compliance": "Confirmación actual",
        "review": "Personas a revisar",
        "priority": "Prioridad actual",
        "ppe_status": "Confirmación actual por EPP",
        "events": "Registro de Eventos",
        "events_intro": (
            "Historial de situaciones detectadas durante el análisis, "
            "con información del evento y evidencia visual "
            "para facilitar su consulta y revisión."
        ),
        "no_events": "No se han registrado eventos de revisión sostenidos.",
        "export": "Exportar eventos",
        "export_help": (
            "Descarga el registro de eventos en formato CSV "
            "para facilitar su análisis, documentación y seguimiento."
        ),
        "download_csv": "Descargar CSV",
        "pause": "⏸ Pausar",
        "resume": "▶ Reanudar",
        "restart": "↻ Reiniciar análisis",
        "finished": "El análisis del video ha finalizado.",
        "reset": "Reiniciar sesión",
        "background": "⚙️ \n\nProcesar video en segundo plano",
        "background_upload": "Sube un video para procesar en segundo plano",
        "background_start": "Iniciar procesamiento",
        "background_processing": "Procesando video...",
        "background_completed": "Procesamiento en segundo plano finalizado.",
        "sample_video": "Usar video de muestra",
        "sample_video_missing": "No se encontró el video de muestra.",
    },
}

t = TEXT[language]


SECTION_INFO = {
    "en": {
        "Image": (
            "Analyze one frame and obtain an immediate scene-level PPE snapshot."
        ),
        "Video": (
            "Monitor PPE confirmation over time and record sustained review periods."
        ),
        "Webcam": (
            "Monitor a live scene and preserve sustained PPE review events."
        ),

        "Background": (
            "Process a recorded video in the background and review the results once completed."
        ),
    },
    "es": {
        "Image": (
            "Analiza un frame y obtén una fotografía inmediata del EPP en la escena."
        ),
        "Video": (
            "Monitorea la confirmación de EPP en el tiempo y registra periodos sostenidos de revisión."
        ),
        "Webcam": (
            "Monitorea una escena en vivo y conserva eventos sostenidos de revisión de EPP."
        ),
        "Background": (
            "Procesa un video grabado en segundo plano y revisa los resultados al finalizar."
        ),
    },
}


# ============================================================
# HELPERS
# ============================================================

def info_panel(title, body):
    st.markdown(
        (
            '<div class="info-panel">'
            f'<div class="info-panel-title">{title}</div>'
            f'<div class="info-panel-text">{body}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def format_time(seconds):
    if seconds is None:
        return "—"

    seconds = max(
        0.0,
        float(seconds),
    )

    minutes = int(
        seconds // 60
    )

    secs = seconds % 60

    return (
        f"{minutes:02d}:{secs:04.1f}"
    )


def snapshot_to_data_uri(snapshot):
    if snapshot is None:
        return None

    ok, buffer = cv2.imencode(
        ".jpg",
        snapshot,
        [
            int(cv2.IMWRITE_JPEG_QUALITY),
            78,
        ],
    )

    if not ok:
        return None

    encoded = base64.b64encode(
        buffer.tobytes()
    ).decode("ascii")

    return (
        "data:image/jpeg;base64,"
        + encoded
    )


def render_monitor(scene):
    priority = scene[
        "priority"
    ]

    priority_name = (
        DISPLAY_NAMES[language].get(
            priority,
            priority,
        )
        if priority
        else "—"
    )

    html_block = (
        '<div class="dashboard-shell">'
        f'<div class="dashboard-main-title">{t["monitor_title"]}</div>'
        f'<div class="dashboard-note">{t["monitor_note"]}</div>'

        '<div class="dashboard-grid">'

        '<div class="dashboard-card">'
        f'<div class="dashboard-label">{t["persons"]}</div>'
        f'<div class="dashboard-value">{scene["persons"]}</div>'
        '</div>'

        '<div class="dashboard-card">'
        f'<div class="dashboard-label">{t["compliance"]}</div>'
        f'<div class="dashboard-value">{scene["compliance"]:.0f}%</div>'
        '</div>'

        '<div class="dashboard-card">'
        f'<div class="dashboard-label">{t["review"]}</div>'
        f'<div class="dashboard-value">{scene["review_people"]}</div>'
        '</div>'

        '<div class="dashboard-card">'
        f'<div class="dashboard-label">{t["priority"]}</div>'
        f'<div class="dashboard-priority">{html.escape(str(priority_name))}</div>'
        '</div>'

        '</div>'

        f'<div class="dashboard-section-title">{t["ppe_status"]}</div>'
    )

    for ppe, stats in scene[
        "ppe_stats"
    ].items():
        display_name = (
            DISPLAY_NAMES[language]
            .get(ppe, ppe)
        )

        percent = stats[
            "percent"
        ]

        html_block += (
            '<div class="ppe-row">'
            '<div class="ppe-row-header">'
            f'<span>{html.escape(display_name)}</span>'
            f'<span>{stats["confirmed"]}/{scene["persons"]} · {percent:.0f}%</span>'
            '</div>'
            '<div class="ppe-bar">'
            '<div class="ppe-bar-fill" '
            f'style="width:{percent:.0f}%"></div>'
            '</div>'
            '</div>'
        )

    html_block += '</div>'

    st.markdown(
        html_block,
        unsafe_allow_html=True,
    )


def event_rows_for_export(
    monitor,
):
    rows = []

    for row in monitor.export_rows():
        ppe_name = (
            DISPLAY_NAMES[language]
            .get(
                row["ppe"],
                row["ppe"],
            )
        )

        if language == "es":
            rows.append(
                {
                    "Evento": row["event_id"],
                    "Individuo": row["person_index"],
                    "EPP": ppe_name,
                    "Inicio (s)": row["start_s"],
                    "Fin (s)": row["end_s"],
                    "Duración (s)": row["duration_s"],
                    "Personas promedio": row["avg_persons"],
                    "Confirmación promedio (%)": row["avg_confirmed_pct"],
                    "Confirmación mínima (%)": row["min_confirmed_pct"],
                    "Estado": (
                        "ABIERTO"
                        if row["status"] == "OPEN"
                        else "CERRADO"
                    ),
                }
            )
        else:
            rows.append(
                {
                    "Event": row["event_id"],
                    "Individual": row["person_index"],
                    "PPE": ppe_name,
                    "Start (s)": row["start_s"],
                    "End (s)": row["end_s"],
                    "Duration (s)": row["duration_s"],
                    "Average persons": row["avg_persons"],
                    "Average confirmation (%)": row["avg_confirmed_pct"],
                    "Minimum confirmation (%)": row["min_confirmed_pct"],
                    "Status": row["status"],
                }
            )

    return pd.DataFrame(
        rows
    )


def build_excel_bytes(
    monitor,
):
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XLImage

    rows = monitor.export_rows()

    wb = Workbook()
    ws = wb.active
    ws.title = "Review Events"

    if language == "es":
        headers = [
            "Snapshot",
            "Evento",
            "Individuo",
            "EPP",
            "Inicio (s)",
            "Fin (s)",
            "Duración (s)",
            "Personas promedio",
            "Confirmación promedio (%)",
            "Confirmación mínima (%)",
            "Estado",
        ]
    else:
        headers = [
            "Snapshot",
            "Event",
            "Individual",
            "PPE",
            "Start (s)",
            "End (s)",
            "Duration (s)",
            "Average persons",
            "Average confirmation (%)",
            "Minimum confirmation (%)",
            "Status",
        ]

    ws.append(
        headers
    )

    for index, row in enumerate(
        rows,
        start=2,
    ):
        ppe_name = (
            DISPLAY_NAMES[language]
            .get(
                row["ppe"],
                row["ppe"],
            )
        )

        status = row["status"]

        if language == "es":
            status = (
                "ABIERTO"
                if status == "OPEN"
                else "CERRADO"
            )

        ws.append(
            [
                "",
                row["event_id"],
                row["person_index"],
                ppe_name,
                row["start_s"],
                row["end_s"],
                row["duration_s"],
                row["avg_persons"],
                row["avg_confirmed_pct"],
                row["min_confirmed_pct"],
                status,
            ]
        )

        snapshot = row[
            "snapshot"
        ]

        if snapshot is not None:
            rgb = cv2.cvtColor(
                snapshot,
                cv2.COLOR_BGR2RGB,
            )

            image_buffer = BytesIO()

            Image.fromarray(
                rgb
            ).save(
                image_buffer,
                format="JPEG",
                quality=78,
            )

            image_buffer.seek(0)

            xl_image = XLImage(
                image_buffer
            )

            xl_image.width = 72
            xl_image.height = 72

            ws.add_image(
                xl_image,
                f"A{index}",
            )

            ws.row_dimensions[
                index
            ].height = 58

    ws.column_dimensions["A"].width = 13
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 13
    ws.column_dimensions["F"].width = 13
    ws.column_dimensions["G"].width = 14
    ws.column_dimensions["H"].width = 20
    ws.column_dimensions["I"].width = 25
    ws.column_dimensions["J"].width = 24
    ws.column_dimensions["K"].width = 14

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.getvalue()


def render_events(
    monitor,
    key_prefix,
    allow_export=True,
):
    info_panel(
        t["events"],
        t["events_intro"],
    )

    rows = monitor.export_rows()

    if not rows:
        st.info(
            t["no_events"]
        )
        return

    # Compact event cards: 78px thumbnail at left.
    for row in reversed(
        rows[-20:]
    ):
        ppe_name = (
            DISPLAY_NAMES[language]
            .get(
                row["ppe"],
                row["ppe"],
            )
        )

        snapshot_uri = (
            snapshot_to_data_uri(
                row["snapshot"]
            )
        )

        if snapshot_uri:
            snapshot_html = (
                f'<img class="event-thumb" src="{snapshot_uri}" />'
            )
        else:
            snapshot_html = (
                '<div class="event-thumb event-thumb-empty">—</div>'
            )

        status = (
            "EN CURSO"
            if (
                language == "es"
                and row["status"] == "OPEN"
            )
            else "ABIERTO"
            if (
                language == "es"
                and row["status"] == "OPEN"
            )
            else "CERRADO"
            if language == "es"
            else "OPEN"
            if row["status"] == "OPEN"
            else "CLOSED"
        )

        end_text = (
            format_time(
                row["end_s"]
            )
            if row["end_s"] is not None
            else (
                "Ahora"
                if language == "es"
                else "Now"
            )
        )

        if language == "es":
            detail = (
                f'Confirmación media {row["avg_confirmed_pct"]:.0f}% · '
                f'{row["avg_persons"]:.1f} personas prom.'
            )
        else:
            detail = (
                f'Average confirmation {row["avg_confirmed_pct"]:.0f}% · '
                f'{row["avg_persons"]:.1f} avg. persons'
            )

        event_html = (
            '<div class="event-card">'
            f'{snapshot_html}'
            '<div class="event-body">'
            '<div class="event-topline">'
            f'<span class="event-id">#{row["event_id"]}</span>'
            f'<span class="event-id">'
            f'{"Individuo" if language == "es" else "Individual"} '
            f'{row["person_index"]}</span>'
            f'<span class="event-ppe">{html.escape(ppe_name)}</span>'
            f'<span class="event-status">{status}</span>'
            '</div>'
            '<div class="event-time">'
            f'{format_time(row["start_s"])} → {end_text}'
            f' · {row["duration_s"]:.1f}s'
            '</div>'
            f'<div class="event-detail">{html.escape(detail)}</div>'
            '</div>'
            '</div>'
        )

        st.markdown(
            event_html,
            unsafe_allow_html=True,
        )

    if not allow_export:
        return

    st.subheader(t["export"])

    st.markdown(
        f"""
        <div class="section-info">
            <p>{t["export_help"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    export_df = (
        event_rows_for_export(
            monitor
        )
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    csv_bytes = (
        export_df
        .to_csv(
            index=False,
        )
        .encode("utf-8-sig")
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            t["download_csv"],
            data=csv_bytes,
            file_name=(
                f"hse_review_events_{timestamp}.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key=f"{key_prefix}_csv",
        )

    with col2:
        try:
            xlsx_bytes = (
                build_excel_bytes(
                    monitor
                )
            )

        except ImportError:
            # Excel export is optional. CSV remains available without
            # exposing dependency warnings to the end user.
            pass

def process_video_background(
    job_id,
    video_path,
    selected_ppe,
):

    # Modelo independiente para evitar conflictos
    # con Cámara o Video normal.
    worker_detector = PPEDetector(
        model_path=MODEL_PATH,
        confidence=0.25,
    )

    monitor = SceneEventMonitor()

    cap = cv2.VideoCapture(
        str(video_path)
    )

    source_fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    TARGET_FPS = 10.0

    frame_step = max(
        1,
        round(source_fps / TARGET_FPS)
    )

    frame_index = 0
    processed_frames = 0

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    processed_frames = 0

    try:

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            frame_index += 1

            # Saltar frames que no necesitamos analizar
            if frame_index % frame_step != 0:
                continue

            timestamp_seconds = (
                cap.get(
                    cv2.CAP_PROP_POS_MSEC
                )
                / 1000.0
            )

            result = worker_detector.predict(
                frame
            )

            detections = (
                worker_detector.get_detections(
                    result
                )
            )

            monitor.update(
                detections,
                selected_ppe,
                timestamp_seconds,
                frame=frame,
            )

            processed_frames += 1

            progress = (
                frame_index / total_frames
                if total_frames
                else 0.0
            )

            with background_jobs["lock"]:

                background_jobs["jobs"][
                    job_id
                ]["progress"] = progress

        final_time = (
            cap.get(
                cv2.CAP_PROP_POS_MSEC
            )
            / 1000.0
        )

        monitor.finalize(
            final_time
        )

        with background_jobs["lock"]:

            background_jobs["jobs"][
                job_id
            ].update(
                {
                    "status": "completed",
                    "progress": 1.0,
                    "monitor": monitor,
                }
            )

    except Exception as exc:

        with background_jobs["lock"]:

            background_jobs["jobs"][
                job_id
            ].update(
                {
                    "status": "error",
                    "error": str(exc),
                }
            )

    finally:

        cap.release()

        try:
            Path(video_path).unlink(missing_ok=True)
        except Exception:
            pass

def footer():
    st.markdown(
        """
        <div class="app-footer">
            Developed September 2026 by Nahuel Soliz —
            <a
                href="https://www.linkedin.com/in/nahuelsoliz/"
                target="_blank"
                rel="noopener noreferrer"
            >
                Follow me on LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    (
        '<div class="hero">'
        '<div class="hero-title">EPP DETECTOR</div>'
        f'<div class="hero-subtitle">{t["description"]}</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)


# ============================================================
# SOURCE
# ============================================================

if "source" not in st.session_state:
    st.session_state.source = None

col1, col2 = st.columns(2)

with col1:
    if st.button(
        t["image"],
        use_container_width=True,
    ):
        st.session_state.source = "Image"

with col2:
    if st.button(
        t["video"],
        use_container_width=True,
    ):
        st.session_state.source = "Video"


col3, col4 = st.columns(2)

with col3:
    if st.button(
        t["camera"],
        use_container_width=True,
    ):
        st.session_state.source = "Webcam"

with col4:
    if st.button(
        t["background"],
        use_container_width=True,
    ):
        st.session_state.source = "Background"

source = st.session_state.source


# ============================================================
# SOURCE SESSION INIT
# ============================================================

if (
    source is not None
    and
    st.session_state.get(
        "_last_source"
    ) != source
):
    st.session_state._last_source = (
        source
    )

    if source == "Video":
        old_cap = st.session_state.get(
            "video_cap"
        )

        if old_cap is not None:
            try:
                old_cap.release()
            except Exception:
                pass

        st.session_state.video_hash = None
        st.session_state.video_cap = None
        st.session_state.video_monitor = (
            SceneEventMonitor()
        )
        st.session_state.video_finished = False
        st.session_state.video_paused = False
        st.session_state.video_last_frame = None
        st.session_state.video_last_scene = (
            analyze_scene(
                {},
                REQUIRED_PPE,
            )
        )

    elif source == "Webcam":
        st.session_state.camera_monitor = (
            SceneEventMonitor()
        )
        st.session_state.camera_started_at = (
            time.monotonic()
        )

        st.session_state.camera_queue = Queue(
            maxsize=1
        )

        st.session_state.camera_last_scene = (
            analyze_scene(
                {},
                REQUIRED_PPE,
            )
        )


# ============================================================
# DESCRIPTION + FILTER
# ============================================================

selected_ppe = list(
    REQUIRED_PPE
)

section_description = SECTION_INFO.get(
    language, {}
).get(source)

if section_description:
    st.markdown(
        (
            '<div class="section-description">'
            f'{section_description}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    info_panel(
        t["ppe_title"],
        t["ppe_intro"],
    )

    selected_ppe = st.multiselect(
        t["ppe_selector"],
        options=REQUIRED_PPE,
        default=REQUIRED_PPE,
        format_func=lambda ppe: (
            DISPLAY_NAMES[language].get(
                ppe,
                ppe,
            )
        ),
    )

    if not selected_ppe:
        st.warning(
            t["no_ppe"]
        )


# ============================================================
# IMAGE
# ============================================================

if source == "Image":
    uploaded_file = st.file_uploader(
        t["upload_image"],
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
    )

    if uploaded_file:
        image = (
            Image.open(
                uploaded_file
            )
            .convert("RGB")
        )

        frame_rgb = np.array(
            image
        )

        frame = cv2.cvtColor(
            frame_rgb,
            cv2.COLOR_RGB2BGR,
        )

        result = detector.predict(
            frame
        )

        detections = (
            detector.get_detections(
                result
            )
        )

        scene = analyze_scene(
            detections,
            selected_ppe,
        )

        annotated = detector.draw(
            frame,
            result,
            display_names=DISPLAY_NAMES[
                language
            ],
        )

        c1, c2 = st.columns(2)

        with c1:
            st.subheader(
                t["original"]
            )
            st.image(
                frame_rgb,
                use_container_width=True,
            )

        with c2:
            st.subheader(
                t["detection"]
            )
            st.image(
                cv2.cvtColor(
                    annotated,
                    cv2.COLOR_BGR2RGB,
                ),
                use_container_width=True,
            )

        render_monitor(
            scene
        )


# ============================================================
# VIDEO
# ============================================================

elif source == "Video":

    use_sample = st.checkbox(
        t["sample_video"]
    )

    uploaded_file = None

    if not use_sample:

        uploaded_file = st.file_uploader(
            t["upload_video"],
            type=[
                "mp4",
                "avi",
                "mov",
                "mkv",
            ],
        )

    video_bytes = None

    if use_sample:

        if SAMPLE_VIDEO.exists():

            video_bytes = SAMPLE_VIDEO.read_bytes()

        else:

            st.error(
                "Sample video not found."
                if language == "en"
                else "No se encontró el video de muestra."
            )

    elif uploaded_file:

        video_bytes = uploaded_file.getvalue()

    if video_bytes:
        file_bytes = video_bytes

        video_hash = sha1(
            file_bytes
        ).hexdigest()

        if (
            st.session_state.get(
                "video_hash"
            ) != video_hash
        ):
            temp_path = (
                PROJECT_ROOT
                / "temp_video.mp4"
            )

            with open(
                temp_path,
                "wb",
            ) as f:
                f.write(
                    file_bytes
                )

            old_cap = st.session_state.get(
                "video_cap"
            )

            if old_cap is not None:
                try:
                    old_cap.release()
                except Exception:
                    pass

            st.session_state.video_hash = (
                video_hash
            )

            st.session_state.video_cap = (
                cv2.VideoCapture(
                    str(temp_path)
                )
            )

            st.session_state.video_monitor = (
                SceneEventMonitor()
            )

            st.session_state.video_finished = False
            st.session_state.video_paused = False
            st.session_state.video_last_frame = None
            st.session_state.video_last_scene = (
                analyze_scene(
                    {},
                    selected_ppe,
                )
            )

        monitor = (
            st.session_state.video_monitor
        )

        def restart_video():
            cap = st.session_state.get(
                "video_cap"
            )

            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass

            temp_path = (
                PROJECT_ROOT
                / "temp_video.mp4"
            )

            st.session_state.video_cap = (
                cv2.VideoCapture(
                    str(temp_path)
                )
            )

            monitor.reset()

            st.session_state.video_finished = False
            st.session_state.video_paused = False
            st.session_state.video_last_frame = None
            st.session_state.video_last_scene = (
                analyze_scene(
                    {},
                    selected_ppe,
                )
            )

        controls1, controls2 = (
            st.columns(2)
        )

        with controls1:
            pause_label = (
                t["resume"]
                if st.session_state.video_paused
                else t["pause"]
            )

            if st.button(
                pause_label,
                use_container_width=True,
                key="video_pause",
            ):
                st.session_state.video_paused = (
                    not st.session_state.video_paused
                )

        with controls2:
            if st.button(
                t["restart"],
                use_container_width=True,
                key="video_restart",
            ):
                restart_video()

        frame_placeholder = st.empty()
        stats_placeholder = st.empty()
        monitor_placeholder = st.empty()
        events_placeholder = st.empty()

        cap = (
            st.session_state.video_cap
        )

        source_fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if (
            not source_fps
            or source_fps <= 0
        ):
            source_fps = 30.0

        frame_duration = (
            1.0 / source_fps
        )

        last_ui_update = 0.0

        while (
            cap.isOpened()
            and
            not st.session_state.video_paused
            and
            not st.session_state.video_finished
        ):
            loop_start = (
                time.perf_counter()
            )

            ret, frame = cap.read()

            if not ret:
                st.session_state.video_finished = True

                final_time = (
                    cap.get(
                        cv2.CAP_PROP_POS_MSEC
                    )
                    / 1000.0
                )

                monitor.finalize(
                    final_time
                )

                break

            timestamp_seconds = (
                cap.get(
                    cv2.CAP_PROP_POS_MSEC
                )
                / 1000.0
            )

            inference_start = (
                time.perf_counter()
            )

            # NO TRACKING
            result = detector.predict(
                frame
            )

            inference_time = (
                time.perf_counter()
                - inference_start
            )

            detections = (
                detector.get_detections(
                    result
                )
            )

            monitor_data = monitor.update(
                detections,
                selected_ppe,
                timestamp_seconds,
                frame=frame,
            )

            scene = monitor_data[
                "scene"
            ]

            st.session_state.video_last_scene = (
                scene
            )

            annotated = detector.draw(
                frame,
                result,
                display_names=DISPLAY_NAMES[
                    language
                ],
            )

            frame_rgb = cv2.cvtColor(
                annotated,
                cv2.COLOR_BGR2RGB,
            )

            st.session_state.video_last_frame = (
                frame_rgb
            )

            frame_placeholder.image(
                frame_rgb,
                channels="RGB",
                use_container_width=True,
            )

            elapsed = (
                time.perf_counter()
                - loop_start
            )

            processing_fps = (
                1.0 / elapsed
                if elapsed > 0
                else 0.0
            )

            stats_placeholder.caption(
                f"Source: {source_fps:.1f} FPS · "
                f"Processing: {processing_fps:.1f} FPS · "
                f"Inference: {inference_time * 1000:.1f} ms"
            )

            # Dashboard/events only 2x/sec. They do not block every frame.
            if (
                timestamp_seconds
                - last_ui_update
            ) >= 0.5:
                with monitor_placeholder.container():
                    render_monitor(
                        scene
                    )

                with events_placeholder.container():
                    render_events(
                        monitor,
                        key_prefix="video_live",
                        allow_export=False,
                    )

                last_ui_update = (
                    timestamp_seconds
                )

            remaining = (
                frame_duration
                - (
                    time.perf_counter()
                    - loop_start
                )
            )

            if remaining > 0:
                time.sleep(
                    remaining
                )

        if (
            st.session_state.video_last_frame
            is not None
            and
            st.session_state.video_paused
        ):
            frame_placeholder.image(
                st.session_state.video_last_frame,
                channels="RGB",
                use_container_width=True,
            )

        if st.session_state.video_finished:
            st.success(
                t["finished"]
            )

        render_monitor(
            st.session_state.video_last_scene
        )

        render_events(
            monitor,
            key_prefix="video",
            allow_export=True,
        )


# ============================================================
# CAMERA
# ============================================================

elif source == "Webcam":

    if "camera_monitor" not in st.session_state:
        st.session_state.camera_monitor = (
            SceneEventMonitor()
        )

    if "camera_queue" not in st.session_state:
        st.session_state.camera_queue = (
            Queue(maxsize=1)
        )

    if "camera_started_at" not in st.session_state:
        st.session_state.camera_started_at = (
            time.monotonic()
        )

    monitor = (
        st.session_state.camera_monitor
    )

    camera_queue = (
        st.session_state.camera_queue
    )

    # Copiamos el tiempo inicial fuera del callback.
    # Así evitamos consultar session_state
    # continuamente desde el thread de WebRTC.
    camera_started_at = (
        st.session_state.camera_started_at
    )

    # Copia local del filtro actual
    camera_selected_ppe = (
        selected_ppe.copy()
    )


    def video_frame_callback(
        frame: av.VideoFrame,
    ) -> av.VideoFrame:

        img = frame.to_ndarray(
            format="bgr24"
        )

        # ----------------------------------------------------
        # Evitar inferencias simultáneas
        # ----------------------------------------------------

        acquired = camera_inference_lock.acquire(
            blocking=False
        )

        if not acquired:

            # Si YOLO todavía está procesando otro frame,
            # devolvemos inmediatamente el frame actual.
            # Así WebRTC no acumula inferencias.
            return av.VideoFrame.from_ndarray(
                img,
                format="bgr24",
            )


        try:

            # ------------------------------------------------
            # YOLO
            # ------------------------------------------------

            result = detector.predict(
                img
            )


            # ------------------------------------------------
            # DETECTIONS
            # ------------------------------------------------

            detections = (
                detector.get_detections(
                    result
                )
            )


            # ------------------------------------------------
            # TIMESTAMP
            # ------------------------------------------------

            timestamp_seconds = (
                time.monotonic()
                - camera_started_at
            )


            # ------------------------------------------------
            # EVENT MONITOR
            # ------------------------------------------------

            data = monitor.update(
                detections,
                camera_selected_ppe,
                timestamp_seconds,
                frame=img,
            )


            # ------------------------------------------------
            # DASHBOARD QUEUE
            # ------------------------------------------------

            try:

                if camera_queue.full():
                    camera_queue.get_nowait()

                camera_queue.put_nowait(
                    data
                )

            except Exception:
                pass


            # ------------------------------------------------
            # DRAW DETECTIONS
            # ------------------------------------------------

            annotated = detector.draw(
                img,
                result,
                display_names=DISPLAY_NAMES[
                    language
                ],
            )


            return av.VideoFrame.from_ndarray(
                annotated,
                format="bgr24",
            )


        finally:

            camera_inference_lock.release()


    # ========================================================
    # WEBRTC
    # ========================================================

    webrtc_ctx = webrtc_streamer(
        key="ppe-webcam",

        mode=WebRtcMode.SENDRECV,

        video_frame_callback=video_frame_callback,

        media_stream_constraints={
            "video": True,
            "audio": False,
        },

        async_processing=True,
    )


    camera_playing = bool(
        webrtc_ctx.state.playing
    )


    # ========================================================
    # LAST DASHBOARD STATE
    # ========================================================

    if not camera_playing:

        try:

            while True:

                data = (
                    camera_queue.get_nowait()
                )

                st.session_state.camera_last_scene = (
                    data["scene"]
                )

        except Empty:
            pass


    # ========================================================
    # DASHBOARD REFRESH
    # ========================================================

    camera_run_every = (
        0.5
        if camera_playing
        else None
    )


    @st.fragment(
        run_every=camera_run_every
    )
    def camera_monitor_fragment():

        try:

            while True:

                data = (
                    camera_queue.get_nowait()
                )

                st.session_state.camera_last_scene = (
                    data["scene"]
                )

        except Empty:
            pass


        scene = st.session_state.get(
            "camera_last_scene",

            analyze_scene(
                {},
                camera_selected_ppe,
            ),
        )


        render_monitor(
            scene
        )


        render_events(
            monitor,

            key_prefix="camera",

            allow_export=(
                not camera_playing
            ),
        )


        # ----------------------------------------------------
        # RESET SESSION
        # ----------------------------------------------------

        if not camera_playing:

            if st.button(
                t["reset"],

                key="camera_reset",

                use_container_width=True,
            ):

                monitor.reset()

                st.session_state.camera_started_at = (
                    time.monotonic()
                )

                st.session_state.camera_last_scene = (
                    analyze_scene(
                        {},
                        camera_selected_ppe,
                    )
                )

                st.rerun()


    camera_monitor_fragment()

# ============================================================
# BACKGROUND VIDEO
# ============================================================

elif source == "Background":

    uploaded_file = st.file_uploader(
        t["background_upload"],
        type=[
            "mp4",
            "avi",
            "mov",
            "mkv",
        ],
        key="background_video",
    )

    if uploaded_file:

        if st.button(
            t["background_start"],
            use_container_width=True,
        ):

            job_id = str(
                uuid.uuid4()
            )

            temp_path = (
                PROJECT_ROOT
                / f"background_{job_id}.mp4"
            )

            with open(
                temp_path,
                "wb",
            ) as f:

                f.write(
                    uploaded_file.getvalue()
                )

            with background_jobs["lock"]:

                background_jobs["jobs"][
                    job_id
                ] = {
                    "status": "processing",
                    "progress": 0.0,
                    "monitor": None,
                    "error": None,
                }

            st.session_state.background_job_id = (
                job_id
            )

            thread = Thread(
                target=process_video_background,
                args=(
                    job_id,
                    temp_path,
                    selected_ppe.copy(),
                ),
                daemon=True,
            )

            thread.start()

            st.rerun()

    job_id = st.session_state.get(
        "background_job_id"
    )

    if job_id:

        with background_jobs["lock"]:

            job = (
                background_jobs["jobs"]
                .get(job_id)
            )

        if job:

            if job["status"] == "processing":

                st.info(
                    t["background_processing"]
                )

                st.progress(
                    job["progress"]
                )

                time.sleep(0.5)
                st.rerun()

            elif job["status"] == "completed":

                st.success(
                    t["background_completed"]
                )

                monitor = job["monitor"]

                render_monitor(
                    monitor.snapshot()["scene"]
                )

                render_events(
                    monitor,
                    key_prefix="background",
                    allow_export=True,
                )

            elif job["status"] == "error":

                st.error(
                    job["error"]
                )

# ============================================================
# FOOTER
# ============================================================

footer()
