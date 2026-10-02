from pathlib import Path

import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline


class LocalI2IGenerator:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.model_path = base_dir / "models" / "stable-diffusion-v1-5"

        print("Loading local Stable Diffusion I2I...")

        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            str(self.model_path),
            torch_dtype=torch.float16
        )

        self.pipe = self.pipe.to("cuda")

        print("Local Stable Diffusion I2I ready.")

    def generate(
        self,
        prompt,
        input_path,
        output_path,
        strength=0.55,
        guidance_scale=7.5
    ):
        image = Image.open(input_path).convert("RGB")

        result = self.pipe(
            prompt=prompt,
            image=image,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=15
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result.images[0].save(output_path)

        return str(output_path)
