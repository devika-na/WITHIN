import time
from pathlib import Path

import gradio as gr

from within.t2i_pipeline import WITHINT2IPipeline
from within.i2i_pipeline import WITHINI2IPipeline


# ============================================================
# PATHS / BACKEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Initializing WITHIN...")

t2i_pipeline = WITHINT2IPipeline()
i2i_pipeline = WITHINI2IPipeline()

print("WITHIN ready.")


# ============================================================
# UI HELPERS
# ============================================================

def prompt_safety_html(result):
    if not result:
        return ""

    decision = result.get("decision", "UNKNOWN")
    category = result.get("category")
    reason = result.get("reason", "")

    if decision == "ALLOW":
        label = "ALLOW"
        detail = "No restricted content detected."
    elif decision == "RESTRICT":
        label = "RESTRICT"
        detail = f"{category or 'Sensitive content'} · {reason}"
    else:
        label = "BLOCK"
        detail = f"{category or 'High-risk content'} · {reason}"

    return f"""
    <div class="status-row">
        <div class="status-label">PROMPT SAFETY</div>
        <div class="status-value {decision.lower()}">{label}</div>
        <div class="status-detail">{detail}</div>
    </div>
    """


def output_safety_html(result):
    if not result:
        return ""

    safe = result.get("safe", False)
    nsfw = result.get("nsfw_detected", False)

    if safe:
        label = "PASS"
        cls = "allow"
        detail = "Local safety checker passed."
    else:
        label = "BLOCK"
        cls = "block"
        detail = "NSFW concept detected locally."

    return f"""
    <div class="status-row">
        <div class="status-label">OUTPUT SAFETY</div>
        <div class="status-value {cls}">{label}</div>
        <div class="status-detail">{detail}</div>
    </div>
    """


def privacy_html(receipt_path):
    if not receipt_path:
        return ""

    return f"""
    <div class="receipt-box">
        <div class="receipt-title">PRIVACY RECEIPT</div>

        <div class="receipt-row">
            <span>Processing</span>
            <strong>LOCAL</strong>
        </div>

        <div class="receipt-row">
            <span>Cloud AI API</span>
            <strong>FALSE</strong>
        </div>

        <div class="receipt-row">
            <span>Network required</span>
            <strong>FALSE</strong>
        </div>

        <div class="receipt-row">
            <span>Receipt</span>
            <span class="receipt-path">{receipt_path}</span>
        </div>
    </div>
    """


def blocked_html(reason):
    return f"""
    <div class="blocked-box">
        <div class="blocked-title">GENERATION BLOCKED</div>
        <div class="blocked-reason">{reason}</div>
    </div>
    """


# ============================================================
# T2I
# ============================================================

def generate_t2i(prompt):
    if not prompt or not prompt.strip():
        return (
            None,
            "",
            "",
            "",
            "Enter a prompt.",
            None
        )

    start = time.time()

    output_path = OUTPUT_DIR / "within_t2i_final.png"

    try:
        result = t2i_pipeline.generate(
            prompt=prompt,
            output_path=output_path
        )

        elapsed = time.time() - start
        time_text = f"{elapsed:.1f}s"

        if result["status"] == "BLOCKED":
            return (
                None,
                prompt_safety_html(result.get("prompt_safety")),
                output_safety_html(result.get("safety")),
                "",
                blocked_html(result.get("reason", "Unsafe request.")),
                None
            )

        return (
            result.get("output"),
            prompt_safety_html(result.get("prompt_safety")),
            output_safety_html(result.get("safety")),
            privacy_html(result.get("privacy_receipt")),
            f"Generated locally · {time_text}",
            result.get("output")
        )

    except Exception as e:
        return (
            None,
            "",
            "",
            "",
            f"Generation error: {e}",
            None
        )


# ============================================================
# I2I
# ============================================================

def generate_i2i(input_image, prompt):
    if input_image is None:
        return (
            None,
            "",
            "",
            "",
            "Upload an input image.",
            None
        )

    if not prompt or not prompt.strip():
        return (
            None,
            "",
            "",
            "",
            "Enter a prompt.",
            None
        )

    start = time.time()

    input_path = Path(input_image)
    output_path = OUTPUT_DIR / "within_i2i_final.png"

    try:
        result = i2i_pipeline.generate(
            prompt=prompt,
            input_path=input_path,
            output_path=output_path
        )

        elapsed = time.time() - start
        time_text = f"{elapsed:.1f}s"

        if result["status"] == "BLOCKED":
            return (
                None,
                prompt_safety_html(result.get("prompt_safety")),
                output_safety_html(
                    result.get("output_safety")
                    or result.get("input_safety")
                ),
                "",
                blocked_html(result.get("reason", "Unsafe request.")),
                None
            )

        return (
            result.get("output"),
            prompt_safety_html(result.get("prompt_safety")),
            output_safety_html(result.get("output_safety")),
            privacy_html(result.get("privacy_receipt")),
            f"Edited locally · {time_text}",
            result.get("output")
        )

    except Exception as e:
        return (
            None,
            "",
            "",
            "",
            f"Generation error: {e}",
            None
        )


# ============================================================
# CLEAR
# ============================================================

def clear_t2i():
    return None, "", "", "", "", None


def clear_i2i():
    return None, "", "", "", "", None


# ============================================================
# CSS
# ============================================================

CSS = """

/* ============================================================
   WITHIN — Visual System v2
   ============================================================ */

:root {
    --bg: #101827;
    --bg-deep: #0b1220;
    --panel: #162033;
    --panel-raised: #1b2940;
    --panel-soft: #202e45;

    --border: #2a3a52;
    --border-bright: #3b506d;

    --text: #edf4ff;
    --text-soft: #c5d1e2;
    --muted: #8fa0b7;
    --dim: #667993;

    --indigo: #6366f1;
    --indigo-light: #818cf8;
    --cyan: #22d3ee;
    --cyan-soft: rgba(34,211,238,0.12);

    --success: #5eead4;
    --danger: #fb7185;

    --shadow: rgba(0,0,0,0.32);
}

/* ============================================================
   BASE
   ============================================================ */

* {
    box-sizing: border-box;
}

body {
    background: var(--bg-deep) !important;
    color: var(--text) !important;
    font-family:
        Inter,
        "Segoe UI",
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        sans-serif !important;
    font-size: 15px !important;
}

.gradio-container {
    max-width: none !important;
    padding: 0 !important;

    background:
        radial-gradient(
            circle at 78% 8%,
            rgba(99,102,241,0.14),
            transparent 28%
        ),
        radial-gradient(
            circle at 12% 88%,
            rgba(34,211,238,0.07),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #0b1220 0%,
            #101827 48%,
            #111c2e 100%
        ) !important;
}

/* ============================================================
   SCROLLBAR
   ============================================================ */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0d1523;
}

::-webkit-scrollbar-thumb {
    background: #34465f;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4a607e;
}

/* ============================================================
   TEXT
   ============================================================ */

h1,
h2,
h3,
h4,
p,
label {
    color: var(--text) !important;
}

h1 {
    font-weight: 700 !important;
    letter-spacing: -0.035em !important;
}

h2 {
    font-weight: 650 !important;
    letter-spacing: -0.025em !important;
}

label span {
    color: var(--text-soft) !important;
    font-size: 13px !important;
    font-weight: 550 !important;
}

/* ============================================================
   TOP BAR
   ============================================================ */

.topbar {
    height: 70px;
    padding: 0 30px !important;

    background: rgba(11,18,32,0.94) !important;
    border-bottom: 1px solid var(--border);

    display: flex;
    align-items: center;

    box-shadow: 0 8px 30px rgba(0,0,0,0.18);
}

.brand {
    display: flex;
    align-items: center;
    gap: 13px;
}

.brand-mark {
    width: 36px;
    height: 36px;

    border: 1px solid rgba(99,102,241,0.8);
    border-radius: 9px;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #ffffff;
    font-size: 14px;
    font-weight: 750;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.3),
            rgba(34,211,238,0.14)
        );

    box-shadow:
        0 0 25px rgba(99,102,241,0.16),
        inset 0 0 18px rgba(34,211,238,0.05);
}

.brand-name {
    font-size: 20px !important;
    font-weight: 750 !important;
    letter-spacing: 0.08em !important;
}

.brand-subtitle {
    color: var(--muted) !important;
    font-size: 12px !important;
    letter-spacing: 0.045em;
}

/* ============================================================
   LAYOUT
   ============================================================ */

.main-layout {
    min-height: calc(100vh - 70px);
}

.sidebar {
    background:
        linear-gradient(
            180deg,
            rgba(22,32,51,0.96),
            rgba(13,21,35,0.98)
        ) !important;

    border-right: 1px solid var(--border);

    padding: 28px 22px !important;

    box-shadow: 10px 0 35px rgba(0,0,0,0.12);
}

.workspace-area {
    padding: 34px 38px 44px !important;
    background: transparent !important;
}

/* ============================================================
   MODE TABS
   ============================================================ */

.mode-tabs {
    background: rgba(22,32,51,0.8) !important;

    border: 1px solid var(--border) !important;
    border-radius: 10px !important;

    padding: 5px !important;

    box-shadow:
        inset 0 1px rgba(255,255,255,0.025),
        0 10px 30px rgba(0,0,0,0.12);
}

.mode-tabs button {
    min-height: 42px !important;

    border: 0 !important;
    border-radius: 7px !important;

    background: transparent !important;

    color: var(--muted) !important;

    font-size: 14px !important;
    font-weight: 600 !important;

    transition:
        background 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;
}

.mode-tabs button:hover {
    background: rgba(99,102,241,0.09) !important;
    color: var(--text) !important;
}

.mode-tabs button.selected {
    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.24),
            rgba(34,211,238,0.08)
        ) !important;

    color: #ffffff !important;

    box-shadow:
        inset 0 0 0 1px rgba(99,102,241,0.38),
        0 5px 20px rgba(99,102,241,0.08);
}

/* ============================================================
   MAIN HEADINGS
   ============================================================ */

.workspace-title {
    font-size: clamp(34px, 4vw, 52px) !important;
    line-height: 1.02 !important;

    font-weight: 720 !important;

    letter-spacing: -0.055em !important;

    margin-bottom: 12px !important;

    background:
        linear-gradient(
            100deg,
            #ffffff 15%,
            #dbeafe 55%,
            #a5f3fc 100%
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.workspace-subtitle {
    max-width: 720px;

    color: var(--muted) !important;

    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* ============================================================
   PANELS
   ============================================================ */

.panel {
    background:
        linear-gradient(
            145deg,
            rgba(27,41,64,0.92),
            rgba(19,30,48,0.94)
        ) !important;

    border: 1px solid var(--border) !important;

    border-radius: 11px !important;

    box-shadow:
        0 18px 45px var(--shadow),
        inset 0 1px rgba(255,255,255,0.025);
}

.panel-header {
    padding: 17px 20px !important;

    border-bottom: 1px solid rgba(42,58,82,0.85);
}

.panel-title {
    font-size: 12px !important;
    font-weight: 700 !important;

    text-transform: uppercase;
    letter-spacing: 0.13em;

    color: var(--text-soft) !important;
}

/* ============================================================
   INPUTS
   ============================================================ */

textarea,
input,
.gr-input,
.gr-text-input {
    background: rgba(11,18,32,0.88) !important;

    color: var(--text) !important;

    border: 1px solid var(--border) !important;
    border-radius: 8px !important;

    font-size: 15px !important;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease;
}

textarea {
    line-height: 1.65 !important;
    padding: 14px !important;
}

textarea:focus,
input:focus {
    border-color: rgba(99,102,241,0.85) !important;

    background: rgba(13,22,38,0.98) !important;

    box-shadow:
        0 0 0 3px rgba(99,102,241,0.11),
        0 0 30px rgba(34,211,238,0.04) !important;
}

/* ============================================================
   BUTTONS
   ============================================================ */

button {
    font-family: inherit !important;
    font-size: 14px !important;
}

button.primary {
    min-height: 46px !important;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #4f46e5
        ) !important;

    color: white !important;

    border: 1px solid rgba(129,140,248,0.7) !important;

    border-radius: 8px !important;

    font-size: 14px !important;
    font-weight: 700 !important;

    box-shadow:
        0 8px 25px rgba(79,70,229,0.23),
        inset 0 1px rgba(255,255,255,0.12);

    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease;
}

button.primary:hover {
    filter: brightness(1.1);

    transform: translateY(-1px);

    box-shadow:
        0 12px 32px rgba(79,70,229,0.3),
        0 0 20px rgba(34,211,238,0.07);
}

button.secondary {
    min-height: 42px !important;

    background: rgba(27,41,64,0.8) !important;

    color: var(--text-soft) !important;

    border: 1px solid var(--border) !important;

    border-radius: 8px !important;

    font-weight: 600 !important;
}

button.secondary:hover {
    background: var(--panel-soft) !important;
    border-color: var(--border-bright) !important;
    color: #ffffff !important;
}

/* ============================================================
   IMAGE / CREATIVE CANVAS
   ============================================================ */

.image-workspace {
    min-height: 520px;

    background:
        radial-gradient(
            circle at 50% 48%,
            rgba(99,102,241,0.13),
            transparent 23%
        ),
        radial-gradient(
            circle at 50% 48%,
            rgba(34,211,238,0.07),
            transparent 42%
        ),
        linear-gradient(
            rgba(255,255,255,0.018) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.018) 1px,
            transparent 1px
        ),
        #0c1524 !important;

    background-size:
        auto,
        auto,
        32px 32px,
        32px 32px,
        auto !important;

    border: 1px solid var(--border-bright) !important;

    border-radius: 11px !important;

    position: relative;

    overflow: hidden;

    box-shadow:
        0 25px 60px rgba(0,0,0,0.28),
        inset 0 0 70px rgba(34,211,238,0.025);
}

.image-workspace::before {
    content: "";

    position: absolute;

    width: 170px;
    height: 170px;

    left: 50%;
    top: 50%;

    transform: translate(-50%, -50%);

    border: 1px solid rgba(99,102,241,0.18);

    border-radius: 50%;

    box-shadow:
        0 0 0 28px rgba(99,102,241,0.035),
        0 0 0 58px rgba(34,211,238,0.018);

    pointer-events: none;
}

.image-workspace::after {
    content: "LOCAL INFERENCE   •   DEVICE PROCESSING";

    position: absolute;

    right: 20px;
    bottom: 16px;

    color: rgba(191,219,254,0.3);

    font-size: 9px;

    font-weight: 600;

    letter-spacing: 0.14em;

    pointer-events: none;
}

.canvas {
    background: transparent !important;
    border: 0 !important;
}

/* ============================================================
   CAPABILITY CHIPS
   ============================================================ */

.capability-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.capability {
    padding: 7px 11px;

    background: rgba(27,41,64,0.82);

    color: var(--muted);

    border: 1px solid var(--border);

    border-radius: 6px;

    font-size: 11px;

    font-weight: 600;

    letter-spacing: 0.02em;

    transition:
        border-color 0.18s ease,
        background 0.18s ease,
        color 0.18s ease;
}

.capability:hover {
    background: rgba(99,102,241,0.09);
    border-color: rgba(99,102,241,0.4);
    color: var(--text-soft);
}

.capability.active {
    color: #c7f9ff;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.12),
            rgba(34,211,238,0.08)
        );

    border-color: rgba(34,211,238,0.25);
}

/* ============================================================
   SAFETY / PRIVACY
   ============================================================ */

.safety-card,
.privacy-card {
    background:
        linear-gradient(
            145deg,
            rgba(27,41,64,0.85),
            rgba(18,29,46,0.9)
        ) !important;

    border: 1px solid var(--border) !important;

    border-radius: 8px !important;

    padding: 14px !important;

    box-shadow: inset 0 1px rgba(255,255,255,0.02);
}

.status-success {
    color: var(--success) !important;
}

.status-danger {
    color: var(--danger) !important;
}

.status-muted {
    color: var(--muted) !important;
}

/* ============================================================
   EMPTY STATE
   ============================================================ */

.empty-state {
    min-height: 380px;

    display: flex;

    align-items: center;
    justify-content: center;

    text-align: center;
}

.empty-state-core {
    width: 82px;
    height: 82px;

    margin: 0 auto 25px;

    border: 1px solid rgba(129,140,248,0.65);

    border-radius: 22px;

    display: flex;

    align-items: center;
    justify-content: center;

    color: #c7d2fe;

    font-size: 24px;
    font-weight: 750;

    background:
        radial-gradient(
            circle,
            rgba(99,102,241,0.18),
            rgba(34,211,238,0.04)
        );

    box-shadow:
        0 0 45px rgba(99,102,241,0.13),
        inset 0 0 25px rgba(34,211,238,0.05);
}

.empty-state-core::before,
.empty-state-core::after {
    content: "";

    position: absolute;

    border: 1px solid rgba(129,140,248,0.14);

    border-radius: 50%;

    pointer-events: none;
}

.empty-state-core::before {
    width: 130px;
    height: 130px;
}

.empty-state-core::after {
    width: 190px;
    height: 190px;

    border-color: rgba(34,211,238,0.07);
}

.empty-state-title {
    font-size: 25px;

    font-weight: 650;

    letter-spacing: -0.025em;
}

.empty-state-copy {
    max-width: 470px;

    margin: 10px auto 0;

    color: var(--muted) !important;

    line-height: 1.65;

    font-size: 14px;
}

/* ============================================================
   METADATA
   ============================================================ */

.metadata-bar {
    border-top: 1px solid var(--border);

    color: var(--dim) !important;

    font-size: 11px !important;

    letter-spacing: 0.045em;

    padding-top: 11px !important;
}

/* ============================================================
   FILES
   ============================================================ */

.file-preview,
.file-container {
    background: rgba(11,18,32,0.8) !important;

    border-color: var(--border) !important;

    border-radius: 8px !important;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1100px) {
    .workspace-area {
        padding: 28px 24px 36px !important;
    }

    .workspace-title {
        font-size: 38px !important;
    }
}

@media (max-width: 900px) {
    .topbar {
        height: 62px;
        padding: 0 18px !important;
    }

    .sidebar {
        border-right: 0;
        border-bottom: 1px solid var(--border);
        padding: 20px !important;
    }

    .workspace-area {
        padding: 22px 18px 30px !important;
    }

    .workspace-title {
        font-size: 32px !important;
    }

    .image-workspace {
        min-height: 420px;
    }
}

"""


# ============================================================
# UI
# ============================================================

with gr.Blocks(title="WITHIN") as app:

    # --------------------------------------------------------
    # COMPACT HEADER
    # --------------------------------------------------------

    with gr.Column(elem_classes="app-shell"):

        with gr.Row(
            elem_classes="topbar",
            equal_height=True
        ):

            with gr.Row(
                elem_classes="brand-area",
                

            ):
                gr.HTML(
                    """
                    <div class="brand">WITHIN</div>
                    <div class="brand-subtitle">
                        Privacy by Architecture. Safe by Design.
                    </div>
                    """
                )

            # ------------------------------------------------
            # TABS
            # ------------------------------------------------

            with gr.Tabs(
                elem_classes="mode-tabs"
            ):

                # ====================================================
                # T2I
                # ====================================================

                with gr.Tab("TEXT TO IMAGE"):

                    with gr.Row(elem_classes="mode-page"):

                        with gr.Row(elem_classes="workspace"):

                            # ----------------------------------------
                            # CONTROLS
                            # ----------------------------------------

                            with gr.Column(
                                elem_classes="controls",
                                scale=0
                            ):

                                gr.HTML(
                                    '<div class="section-label">PROMPT</div>'
                                )

                                prompt_t2i = gr.Textbox(
                                    placeholder=(
                                        "Describe the image you want to create..."
                                    ),
                                    lines=4,
                                    show_label=False,
                                    elem_classes="prompt-box"
                                )

                                generate_t2i_btn = gr.Button(
                                    "GENERATE",
                                    elem_classes="generate-btn"
                                )

                                with gr.Row():

                                    regenerate_t2i_btn = gr.Button(
                                        "REGENERATE",
                                        elem_classes="secondary-btn"
                                    )

                                    clear_t2i_btn = gr.Button(
                                        "CLEAR",
                                        elem_classes="secondary-btn"
                                    )

                                gr.HTML(
                                    """
                                    <div class="model-info">

                                        <div class="section-label">
                                            LOCAL MODEL
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Model
                                            </span>
                                            <span class="info-value">
                                                Stable Diffusion 1.5
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Steps
                                            </span>
                                            <span class="info-value">
                                                15
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Resolution
                                            </span>
                                            <span class="info-value">
                                                512 × 512
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Inference
                                            </span>
                                            <span class="info-value">
                                                Local / CUDA
                                            </span>
                                        </div>

                                    </div>
                                    """
                                )

                                t2i_prompt_status = gr.HTML()

                                t2i_output_status = gr.HTML()

                                t2i_privacy = gr.HTML()

                            # ----------------------------------------
                            # IMAGE AREA
                            # ----------------------------------------

                            with gr.Column(
                                elem_classes="image-workspace"
                            ):

                                t2i_output = gr.Image(
                                    label="",
                                    show_label=False,
                                    type="filepath",
                                    interactive=False,
                                    elem_classes="canvas"
                                )

                                t2i_message = gr.HTML()

                                t2i_download = gr.File(
                                    label="",
                                    show_label=False,
                                    interactive=False
                                )

                                gr.HTML(
                                    """
                                    <div class="metadata-bar">
                                        Local inference · Stable Diffusion 1.5
                                    </div>
                                    """
                                )


                # ====================================================
                # I2I
                # ====================================================

                with gr.Tab("IMAGE TO IMAGE"):

                    with gr.Row(elem_classes="mode-page"):

                        with gr.Row(elem_classes="workspace"):

                            # ----------------------------------------
                            # CONTROLS
                            # ----------------------------------------

                            with gr.Column(
                                elem_classes="controls",
                                scale=0
                            ):

                                gr.HTML(
                                    '<div class="section-label">SOURCE IMAGE</div>'
                                )

                                i2i_input = gr.Image(
                                    label="",
                                    show_label=False,
                                    type="filepath",
                                    interactive=True,
                                    elem_classes="upload-box"
                                )

                                gr.HTML(
                                    '<div class="section-label">EDIT PROMPT</div>'
                                )

                                prompt_i2i = gr.Textbox(
                                    placeholder=(
                                        "Describe how you want to transform the image..."
                                    ),
                                    lines=4,
                                    show_label=False,
                                    elem_classes="prompt-box"
                                )

                                generate_i2i_btn = gr.Button(
                                    "GENERATE",
                                    elem_classes="generate-btn"
                                )

                                with gr.Row():

                                    regenerate_i2i_btn = gr.Button(
                                        "REGENERATE",
                                        elem_classes="secondary-btn"
                                    )

                                    clear_i2i_btn = gr.Button(
                                        "CLEAR",
                                        elem_classes="secondary-btn"
                                    )

                                gr.HTML(
                                    """
                                    <div class="model-info">

                                        <div class="section-label">
                                            LOCAL MODEL
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Model
                                            </span>
                                            <span class="info-value">
                                                Stable Diffusion 1.5
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Strength
                                            </span>
                                            <span class="info-value">
                                                0.55
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Steps
                                            </span>
                                            <span class="info-value">
                                                15
                                            </span>
                                        </div>

                                        <div class="info-row">
                                            <span class="info-key">
                                                Inference
                                            </span>
                                            <span class="info-value">
                                                Local / CUDA
                                            </span>
                                        </div>

                                    </div>
                                    """
                                )

                                i2i_prompt_status = gr.HTML()

                                i2i_output_status = gr.HTML()

                                i2i_privacy = gr.HTML()

                            # ----------------------------------------
                            # IMAGE AREA
                            # ----------------------------------------

                            with gr.Column(
                                elem_classes="image-workspace"
                            ):

                                i2i_output = gr.Image(
                                    label="",
                                    show_label=False,
                                    type="filepath",
                                    interactive=False,
                                    elem_classes="canvas"
                                )

                                i2i_message = gr.HTML()

                                i2i_download = gr.File(
                                    label="",
                                    show_label=False,
                                    interactive=False
                                )

                                gr.HTML(
                                    """
                                    <div class="metadata-bar">
                                        Local inference · Stable Diffusion 1.5
                                    </div>
                                    """
                                )


            # --------------------------------------------------------
            # LOCAL STATUS
            # --------------------------------------------------------

            with gr.Row(
                elem_classes="local-area",
                

            ):
                gr.HTML(
                    """
                    <div class="local-status">
                        <span class="local-dot"></span>
                        LOCAL
                    </div>
                    """
                )


    # ============================================================
    # EVENTS
    # ============================================================

    generate_t2i_btn.click(
        fn=generate_t2i,
        inputs=[prompt_t2i],
        outputs=[
            t2i_output,
            t2i_prompt_status,
            t2i_output_status,
            t2i_privacy,
            t2i_message,
            t2i_download
        ]
    )

    regenerate_t2i_btn.click(
        fn=generate_t2i,
        inputs=[prompt_t2i],
        outputs=[
            t2i_output,
            t2i_prompt_status,
            t2i_output_status,
            t2i_privacy,
            t2i_message,
            t2i_download
        ]
    )

    clear_t2i_btn.click(
        fn=clear_t2i,
        inputs=[],
        outputs=[
            t2i_output,
            t2i_prompt_status,
            t2i_output_status,
            t2i_privacy,
            t2i_message,
            t2i_download
        ]
    )


    generate_i2i_btn.click(
        fn=generate_i2i,
        inputs=[i2i_input, prompt_i2i],
        outputs=[
            i2i_output,
            i2i_prompt_status,
            i2i_output_status,
            i2i_privacy,
            i2i_message,
            i2i_download
        ]
    )

    regenerate_i2i_btn.click(
        fn=generate_i2i,
        inputs=[i2i_input, prompt_i2i],
        outputs=[
            i2i_output,
            i2i_prompt_status,
            i2i_output_status,
            i2i_privacy,
            i2i_message,
            i2i_download
        ]
    )

    clear_i2i_btn.click(
        fn=clear_i2i,
        inputs=[],
        outputs=[
            i2i_output,
            i2i_prompt_status,
            i2i_output_status,
            i2i_privacy,
            i2i_message,
            i2i_download
        ]
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        inbrowser=True,
        show_error=True,
        css=CSS,
        theme=gr.themes.Base(
            primary_hue="neutral",
            secondary_hue="neutral",
            neutral_hue="neutral"
        )
    )


