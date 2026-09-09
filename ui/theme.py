import random

import streamlit as st


THEMES = {
    "Quantum Violet": {
        "accent": "#a78bfa", "accent2": "#7c3aed",
        "rgb": "167,139,250", "node": "140, 95, 220", "link": "150, 105, 230",
    },
    "Neural Blue": {
        "accent": "#38bdf8", "accent2": "#2563eb",
        "rgb": "56,189,248", "node": "56, 189, 248", "link": "59, 130, 246",
    },
    "Matrix Emerald": {
        "accent": "#34d399", "accent2": "#059669",
        "rgb": "52,211,153", "node": "52, 211, 153", "link": "16, 185, 129",
    },
}


def apply_theme(theme_name="Quantum Violet"):
    palette = THEMES.get(theme_name, THEMES["Quantum Violet"])

    css = """
        <style>

        /* =========================
           APP / CENTERED LAYOUT
        ========================== */

        .stApp {
            background:
                radial-gradient(circle at 18% 18%,
                    rgba(126, 34, 206, 0.16),
                    transparent 32%),
                radial-gradient(circle at 82% 72%,
                    rgba(99, 102, 241, 0.18),
                    transparent 36%),
                radial-gradient(circle at 55% 45%,
                    rgba(168, 85, 247, 0.07),
                    transparent 42%),
                linear-gradient(
                    135deg,
                    #05020d,
                    #0a0618 45%,
                    #100922
                );

            color: white;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        .block-container {
            width: 100%;
            max-width: 940px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-top: 1.2rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
        }

        /* Keep Streamlit content above particles */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .block-container {
            position: relative;
            z-index: 2;
        }


        /* =========================
           HERO
        ========================== */

        .hero {
            text-align: center;
            padding-top: 42px;
            padding-bottom: 22px;
            position: relative;
            z-index: 3;
        }

        .hero-title {
            font-family: "Segoe UI", sans-serif;
            font-size: 3.4rem;
            font-weight: 800;
            letter-spacing: 3px;

            color: #ffffff;
            -webkit-text-fill-color: #ffffff;

            text-shadow:
                0 0 6px rgba(255, 255, 255, 0.18),
                0 0 14px rgba(167, 139, 250, 0.12);
        }

        .hero-subtitle {
            color: #a7b0c0;
            font-size: 1.10rem;
            max-width: 720px;
            margin: auto;
            line-height: 1.7;
        }


        /* =========================
           SECTION DESCRIPTION
        ========================== */

        .section-description {
            text-align: center;
            color: #b0b9c7;
            font-size: 1.02rem;
            line-height: 1.65;
            margin: 14px auto 22px auto;
            max-width: 760px;
            position: relative;
            z-index: 3;
        }


        /* =========================
           TOP CONTROLS
        ========================== */

        div[data-testid="stSelectbox"] {
            position: relative;
            z-index: 1000;
        }

        div[data-testid="stSelectbox"] > div {
            min-width: 0 !important;
        }

        div[data-baseweb="select"] > div {
            min-height: 32px !important;
            height: 32px !important;
            border-radius: 9px !important;
            padding-left: 7px !important;
            padding-right: 3px !important;
            font-size: 0.78rem !important;
        }

        div[data-baseweb="select"] span {
            font-size: 0.78rem !important;
            white-space: nowrap !important;
        }

        div[data-baseweb="popover"],
        div[role="listbox"] {
            z-index: 999999 !important;
        }

        /* =========================
           NEURAL PROCESSING
        ========================== */

        .neural-panel {
            background: #07101d;
            border: 1px solid rgba(167,139,250,.16);
            border-radius: 12px;
            padding: 11px 14px;
            margin: 8px 0 6px 0;
            position: relative;
            z-index: 3;
        }

        .neural-title {
            color: #ffffff;
            font-size: .92rem;
            font-weight: 750;
            margin-bottom: 3px;
        }

        .neural-text {
            color: #9eabbc;
            font-size: .82rem;
            line-height: 1.45;
        }

        /* =========================
           LANGUAGE
        ========================== */

        .language-icon {
            font-size: 1.20rem;
            line-height: 1;
            text-align: right;
            padding-top: 3px;
        }


        /* =========================
           BUTTONS
        ========================== */

        div[data-testid="stButton"] > button {
            width: 100%;
            min-height: 70px;
            border-radius: 14px;

            background:
                linear-gradient(
                    145deg,
                    rgba(20,30,50,.82),
                    rgba(10,18,32,.88)
                );

            border:
                1px solid rgba(167,139,250,.28);

            color: #ffffff;

            font-size: 1.08rem;
            font-weight: 700;

            backdrop-filter: blur(12px);

            box-shadow:
                0 8px 24px rgba(0,0,0,.22);

            transition:
                transform .22s ease,
                border-color .22s ease,
                box-shadow .22s ease;
        }

        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px);

            border-color: rgba(167,139,250,.75);

            box-shadow:
                0 12px 28px rgba(0,0,0,.32),
                0 0 18px rgba(167,139,250,.14);
        }

        div[data-testid="stButton"] > button p {
            font-size: 1.08rem;
            font-weight: 700;
            margin: 0;
        }


        /* =========================
           STANDARD STREAMLIT TEXT
        ========================== */

        [data-testid="stCaptionContainer"] p {
            font-size: 0.90rem !important;
        }

        [data-testid="stAlertContainer"] p {
            font-size: 0.98rem !important;
        }

        [data-testid="stWidgetLabel"] p {
            font-size: 0.96rem !important;
        }


        /* =========================
           MEDIA
        ========================== */

        img,
        video {
            border-radius: 14px;

            box-shadow:
                0 10px 35px rgba(0,0,0,.4);
        }


        /* =========================
           INFO PANELS
        ========================== */

        .info-panel {
            background: #07101d;

            border:
                1px solid rgba(167, 139, 250, 0.16);

            border-radius: 14px;

            padding: 15px 17px;
            margin: 12px 0 18px 0;

            box-shadow:
                0 8px 22px rgba(0,0,0,.24);

            position: relative;
            z-index: 3;
        }

        .info-panel-title {
            color: #ffffff;
            font-size: 1.00rem;
            font-weight: 750;
            margin-bottom: 6px;
        }

        .info-panel-text {
            color: #a9b5c6;
            font-size: 0.94rem;
            line-height: 1.62;
        }


        /* =========================
           DASHBOARD
        ========================== */

        .dashboard-shell {
            background: #050c16;

            border:
                1px solid rgba(167,139,250,.16);

            border-radius: 18px;

            padding: 21px;
            margin: 18px 0;

            box-shadow:
                0 14px 36px rgba(0,0,0,.35);

            position: relative;
            z-index: 3;
        }

        .dashboard-main-title {
            color: #ffffff;
            font-size: 1.16rem;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .dashboard-note {
            color: #9aa9bc;
            font-size: 0.90rem;
            line-height: 1.58;
            margin-bottom: 19px;
        }

        .dashboard-grid {
            display: grid;

            grid-template-columns:
                repeat(4, minmax(0, 1fr));

            gap: 11px;
            margin-bottom: 20px;
        }

        .dashboard-card {
            background: #0a1422;

            border:
                1px solid rgba(255,255,255,.07);

            border-radius: 12px;

            padding: 14px;
            min-height: 92px;
        }

        .dashboard-label {
            color: #98a6ba;
            font-size: 0.79rem;
            line-height: 1.35;
            min-height: 36px;
        }

        .dashboard-value {
            color: #ffffff;
            font-size: 1.72rem;
            font-weight: 800;
        }

        .dashboard-priority {
            color: #a78bfa;
            font-size: 1.08rem;
            font-weight: 750;
            margin-top: 7px;
        }

        .dashboard-section-title {
            color: #e1eaf4;
            font-size: 0.95rem;
            font-weight: 750;
            margin: 15px 0 10px 0;
        }

        .ppe-row {
            margin: 10px 0;
        }

        .ppe-row-header {
            display: flex;
            justify-content: space-between;

            color: #d2dce8;

            font-size: 0.88rem;

            margin-bottom: 6px;
        }

        .ppe-bar {
            height: 7px;
            border-radius: 999px;
            overflow: hidden;
            background: #101d2c;
        }

        .ppe-bar-fill {
            height: 100%;
            border-radius: 999px;

            background:
                linear-gradient(
                    90deg,
                    #7c3aed,
                    #a78bfa
                );
        }


        /* =========================
           EVENT LOG
        ========================== */

        .event-card {
            display: flex;
            align-items: center;

            gap: 14px;

            min-height: 96px;

            padding: 10px 13px;
            margin: 9px 0;

            background: #07101d;

            border:
                1px solid rgba(167,139,250,.13);

            border-radius: 13px;

            box-shadow:
                0 7px 20px rgba(0,0,0,.20);

            position: relative;
            z-index: 3;
        }

        .event-thumb {
            width: 76px;
            height: 76px;
            min-width: 76px;

            object-fit: cover;

            border-radius: 9px;

            border:
                1px solid rgba(255,255,255,.10);

            box-shadow: none;
        }

        .event-thumb-empty {
            display: flex;
            align-items: center;
            justify-content: center;

            background: #0c1726;
            color: #617087;
        }

        .event-body {
            flex: 1;
            min-width: 0;
        }

        .event-topline {
            display: flex;
            align-items: center;
            gap: 9px;
            flex-wrap: wrap;
            margin-bottom: 6px;
        }

        .event-id {
            color: #8090a6;
            font-size: 0.82rem;
            font-weight: 700;
        }

        .event-ppe {
            color: #ffffff;
            font-size: 0.99rem;
            font-weight: 800;
        }

        .event-status {
            margin-left: auto;

            color: #a78bfa;

            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: .4px;
        }

        .event-time {
            color: #d0d9e5;
            font-size: 0.87rem;
            margin-bottom: 4px;
        }

        .event-detail {
            color: #92a1b5;
            font-size: 0.81rem;
            line-height: 1.42;
        }


        /* =========================
           FOOTER
        ========================== */

        .app-footer {
            text-align: center;

            margin-top: 48px;

            padding:
                22px 10px 10px 10px;

            color: #8390a4;

            font-size: 0.88rem;

            border-top:
                1px solid rgba(167,139,250,.10);

            position: relative;
            z-index: 3;
        }

        .app-footer a {
            color: #a78bfa;

            text-decoration: none;

            font-weight: 650;
        }

        .app-footer a:hover {
            color: #ffffff;
        }


        /* =========================
           RESPONSIVE
        ========================== */

        @media (max-width: 760px) {

            .block-container {
                max-width: 100% !important;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-title {
                font-size: 2.25rem;
            }

            .hero-subtitle {
                font-size: 1.00rem;
            }

            .dashboard-grid {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }

            .event-thumb {
                width: 66px;
                height: 66px;
                min-width: 66px;
            }
        }

        
        /* =========================
           AI GALACTIC PARTICLES
        ========================== */

        .galaxy-network {
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 1;
            overflow: hidden;
        }

        .galaxy-node {
            position: absolute;
            width: var(--size);
            height: var(--size);
            border-radius: 50%;

            background: rgba(140, 95, 255, 0.95);

            box-shadow:
                0 0 6px rgba(140, 95, 255, 0.85),
                0 0 14px rgba(70, 180, 255, 0.30);

            opacity: var(--opacity);

            animation:
                nodePulse var(--pulse)
                ease-in-out infinite alternate,
                nodeDrift var(--drift)
                ease-in-out infinite alternate;

            animation-delay:
                0s,
                var(--delay);
        }

        .galaxy-link {
            position: absolute;
            height: 1px;
            width: var(--length);

            transform-origin: left center;

            background:
                linear-gradient(
                    90deg,
                    rgba(130, 80, 255, 0.18),
                    rgba(80, 170, 255, 0.16),
                    rgba(130, 80, 255, 0.10)
                );

            opacity: var(--opacity);

            animation:
                linkDrift var(--drift)
                ease-in-out infinite alternate;

            animation-delay:
                var(--delay);
        }

        @keyframes nodePulse {
            from {
                opacity: .35;
            }

            to {
                opacity: .95;
            }
        }

        @keyframes nodeDrift {
            from {
                translate: -5px 3px;
                scale: .88;
            }

            to {
                translate: 6px -5px;
                scale: 1.15;
            }
        }

        @keyframes linkDrift {
            from {
                transform:
                    translate(-4px, 3px)
                    rotate(var(--angle));
            }

            to {
                transform:
                    translate(6px, -5px)
                    rotate(var(--angle));
            }
        }

        </style>
        """

    if theme_name != "Quantum Violet":
        css = (
            css
            .replace("#a78bfa", palette["accent"])
            .replace("#7c3aed", palette["accent2"])
            .replace("167,139,250", palette["rgb"])
            .replace("167, 139, 250", palette["rgb"].replace(",", ", "))
            .replace("126, 34, 206", palette["rgb"].replace(",", ", "))
            .replace("99, 102, 241", palette["rgb"].replace(",", ", "))
            .replace("168, 85, 247", palette["rgb"].replace(",", ", "))
        )

    st.markdown(css, unsafe_allow_html=True)


def particles(theme_name="Quantum Violet"):
    palette = THEMES.get(theme_name, THEMES["Quantum Violet"])
    """
    Sparse AI constellation network:
    tiny violet nodes, very thin faint links, slow organic movement.
    Inspired by the reference style previously shared by the user.
    """
    import streamlit.components.v1 as components

    html_code = """
        <script>
        (() => {
            const DOC = window.parent.document;
            const WIN = window.parent;

            const oldCanvas = DOC.getElementById("hse-godin-network");
            if (oldCanvas) oldCanvas.remove();

            const canvas = DOC.createElement("canvas");
            canvas.id = "hse-godin-network";

            Object.assign(canvas.style, {
                position: "fixed",
                inset: "0",
                width: "100vw",
                height: "100vh",
                pointerEvents: "none",
                zIndex: "1",
                opacity: "1"
            });

            DOC.body.appendChild(canvas);

            const ctx = canvas.getContext("2d");

            const mouse = {
                x: null,
                y: null,
                active: false
            };

            WIN.addEventListener(
                "mousemove",
                (event) => {
                    mouse.x = event.clientX;
                    mouse.y = event.clientY;
                    mouse.active = true;
                },
                { passive: true }
            );

            WIN.addEventListener(
                "mouseleave",
                () => {
                    mouse.active = false;
                }
            );

            let width = WIN.innerWidth;
            let height = WIN.innerHeight;
            let dpr = Math.max(1, Math.min(2, WIN.devicePixelRatio || 1));

            function resize() {
                width = WIN.innerWidth;
                height = WIN.innerHeight;
                dpr = Math.max(1, Math.min(2, WIN.devicePixelRatio || 1));

                canvas.width = Math.floor(width * dpr);
                canvas.height = Math.floor(height * dpr);

                canvas.style.width = width + "px";
                canvas.style.height = height + "px";

                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            }

            resize();
            WIN.addEventListener("resize", resize);

            // Sparse field, like the reference image.
            const NODE_COUNT = Math.max(
                55,
                Math.min(
                    95,
                    Math.floor((width * height) / 18000)
                )
            );

            const nodes = Array.from(
                { length: NODE_COUNT },
                () => ({
                    x: Math.random() * width,
                    y: Math.random() * height,

                    vx: (Math.random() - 0.5) * 0.10,
                    vy: (Math.random() - 0.5) * 0.10,

                    r: 1.0 + Math.random() * 0.65,

                    phase: Math.random() * Math.PI * 2
                })
            );

            const LINK_DISTANCE = 145;

            function wrap(node) {
                if (node.x < -8) node.x = width + 8;
                if (node.x > width + 8) node.x = -8;

                if (node.y < -8) node.y = height + 8;
                if (node.y > height + 8) node.y = -8;
            }

            function update(node) {
                node.x += node.vx;
                node.y += node.vy;

                // Tiny organic drift so motion never looks mechanical.
                node.phase += 0.0025;

                node.vx += Math.sin(node.phase) * 0.00035;
                node.vy += Math.cos(node.phase * 0.9) * 0.00035;

                // Soft cursor attraction: preserves the existing organic drift.
                if (mouse.active) {
                    const dx = mouse.x - node.x;
                    const dy = mouse.y - node.y;
                    const distance = Math.hypot(dx, dy);
                    const radius = 190;

                    if (distance > 1 && distance < radius) {
                        const force = (1 - distance / radius) * 0.004;
                        node.vx += (dx / distance) * force;
                        node.vy += (dy / distance) * force;
                    }
                }

                // Very soft cap.
                const speed = Math.hypot(node.vx, node.vy);

                if (speed > 0.16) {
                    node.vx *= 0.985;
                    node.vy *= 0.985;
                }

                wrap(node);
            }

            function drawLinks() {
                for (let i = 0; i < nodes.length; i++) {
                    for (let j = i + 1; j < nodes.length; j++) {
                        const a = nodes[i];
                        const b = nodes[j];

                        const dx = b.x - a.x;
                        const dy = b.y - a.y;
                        const dist = Math.hypot(dx, dy);

                        if (dist > LINK_DISTANCE) continue;

                        let alpha =
                            (1 - dist / LINK_DISTANCE) * 0.23;

                        if (mouse.active) {
                            const midX = (a.x + b.x) / 2;
                            const midY = (a.y + b.y) / 2;
                            const mouseDistance = Math.hypot(
                                mouse.x - midX,
                                mouse.y - midY
                            );

                            if (mouseDistance < 180) {
                                alpha *= 1.6;
                            }
                        }

                        ctx.beginPath();

                        ctx.strokeStyle =
                            `rgba(150, 105, 230, ${alpha})`;

                        ctx.lineWidth = 0.55;

                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);

                        ctx.stroke();
                    }
                }
            }

            function drawNodes() {
                for (const node of nodes) {
                    const pulse =
                        0.72 + Math.sin(node.phase * 2.2) * 0.18;

                    // subtle halo
                    ctx.beginPath();

                    ctx.fillStyle =
                        `rgba(105, 72, 175, ${0.16 * pulse})`;

                    ctx.arc(
                        node.x,
                        node.y,
                        node.r * 1.7,
                        0,
                        Math.PI * 2
                    );

                    ctx.fill();

                    // tiny violet point
                    ctx.beginPath();

                    ctx.fillStyle =
                        `rgba(140, 95, 220, ${0.95 * pulse})`;

                    ctx.arc(
                        node.x,
                        node.y,
                        node.r,
                        0,
                        Math.PI * 2
                    );

                    ctx.fill();
                }
            }

            let raf = null;

            function animate() {
                ctx.clearRect(0, 0, width, height);

                for (const node of nodes) {
                    update(node);
                }

                drawLinks();
                drawNodes();

                raf = WIN.requestAnimationFrame(animate);
            }

            animate();

            WIN.addEventListener(
                "beforeunload",
                () => {
                    if (raf) WIN.cancelAnimationFrame(raf);
                    canvas.remove();
                }
            );
        })();
        </script>
        """

    if theme_name != "Quantum Violet":
        html_code = (
            html_code
            .replace("150, 105, 230", palette["link"])
            .replace("140, 95, 220", palette["node"])
            .replace("105, 72, 175", palette["node"])
        )

    components.html(
        html_code,
        height=1,
        scrolling=False,
    )
