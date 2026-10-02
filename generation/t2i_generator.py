from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline


class LocalT2IGenerator:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.model_path = base_dir / "models" / "stable-diffusion-v1-5"

        print("Loading local Stable Diffusion...")

        self.pipe = StableDiffusionPipeline.from_pretrained(
            str(self.model_path),
            torch_dtype=torch.float16
        )

        self.pipe = self.pipe.to("cuda")

        print("Local Stable Diffusion ready.")

    def generate(self, prompt, output_path):
        negative_prompt = (
            "blurry, low quality, distorted, deformed, bad anatomy, "
            "extra fingers, extra limbs, duplicate objects, poorly drawn face, "
            "text, watermark"
        )

        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=15
        ).images[0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path)

        return str(output_path)
