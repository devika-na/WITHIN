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
        detail = f"{category or 'Sensitive content'} Ã‚| {reason}"
    else:
        label = "BLOCK"
        detail = f"{category or 'High-risk content'} Ã‚| {reason}"

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
            f"Generated locally Ã‚| {time_text}",
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
            f"Edited locally Ã‚| {time_text}",
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
    return None, "", "", "", None

def clear_i2i():
    return None, "", "", "", None


# ============================================================
# CSS
# ============================================================


# ============================================================
# WITHIN â€” AIR-GAPPED VAULT UI
# ============================================================

VAULT_CSS = r"""
:root {
    --obsidian: #090B0E;
    --slate: #11161D;
    --steel: #1A222D;
    --void: #0B0D11;
    --wire: #263342;
    --amber: #F59E0B;
    --amber-hover: #D97706;
    --teal: #06B6D4;
    --green: #10B981;
    --red: #EF4444;
    --text: #E5E7EB;
    --muted: #7F8A99;
    --dim: #566170;
}

* {
    box-sizing: border-box;
}

body,
.gradio-container {
    background: var(--obsidian) !important;
    color: var(--text) !important;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.gradio-container {
    max-width: 1600px !important;
    margin: auto !important;
    padding: 0 !important;
}

/* ---------- TOP DIAGNOSTIC BAR ---------- */

.vault-topbar {
    min-height: 58px;
    background: #0D1116;
    border-bottom: 1px solid var(--wire);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 22px;
    gap: 18px;
}

.vault-brand {
    display: flex;
    align-items: center;
    gap: 11px;
    min-width: 245px;
}

.vault-mark {
    width: 28px;
    height: 28px;
    border: 1px solid var(--teal);
    background: rgba(6,182,212,.06);
    display: grid;
    place-items: center;
    color: var(--teal);
    font-family: monospace;
    font-size: 13px;
    box-shadow: 0 0 16px rgba(6,182,212,.10);
}

.vault-brand-name {
    font-size: 15px;
    font-weight: 750;
    letter-spacing: .16em;
}

.vault-version {
    color: var(--muted);
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 10px;
    letter-spacing: .06em;
}

.vault-diagnostics {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    flex: 1;
    flex-wrap: wrap;
}

.diag {
    border: 1px solid var(--wire);
    background: #10151B;
    padding: 7px 10px;
    color: #B9C1CB;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 10px;
    letter-spacing: .02em;
}

.diag-green {
    color: #9BE8C8;
    border-color: rgba(16,185,129,.28);
}

.diag-teal {
    color: #8DEAF8;
    border-color: rgba(6,182,212,.28);
}

.vault-gpu {
    min-width: 185px;
    text-align: right;
    color: #AAB3BE;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 10px;
}

/* ---------- WORKSPACE ---------- */

.vault-main {
    padding: 18px;
}

.workspace-tabs {
    background: transparent !important;
    border: 0 !important;
}

.workspace-tabs > .tab-nav {
    border-bottom: 1px solid var(--wire) !important;
    background: transparent !important;
    gap: 4px;
}

.workspace-tabs > .tab-nav button {
    color: var(--muted) !important;
    background: transparent !important;
    border: 0 !important;
    border-bottom: 2px solid transparent !important;
    padding: 13px 18px !important;
    font-family: "JetBrains Mono", "Fira Code", monospace !important;
    font-size: 11px !important;
    letter-spacing: .05em !important;
}

.workspace-tabs > .tab-nav button.selected {
    color: #F3F4F6 !important;
    border-bottom-color: var(--amber) !important;
}

/* ---------- PANELS ---------- */

.rack,
.viewport-panel,
.ledger-panel {
    background: var(--slate) !important;
    border: 1px solid var(--wire) !important;
    border-radius: 3px !important;
}

.rack {
    padding: 18px !important;
}

.panel-heading {
    color: #D7DCE2;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 13px;
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.panel-subheading {
    color: var(--muted);
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-top: 18px;
    margin-bottom: 7px;
}

/* ---------- INPUTS ---------- */

.vault-input textarea,
.vault-input input {
    background: var(--void) !important;
    border: 1px solid var(--wire) !important;
    border-radius: 2px !important;
    color: #E5E7EB !important;
    font-family: Inter, sans-serif !important;
    font-size: 18px !important;
}

.vault-input textarea:focus,
.vault-input input:focus {
    border-color: rgba(6,182,212,.65) !important;
    box-shadow: 0 0 0 1px rgba(6,182,212,.10) !important;
}

.vault-image-input {
    background: var(--void) !important;
    border: 1px dashed #394756 !important;
    border-radius: 2px !important;
}

/* ---------- EXECUTION BUTTON ---------- */

.execute-btn {
    width: 100% !important;
    min-height: 46px !important;
    margin-top: 18px !important;
    background: var(--amber) !important;
    color: #17100A !important;
    border: 1px solid #FBBF24 !important;
    border-radius: 2px !important;
    font-weight: 800 !important;
    font-family: "JetBrains Mono", "Fira Code", monospace !important;
    font-size: 13px !important;
    letter-spacing: .07em !important;
}

.execute-btn:hover {
    background: var(--amber-hover) !important;
}

.execute-btn:active {
    background: #B45309 !important;
}

/* ---------- VIEWPORT ---------- */

.viewport-panel {
    padding: 12px !important;
}

.pipeline {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 10px;
    overflow-x: auto;
}

.pipeline-node {
    padding: 8px 10px;
    border: 1px solid var(--wire);
    background: #0D1218;
    color: var(--muted);
    font: 9px "JetBrains Mono", monospace;
    letter-spacing: .04em;
    white-space: nowrap;
}

.pipeline-arrow {
    color: #46515F;
    font-family: monospace;
}

.pipeline-pass {
    color: #8BE5C1;
    border-color: rgba(16,185,129,.32);
    background: rgba(16,185,129,.06);
}

.pipeline-block {
    color: #FF9A9A;
    border-color: rgba(239,68,68,.45);
    background: rgba(239,68,68,.08);
}

/* ---------- IMAGE FRAME ---------- */

.image-frame {
    min-height: 490px;
    background:
        linear-gradient(rgba(38,51,66,.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(38,51,66,.12) 1px, transparent 1px),
        #090C10;
    background-size: 32px 32px;
    border: 1px dashed #344252;
    position: relative;
    overflow: hidden;
}

.image-frame:before,
.image-frame:after {
    content: "";
    position: absolute;
    pointer-events: none;
    opacity: .45;
}

.image-frame:before {
    left: 50%;
    top: 0;
    bottom: 0;
    width: 1px;
    background: #263342;
}

.image-frame:after {
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: #263342;
}

.image-frame img {
    position: relative;
    z-index: 2;
}

.idle-frame {
    min-height: 490px;
    display: grid;
    place-items: center;
    color: #475361;
    font: 10px "JetBrains Mono", monospace;
    letter-spacing: .12em;
    text-transform: uppercase;
}

/* ---------- LEDGER ---------- */

.ledger-panel {
    margin-top: 10px;
    padding: 15px !important;
}

.ledger-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #DDE3E9;
    font: 11px "JetBrains Mono", monospace;
    letter-spacing: .11em;
}

.ledger-state {
    color: var(--teal);
    font-size: 9px;
    letter-spacing: .08em;
}

.ledger-grid {
    display: grid;
    grid-template-columns: 130px 1fr;
    gap: 7px 12px;
    margin-top: 13px;
    font-family: "JetBrains Mono", monospace;
    font-size: 9px;
}

.ledger-key {
    color: #5F6B79;
}

.ledger-value {
    color: #AEB8C3;
    overflow-wrap: anywhere;
}

.ledger-note {
    margin-top: 13px;
    padding-top: 10px;
    border-top: 1px solid #202B37;
    color: #74808E;
    font: 9px "JetBrains Mono", monospace;
    line-height: 1.6;
}

.status-box {
    margin-top: 10px;
    border: 1px solid var(--wire);
    background: #0C1015;
    padding: 11px;
    font: 10px "JetBrains Mono", monospace;
    line-height: 1.55;
}

.status-box:empty {
    display: none;
}

.status-box h4,
.status-box p {
    margin: 0;
}

@media (max-width: 1050px) {
    .vault-topbar {
        flex-wrap: wrap;
        padding: 10px 14px;
    }

    .vault-diagnostics {
        order: 3;
        width: 100%;
        justify-content: flex-start;
    }

    .vault-gpu {
        min-width: auto;
    }

    .image-frame,
    .idle-frame {
        min-height: 380px;
    }
}
"""

def vault_header():
    return """
    <div class="vault-topbar">
        <div class="vault-brand">
            <div class="vault-mark">></div>
            <div>
                <div class="vault-brand-name">WITHIN</div>
                <div class="vault-version">v1.0 | LOCAL ENGINE</div>
            </div>
        </div>

        <div class="vault-diagnostics">
            <div class="diag diag-teal">> ENGINE: SD v1.5 | CUDA fp16 | 15 STEPS</div>
            <div class="diag diag-green">> SAFETY: COMPVIS NSFW FILTER | LOCAL</div>
            <div class="diag diag-teal">> LOCAL INFERENCE | OFFLINE TESTED</div>
        </div>

        <div class="vault-gpu">
            RTX 3050 | 4 GB MOBILE
        </div>
    </div>
    """


def pipeline_html(prompt_result=None, blocked=False, reason=""):
    if blocked:
        explanation = f"""
        <div style="margin-top:7px;color:#ff9a9a;font-size:9px;">
            INTERCEPTED | {reason}
        </div>
        """
        node1 = f'<div class="pipeline-node pipeline-block">1. PROMPT FILTER | BLOCKED{explanation}</div>'
        node2 = '<div class="pipeline-node">2. LOCAL SD 1.5 | SKIPPED</div>'
        node3 = '<div class="pipeline-node">3. COMPVIS SAFETY | SKIPPED</div>'
    else:
        node1 = '<div class="pipeline-node pipeline-pass">1. PROMPT FILTER | PASS</div>'
        node2 = '<div class="pipeline-node">2. LOCAL SD 1.5 | EXECUTED</div>'
        node3 = '<div class="pipeline-node pipeline-pass">3. COMPVIS SAFETY | CHECKED</div>'

    return f"""
    <div class="pipeline">
        {node1}
        <span class="pipeline-arrow">></span>
        {node2}
        <span class="pipeline-arrow">></span>
        {node3}
    </div>
    """


def idle_html(label="AWAITING LOCAL EXECUTION"):
    return f"""
    <div class="idle-frame">
        <div>
            <div style="text-align:center;font-size:18px;color:#344252;margin-bottom:8px;">+</div>
            {label}
        </div>
    </div>
    """


def ledger_shell(mode):
    operation = "Text-to-Image" if mode == "t2i" else "Image-to-Image"
    return f"""
    <div class="ledger-panel">
        <div class="ledger-title">
            <span>LOCAL EXECUTION LEDGER</span>
            <span class="ledger-state">> SELF-CONTAINED RUN</span>
        </div>
        <div class="ledger-grid">
            <div class="ledger-key">OPERATION</div>
            <div class="ledger-value">{operation}</div>
            <div class="ledger-key">TARGET DISK</div>
            <div class="ledger-value">outputs/within_{mode}_final.png</div>
            <div class="ledger-key">MODEL</div>
            <div class="ledger-value">stable-diffusion-v1-5/stable-diffusion-v1-5</div>
            <div class="ledger-key">SAFETY</div>
            <div class="ledger-value">CompVis Safety Checker | local</div>
            <div class="ledger-key">NETWORK</div>
            <div class="ledger-value">TESTED WITH NETWORK DISABLED</div>
        </div>
        <div class="ledger-note">
            Local inference and receipt generation were verified with network connectivity disabled.
            The Privacy Receipt records the operation, processing state, safety results and SHA-256 output digest.
        </div>
    </div>
    """


with gr.Blocks(
    title="WITHIN | Air-Gapped Vault",
    theme=gr.themes.Base(
        primary_hue="amber",
        secondary_hue="cyan",
        neutral_hue="slate"
    ),
    css=VAULT_CSS
) as app:

    gr.HTML(vault_header())

    with gr.Column(elem_classes="vault-main"):

        with gr.Tabs(elem_classes="workspace-tabs"):

            # ========================================================
            # TEXT TO IMAGE
            # ========================================================

            with gr.Tab("TEXT-TO-IMAGE"):

                with gr.Row(equal_height=False):

                    with gr.Column(scale=3, elem_classes="rack"):

                        gr.HTML("""
                        <div class="panel-heading">CONTROL RACK / GENERATION</div>
                        <div style="color:#697584;font:10px 'JetBrains Mono',monospace;line-height:1.6;">
                            LOCAL CREATIVE ENGINE<br>
                        </div>
                        """)

                        gr.HTML('<div class="panel-subheading">Prompt Input</div>')

                        t2i_prompt = gr.Textbox(
                            placeholder="Describe the image to generate locally...",
                            lines=8,
                            show_label=False,
                            elem_classes="vault-input"
                        )

                        t2i_run = gr.Button(
                            "INITIALIZE LOCAL GENERATION",
                            variant="primary",
                            elem_classes="execute-btn"
                        )
                        t2i_clear = gr.Button(
                            "CLEAR / RESET",
                            variant="secondary"
                        )

                        gr.HTML("""
                        <div style="
                            margin-top:16px;
                            padding:10px;
                            border:1px solid #263342;
                            background:#0C1015;
                            color:#64707E;
                            font:9px 'JetBrains Mono',monospace;
                            line-height:1.65;
                        ">
                            MODEL LOAD: LOCAL<br>
                            NETWORK: NOT REQUIRED FOR INFERENCE<br>
                            SAFETY: PRE + POST GENERATION
                        </div>
                        """)

                    with gr.Column(scale=7, elem_classes="viewport-panel"):

                        t2i_pipeline_status = gr.HTML(
                            pipeline_html(),
                            elem_classes="pipeline-container"
                        )

                        t2i_output = gr.Image(
                            label="LOCAL OUTPUT",
                            show_label=False,
                            type="filepath",
                            interactive=False,
                            elem_classes="image-frame"
                        )

                        t2i_status = gr.HTML(
                            "",
                            elem_classes="status-box"
                        )

                        t2i_privacy = gr.HTML(
                            ledger_shell("t2i")
                        )

                        t2i_download = gr.File(
                            label="LOCAL OUTPUT FILE",
                            interactive=False
                        )

            # ========================================================
            # IMAGE TO IMAGE
            # ========================================================

            with gr.Tab("IMAGE-TO-IMAGE"):

                with gr.Row(equal_height=False):

                    with gr.Column(scale=3, elem_classes="rack"):

                        gr.HTML("""
                        <div class="panel-heading">CONTROL RACK / TRANSFORM</div>
                        <div style="color:#697584;font:10px 'JetBrains Mono',monospace;line-height:1.6;">
                            LOCAL IMAGE TRANSFORMATION<br>
                        </div>
                        """)

                        gr.HTML('<div class="panel-subheading">Source Image</div>')

                        i2i_input = gr.Image(
                            label="DROP SOURCE IMAGE",
                            type="filepath",
                            sources=["upload"],
                            elem_classes="vault-image-input"
                        )

                        gr.HTML('<div class="panel-subheading">Transformation Prompt</div>')

                        i2i_prompt = gr.Textbox(
                            placeholder="Describe how the local image should be transformed...",
                            lines=6,
                            show_label=False,
                            elem_classes="vault-input"
                        )

                        i2i_run = gr.Button(
                            "APPLY LOCAL TRANSFORM",
                            variant="primary",
                            elem_classes="execute-btn"
                        )
                        i2i_clear = gr.Button(
                            "CLEAR / RESET",
                            variant="secondary"
                        )

                    with gr.Column(scale=7, elem_classes="viewport-panel"):

                        i2i_pipeline_status = gr.HTML(
                            pipeline_html(),
                            elem_classes="pipeline-container"
                        )

                        i2i_output = gr.Image(
                            label="TRANSFORMED OUTPUT",
                            show_label=False,
                            type="filepath",
                            interactive=False,
                            elem_classes="image-frame"
                        )

                        i2i_status = gr.HTML(
                            "",
                            elem_classes="status-box"
                        )

                        i2i_privacy = gr.HTML(
                            ledger_shell("i2i")
                        )

                        i2i_download = gr.File(
                            label="LOCAL OUTPUT FILE",
                            interactive=False
                        )

    # ============================================================
    # EVENTS
    # ============================================================

    def run_t2i_ui(prompt):
        result = generate_t2i(prompt)

        output, prompt_html, safety_html, privacy_html_value, status, download = result

        if "blocked" in status.lower() or "unsafe" in status.lower():
            reason = status.replace("Generation blocked:", "").strip()
            pipeline = pipeline_html(blocked=True, reason=reason)
        else:
            pipeline = pipeline_html()

        combined_status = f"""
        <div>
            {prompt_html}
            {safety_html}
            <div style="margin-top:8px;color:#9AA5B1;">{status}</div>
        </div>
        """

        return (
            output,
            pipeline,
            combined_status,
            privacy_html_value or ledger_shell("t2i"),
            download
        )

    def run_i2i_ui(image, prompt):
        result = generate_i2i(image, prompt)

        output, prompt_html, safety_html, privacy_html_value, status, download = result

        if "blocked" in status.lower() or "unsafe" in status.lower():
            reason = status.replace("Generation blocked:", "").strip()
            pipeline = pipeline_html(blocked=True, reason=reason)
        else:
            pipeline = pipeline_html()

        combined_status = f"""
        <div>
            {prompt_html}
            {safety_html}
            <div style="margin-top:8px;color:#9AA5B1;">{status}</div>
        </div>
        """

        return (
            output,
            pipeline,
            combined_status,
            privacy_html_value or ledger_shell("i2i"),
            download
        )

    t2i_run.click(
        fn=run_t2i_ui,
        inputs=[t2i_prompt],
        outputs=[
            t2i_output,
            t2i_pipeline_status,
            t2i_status,
            t2i_privacy,
            t2i_download
        ],
        show_progress="full"
    )

    i2i_run.click(
        fn=run_i2i_ui,
        inputs=[i2i_input, i2i_prompt],
        outputs=[
            i2i_output,
            i2i_pipeline_status,
            i2i_status,
            i2i_privacy,
            i2i_download
        ],
        show_progress="full"
    )

    t2i_clear.click(
        fn=clear_t2i,
        outputs=[
            t2i_output,
            t2i_status,
            t2i_pipeline_status,
            t2i_privacy,
            t2i_download
        ]
    )

    i2i_clear.click(
        fn=clear_i2i,
        outputs=[
            i2i_output,
            i2i_status,
            i2i_pipeline_status,
            i2i_privacy,
            i2i_download
        ]
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    print("")
    print("=" * 62)
    print("WITHIN â€” AIR-GAPPED VAULT")
    print("Privacy by Architecture. Safe by Design.")
    print("=" * 62)
    print("Local inference: READY")
    print("Safety checker: LOCAL")
    print("Network dependency: NOT REQUIRED FOR INFERENCE")
    print("UI: http://127.0.0.1:7861")
    print("=" * 62)

    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        inbrowser=True
    )
















