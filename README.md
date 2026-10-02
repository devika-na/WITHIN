# WITHIN



### Privacy by Architecture. Safe by Design.



WITHIN is a privacy-first local AI image generation and editing system designed to keep user prompts, input images, and generated outputs on the device.



Instead of sending image-generation requests to a cloud AI service, WITHIN runs the generation and safety pipeline locally.



## What WITHIN does



WITHIN currently supports:



\* Text-to-Image (T2I) generation

\* Image-to-Image (I2I) editing

\* Local prompt safety analysis

\* Local image safety analysis

\* Local Stable Diffusion inference

\* Local output storage

\* Privacy Receipts

\* SHA-256 hashing of generated outputs

\* Offline operation testing



## Architecture



```text

&#x20;                   WITHIN LOCAL PIPELINE



&#x20;                        User Input

&#x20;                      /            \\

&#x20;                 Prompt           Image

&#x20;                    ↓                ↓

&#x20;             Local Prompt      Local Image

&#x20;               Safety             Safety

&#x20;                    \\                /

&#x20;                     \\              /

&#x20;                      ↓            ↓

&#x20;                      Local AI

&#x20;                 Stable Diffusion

&#x20;                           ↓

&#x20;                    Output Safety

&#x20;                           ↓

&#x20;                    Local Storage

&#x20;                           ↓

&#x20;                   Privacy Receipt

```



The core principle is to treat privacy and safety as part of the architecture rather than as an additional cloud service.



## Technology Stack



### AI Generation



\* Stable Diffusion v1.5

\* Hugging Face Diffusers

\* PyTorch

\* Transformers

\* Safetensors



### Safety



\* Local rule-based prompt safety layer

\* CompVis Stable Diffusion Safety Checker

\* Local input/output safety processing



### Application



\* Python

\* Gradio

\* Pillow



### Hardware



The current MVP has been tested on a system with:



\* NVIDIA RTX 3050 Laptop GPU

\* 4 GB VRAM

\* 16 GB RAM

\* CUDA-enabled PyTorch



Hardware requirements may vary depending on the model and inference configuration.



## Text-to-Image



The T2I pipeline follows:



```text

Prompt

&#x20; ↓

Prompt Safety

&#x20; ↓

Blocked? ── Yes → Stop

&#x20; ↓ No

Local Stable Diffusion

&#x20; ↓

Output Safety

&#x20; ↓

Local Storage

&#x20; ↓

Privacy Receipt

```



The prompt is checked locally before generation.



Prompts classified as blocked are stopped before the generation model is executed.



## Image-to-Image



The I2I pipeline follows:



```text

Input Image + Prompt

&#x20;       ↓

&#x20;  Prompt Safety

&#x20;       ↓

&#x20;Input Image Safety

&#x20;       ↓

&#x20;Local Stable Diffusion I2I

&#x20;       ↓

&#x20;  Output Safety

&#x20;       ↓

&#x20;  Local Storage

&#x20;       ↓

&#x20; Privacy Receipt

```



This allows an existing image to be transformed using a local diffusion model.



## Safety Layer



WITHIN uses multiple safety stages.



### Prompt Safety



The local rule-based layer currently identifies categories including:



\* Explicit sexual content

\* Sexual content involving minors

\* Self-harm

\* Graphic violence

\* Non-consensual intimate content

\* Non-graphic violence

\* Deceptive impersonation / deepfake-related prompts

\* Certain illegal-activity prompts



The current implementation has three outcomes:



```text

ALLOW

RESTRICT

BLOCK

```



`BLOCK` stops generation.



`RESTRICT` currently allows generation while marking the prompt as sensitive.



### Image Safety



WITHIN integrates the:



```text

CompVis Stable Diffusion Safety Checker

```



locally.



In this MVP, the safety checker is specifically used for NSFW concept detection. It should not be interpreted as a complete detector for every possible unsafe or harmful image category.



## Privacy Receipt



After a successful generation, WITHIN creates a local Privacy Receipt.



The receipt records information such as:



\* Operation type

\* Model used

\* Local processing state

\* Cloud AI API usage state

\* Network status recorded by the application

\* Timestamp

\* Safety results

\* Output path

\* SHA-256 hash of the output



Example structure:



```text

receipts/

└── within\_receipt\_YYYYMMDD\_HHMMSS.json

```



The output hash provides a way to identify the exact generated file associated with the receipt.



## Offline Testing



The system has been tested with network connectivity disabled.



During the offline test:



\* Text-to-Image generation continued to work

\* Image-to-Image generation continued to work

\* Local prompt safety continued to work

\* Local image safety continued to work

\* Privacy Receipt generation continued to work



This demonstrates that the core inference and safety pipeline can operate without an active network connection.



## Models



WITHIN uses pretrained model artifacts from Hugging Face.



### Generation Model



```text

stable-diffusion-v1-5/stable-diffusion-v1-5

```



### Safety Model



```text

CompVis/stable-diffusion-safety-checker

```



The models are downloaded separately and are intentionally \*\*not stored in this Git repository\*\* because of their size.



## Project Structure



```text

WITHIN.org/

│

├── app.py

├── requirements.txt

├── .gitignore

│

├── generation/

│   ├── i2i\_generator.py

│   └── t2i\_generator.py

│

├── privacy/

│   └── privacy\_receipt.py

│

├── safety/

│   ├── prompt\_safety.py

│   └── safety\_checker.py

│

└── within/

&#x20;   ├── i2i\_pipeline.py

&#x20;   └── t2i\_pipeline.py

```



Local runtime directories such as model weights, generated outputs, receipts, and the Python virtual environment are excluded from Git.



## Installation



Create a Python virtual environment:



```bash

python -m venv .venv

```



Activate it on Windows:



```powershell

.venv\\Scripts\\Activate.ps1

```



Install the Python dependencies:



```bash

pip install -r requirements.txt

```



### PyTorch / CUDA



The current requirements file specifies the CUDA 12.8 PyTorch build used during development.



A CUDA-compatible NVIDIA GPU is recommended for local Stable Diffusion inference.



## Model Setup



The required model files must be downloaded separately into the expected local model directories.



The current application expects:



```text

models/

├── stable-diffusion-v1-5/

└── safety-checker/

```



Model weights are intentionally excluded from Git because they are several gigabytes in size.



## Running WITHIN



From the project directory:



```powershell

python app.py

```



The application runs locally and is configured to bind to:



```text

127.0.0.1:7861

```



The Gradio interface can then be accessed through the local browser.



## Limitations



WITHIN is currently an MVP.



The following claims are intentionally \*\*not\*\* made:



\* It does not guarantee complete privacy under every system configuration.

\* It does not provide packet-level proof that zero bytes were transmitted.

\* The Privacy Receipt is not a cryptographic proof of network isolation.

\* The safety system does not detect every category of harmful content.

\* The CompVis safety checker is primarily being used for NSFW concept detection.

\* `RESTRICT` prompts are currently allowed to proceed.

\* Image quality and generation speed depend on the local hardware and model configuration.

\* The current MVP has been tested primarily on NVIDIA CUDA hardware.



## Why Local AI?



Cloud AI image generation normally requires user data to be processed by a remote service.



WITHIN explores a different architecture:



```text

Cloud AI approach:



User → Internet → AI Service → Internet → User





WITHIN:



User → Local Safety → Local AI → Local Safety → Local Storage

```



The goal is not simply to make an AI image generator offline.



The goal is to make \*\*privacy a property of the system architecture\*\*.



## Project Status



Current MVP capabilities:



\* \[x] Local T2I generation

\* \[x] Local I2I generation

\* \[x] Local prompt safety

\* \[x] Local image safety

\* \[x] Output safety checking

\* \[x] Local storage

\* \[x] Privacy Receipt

\* \[x] SHA-256 output hashing

\* \[x] Offline pipeline testing

\* \[ ] Dynamic network traffic verification

\* \[ ] Cryptographically verifiable privacy attestation

\* \[ ] Broader multimodal safety coverage

\* \[ ] Cross-platform packaging



## License



Add the project's license here before public distribution.



## Team



\*\*WITHIN\*\*



Privacy by Architecture. Safe by Design.

