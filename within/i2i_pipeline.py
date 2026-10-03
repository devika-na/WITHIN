from pathlib import Path

from generation.i2i_generator import LocalI2IGenerator
from safety.safety_checker import LocalSafetyChecker
from safety.prompt_safety import PromptSafetyChecker
from privacy.privacy_receipt import PrivacyReceipt


class WITHINI2IPipeline:
    def __init__(self):
        print("Initializing WITHIN I2I pipeline...")

        self.generator = LocalI2IGenerator()
        self.safety = LocalSafetyChecker()
        self.prompt_safety = PromptSafetyChecker()
        self.receipt = PrivacyReceipt()

        print("WITHIN I2I pipeline ready.")

    def generate(
        self,
        prompt,
        input_path,
        output_path,
        strength=0.75,
        guidance_scale=7.5
    ):
        print("Running local prompt safety check...")

        prompt_result = self.prompt_safety.check(prompt)

        if prompt_result["decision"] in ["BLOCK", "RESTRICT"]:
            print("Prompt rejected before generation.")
            return {
                "status": "BLOCKED",
                "reason": prompt_result["reason"],
                "prompt_safety": prompt_result,
                "output": None,
                "input_safety": None,
                "output_safety": None,
                "privacy_receipt": None
            }

        print(
            f"Prompt safety decision: {prompt_result['decision']}"
        )

        print("Running local input safety check...")

        input_safety_result = self.safety.check_image(
            input_path
        )

        if not input_safety_result["safe"]:
            return {
                "status": "BLOCKED",
                "reason": "Unsafe input image detected",
                "prompt_safety": prompt_result,
                "output": None,
                "input_safety": input_safety_result,
                "output_safety": None,
                "privacy_receipt": None
            }

        print("Input image passed safety check.")

        print("Generating I2I image locally...")

        generated_path = self.generator.generate(
            prompt=prompt,
            input_path=input_path,
            output_path=output_path,
            strength=strength,
            guidance_scale=guidance_scale
        )

        print("Running local output safety check...")

        output_safety_result = self.safety.check_image(
            generated_path
        )

        if not output_safety_result["safe"]:
            Path(generated_path).unlink(missing_ok=True)

            return {
                "status": "BLOCKED",
                "reason": "Unsafe output image detected",
                "prompt_safety": prompt_result,
                "output": None,
                "input_safety": input_safety_result,
                "output_safety": output_safety_result,
                "privacy_receipt": None
            }

        receipt_path = self.receipt.create(
            operation="Image-to-Image",
            model="stable-diffusion-v1-5/stable-diffusion-v1-5",
            output_path=generated_path,
            safety_result={
                "prompt": prompt_result,
                "input": input_safety_result,
                "output": output_safety_result
            }
        )

        return {
            "status": "ALLOWED",
            "output": generated_path,
            "prompt_safety": prompt_result,
            "input_safety": input_safety_result,
            "output_safety": output_safety_result,
            "privacy_receipt": receipt_path
        }
