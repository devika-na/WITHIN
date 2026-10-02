from pathlib import Path

from PIL import Image
from transformers import CLIPImageProcessor
from diffusers.pipelines.stable_diffusion.safety_checker import (
    StableDiffusionSafetyChecker,
)


class LocalSafetyChecker:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent

        self.model_path = base_dir / "models" / "safety-checker"
        self.processor_path = (
            base_dir
            / "models"
            / "stable-diffusion-v1-5"
            / "feature_extractor"
        )

        print("Loading local safety checker...")

        self.processor = CLIPImageProcessor.from_pretrained(
            str(self.processor_path)
        )

        self.checker = StableDiffusionSafetyChecker.from_pretrained(
            str(self.model_path)
        )

        print("Local safety checker ready.")

    def check_image(self, image_path):
        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        _, has_nsfw_concept = self.checker(
            clip_input=inputs["pixel_values"],
            images=[image],
        )

        flagged = bool(has_nsfw_concept[0])

        return {
            "safe": not flagged,
            "nsfw_detected": flagged,
        }