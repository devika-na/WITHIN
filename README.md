# WITHIN

Privacy by Architecture. Safe by Design.

WITHIN is a local-first image generation and editing system designed to keep AI image processing on the user's device.

It supports Text-to-Image and Image-to-Image workflows using Stable Diffusion locally, with safety checks before and after generation. A local Privacy Receipt records the processing state, model, timestamp, and safety results for each successful operation.

---

Core Idea

Traditional AI image-generation workflows often depend on remote inference services.

WITHIN takes a local-first approach:

INPUT
  |
  v
LOCAL SAFETY
  |
  v
LOCAL AI
  |
  v
OUTPUT SAFETY
  |
  v
LOCAL STORAGE
  |
  v
PRIVACY RECEIPT

The goal is to make local processing and safety checks explicit parts of the architecture rather than treating them as optional features.

---

Features

Text-to-Image

Generate images from text prompts using Stable Diffusion running locally.

Image-to-Image

Transform an existing image using a local Stable Diffusion image-to-image pipeline.

Local Prompt Safety

Prompts are checked by the local safety layer before image generation or editing.

Restricted prompts can be blocked before the generation model is started.

Local Image Safety

Generated images are analyzed locally using the pretrained Stable Diffusion Safety Checker for NSFW concept detection.

For Image-to-Image processing, the input image is also checked before local editing.

Privacy Receipt

Each successful operation can generate a local JSON receipt containing information such as:

- Operation type
- Model used
- Local processing status
- Cloud AI API usage
- Network requirement/status
- Timestamp
- Prompt safety result
- Input safety result
- Output safety result
- Output file hash

The receipt is intended as a local record of what the pipeline reported during that operation.

Offline Operation

WITHIN's inference workflow is designed to operate locally without requiring a cloud AI API.

The local workflow has been tested with network connectivity disabled.

---

Architecture

INPUT
  |
  v
LOCAL SAFETY
  |
  | Safety Passed
  v
LOCAL AI
Stable Diffusion
  |
  v
OUTPUT SAFETY
Local NSFW Check
  |
  v
LOCAL STORAGE
Generated Image
  |
  v
PRIVACY RECEIPT
JSON Record

---

Technology Stack

- Python
- Gradio - local user interface
- PyTorch - local GPU inference
- Hugging Face Diffusers - Stable Diffusion pipelines
- Hugging Face Transformers - pretrained model components
- Stable Diffusion v1.5 - local image generation and editing
- Stable Diffusion Safety Checker - local NSFW concept detection
- Pillow - image handling
- CUDA / NVIDIA GPU - local acceleration

---

Project Structure

WITHIN/
|
+-- app.py
+-- generation/
|   +-- i2i_generator.py
|   +-- t2i_generator.py
|
+-- within/
|   +-- t2i_pipeline.py
|   +-- i2i_pipeline.py
|
+-- safety/
|   +-- prompt_safety.py
|   +-- safety_checker.py
|
+-- privacy/
|   +-- privacy_receipt.py
|
+-- requirements.txt
+-- README.md
+-- .gitignore

Local model files and generated outputs are intentionally excluded from the repository.

---

Running WITHIN

1. Clone the repository

git clone https://github.com/devika-na/WITHIN.git
cd WITHIN

2. Create a virtual environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

### 4. Add the required local model

WITHIN uses the Stable Diffusion v1.5 model locally.

Obtain the Diffusers-format model from the official Hugging Face model repository:

https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5

Place the complete Diffusers model directory at:

models/
  stable-diffusion-v1-5/

The local model directory should contain the model components and configuration required by the Diffusers pipeline.

The model files are intentionally excluded from Git because of their large size.

### 5. Run

```powershell
python app.py


The Gradio interface will start locally.

---

Local Model

WITHIN currently uses:

stable-diffusion-v1-5/stable-diffusion-v1-5

for local image generation and editing.

The Stable Diffusion Safety Checker is also loaded locally for image safety analysis.

---

Safety Flow

Text-to-Image

Prompt
  |
  v
Prompt Safety
  |
  +---- BLOCK ----> Stop
  |
  v
Local Stable Diffusion
  |
  v
Output Safety
  |
  v
Safe -> Save Output
  |
  v
Privacy Receipt

Image-to-Image

Input Image + Prompt
        |
        v
  Prompt Safety
        |
        v
  Input Image Safety
        |
        v
 Local Stable Diffusion
        |
        v
   Output Safety
        |
        v
    Local Output
        |
        v
   Privacy Receipt

---

Privacy Receipt

A successful operation produces a JSON receipt locally.

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
  "output_sha256": "..."
}

The SHA-256 value provides a content hash for the recorded output file.

---

Testing

The current MVP has been tested for:

- Local Text-to-Image generation
- Local Image-to-Image editing
- Prompt safety blocking
- Prompt safety allowing safe prompts
- Local output safety checking
- Privacy Receipt generation
- Network-disabled local inference

---

Limitations

WITHIN is an MVP.

Current limitations include:

- Local Stable Diffusion inference can take significant time on consumer laptop hardware.
- Generation quality depends on the selected model and available GPU resources.
- The current system is not intended to provide real-time generation.
- Local model weights must be downloaded and stored separately.
- The Privacy Receipt records the application's reported processing state; it is not an independent proof of network isolation.
- Safety detection is model-based and should not be treated as perfect or comprehensive moderation.

---

Hackathon

 Track 02: Build with Local AI.

Team

Devika N A
Archana P U

Tagline

«Privacy by Architecture. Safe by Design.»
