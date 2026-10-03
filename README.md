# WITHIN

Privacy by Architecture. Safe by Design.

WITHIN is a local-first image generation and editing system designed to keep AI image processing on the user's device.

It supports Text-to-Image (T2I) and Image-to-Image (I2I) workflows using Stable Diffusion v1.5 locally, with local safety checks before and after generation and a local Privacy Receipt for successful operations.

---

Core Idea

WITHIN treats privacy and safety as part of the application architecture rather than as an external service.

The processing pipeline is:

INPUT
  ↓
LOCAL SAFETY
  ↓
LOCAL AI
  ↓
OUTPUT SAFETY
  ↓
LOCAL STORAGE
  ↓
PRIVACY RECEIPT

The application does not use a cloud AI API for image generation or editing.

---

Features

Text-to-Image

Generate images from text prompts using Stable Diffusion v1.5 running locally.

The prompt is checked by the local safety layer before generation begins.

Image-to-Image

Transform an uploaded image using a local Stable Diffusion v1.5 pipeline.

The input image and transformation prompt are checked locally before inference.

Local Prompt Safety

Prompts are checked before image generation or editing.

WITHIN uses a local instruction-following safety evaluator based on Qwen2.5-0.5B-Instruct. The model reads the central "INSTRUCTION.md" policy at runtime and classifies prompts as:

- "ALLOW"
- "RESTRICT"
- "BLOCK"

Deterministic pattern-based rules provide a secondary enforcement layer.

Both "BLOCK" and "RESTRICT" decisions stop the generation pipeline before Stable Diffusion inference.

"INSTRUCTION.md" is a policy file interpreted at runtime. It is not a trained model.

Local Image Safety

Generated images are analyzed locally using the pretrained Stable Diffusion Safety Checker for NSFW concept detection.

For Image-to-Image processing, the input image is also checked before local editing.

Privacy Receipt

For successful operations, WITHIN generates a local JSON Privacy Receipt containing information such as:

- Operation type
- Model used
- Processing mode
- Network requirement
- Network status
- Timestamp
- Prompt safety result
- Input safety result
- Output safety result
- SHA-256 hash of the output

The SHA-256 value acts as a cryptographic fingerprint of the generated output file.

Offline Operation

WITHIN has been tested with network connectivity disabled.

After the required models and dependencies are available locally, runtime inference does not require a cloud AI service.

---

Architecture

Text-to-Image

User Prompt
    ↓
Local Prompt Safety
    ↓
ALLOW?
    ↓
Stable Diffusion v1.5
    ↓
Local Output Safety
    ↓
Safe Output
    ↓
Local Storage
    ↓
Privacy Receipt

Image-to-Image

Input Image + Prompt
        ↓
Local Input Image Safety
        ↓
Local Prompt Safety
        ↓
ALLOW?
        ↓
Stable Diffusion v1.5 I2I
        ↓
Local Output Safety
        ↓
Safe Output
        ↓
Local Storage
        ↓
Privacy Receipt

---

Technology Stack

- Python 3.11
- PyTorch
- Hugging Face Diffusers
- Hugging Face Transformers
- Stable Diffusion v1.5
- Qwen2.5-0.5B-Instruct
- Stable Diffusion Safety Checker
- Pillow
- Gradio
- CUDA / NVIDIA GPU

Gradio provides the local web-based interface. The AI inference and safety processing run locally.

---

Local Models

The models are stored locally and are not committed to the Git repository because of their size.

Stable Diffusion

models/
└── stable-diffusion-v1-5/

Used for local Text-to-Image and Image-to-Image generation.

Qwen2.5-0.5B-Instruct

models/
└── qwen2.5-0.5b-instruct/

Used locally to interpret the "INSTRUCTION.md" safety policy.

The Qwen model is loaded with local files only at runtime.

---

VRAM Management

WITHIN is designed to run on a laptop GPU with limited VRAM.

The current development hardware includes:

- NVIDIA RTX 3050 Laptop GPU
- 4 GB VRAM
- 16 GB RAM

The application uses lazy pipeline loading.

Only the required Stable Diffusion pipeline is loaded at a time:

T2I selected
    ↓
Load T2I pipeline

I2I selected
    ↓
Unload T2I
    ↓
Load I2I pipeline

This helps manage GPU memory when switching between Text-to-Image and Image-to-Image workflows.

---

Safety Flow

WITHIN uses multiple safety layers.

Prompt
  ↓
Deterministic Safety Rules
  ↓
Local Instruction-Based Safety Evaluator
  ↓
ALLOW / RESTRICT / BLOCK
  ↓
Generation only if allowed

After generation:

Generated Image
      ↓
Local Safety Checker
      ↓
PASS / FAIL
      ↓
Local Storage

The system does not claim that automated safety detection is perfect. The safety layers are designed as multiple local checks before and after generation.

---

Privacy Receipt

A successful operation produces a local JSON record.

Example fields include:

{
  "operation": "Image-to-Image",
  "model": "stable-diffusion-v1-5/stable-diffusion-v1-5",
  "privacy": {
    "processing": "local",
    "cloud_ai_api": false,
    "network_required": false
  },
  "timestamp": "...",
  "safety": {
    "prompt": {},
    "input": {},
    "output": {}
  },
  "output": "...",
  "output_sha256": "..."
}

The receipt is an application-level record of the operation. It is not an independent packet-level network monitor.

---

Testing

The current implementation has been tested for:

- Local Stable Diffusion Text-to-Image generation
- Local Stable Diffusion Image-to-Image generation
- Local prompt safety
- "ALLOW" prompt handling
- "RESTRICT" prompt blocking
- "BLOCK" prompt blocking
- Local input image safety
- Local output image safety
- Privacy Receipt generation
- SHA-256 output hashing
- CUDA GPU inference
- Offline runtime workflow

Example safety behavior:

Safe prompt
    → ALLOW
    → Generation proceeds

Restricted prompt
    → RESTRICT
    → Generation stops

Blocked prompt
    → BLOCK
    → Generation stops

---

Running WITHIN

Create and activate the Python virtual environment, install the required dependencies and ensure the required models are available locally.

Then run:

python app.py

The local interface is available at:

http://127.0.0.1:7861

---

Project Structure

WITHIN/
│
├── app.py
├── INSTRUCTION.md
├── README.md
│
├── safety/
│   ├── instruction_safety.py
│   └── prompt_safety.py
│
├── within/
│   ├── t2i_pipeline.py
│   └── i2i_pipeline.py
│
├── models/
│   ├── stable-diffusion-v1-5/
│   └── qwen2.5-0.5b-instruct/
│
├── outputs/
├── receipts/
└── requirements.txt

---

Limitations

WITHIN is an MVP and has practical limitations.

- Local diffusion inference can be slower than cloud GPU services.
- Performance depends on available GPU memory and hardware.
- Automated safety models cannot guarantee perfect detection.
- The Privacy Receipt is an application-level record and does not independently monitor network packets.
- Required model files must be available locally before fully offline runtime.

---

Hackathon

Built for the SCT Hackathon — Track 02: Build with Local AI.

WITHIN focuses on local AI inference, privacy-preserving architecture and layered local safety checks for image generation and editing.

---

Team

Built by the WITHIN team.

---

Tagline

Privacy by Architecture. Safe by Design.