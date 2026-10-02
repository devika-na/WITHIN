from pathlib import Path

from generation.t2i_generator import LocalT2IGenerator
from safety.safety_checker import LocalSafetyChecker
from safety.prompt_safety import PromptSafetyChecker
from privacy.privacy_receipt import PrivacyReceipt


class WITHINT2IPipeline:
    def __init__(self):
        print("Initializing WITHIN T2I pipeline...")

        self.generator = LocalT2IGenerator()
        self.safety = LocalSafetyChecker()
        self.prompt_safety = PromptSafetyChecker()
        self.receipt = PrivacyReceipt()

        print("WITHIN T2I pipeline ready.")

    def generate(self, prompt, output_path):
        print("Running local prompt safety check...")

        prompt_result = self.prompt_safety.check(prompt)

        if prompt_result["decision"] == "BLOCK":
            print("Prompt blocked before generation.")

            return {
                "status": "BLOCKED",
                "reason": prompt_result["reason"],
                "prompt_safety": prompt_result,
                "output": None,
                "safety": None,
                "privacy_receipt": None
            }

        print(
            f"Prompt safety decision: {prompt_result['decision']}"
        )

        print("Generating image locally...")

        generated_path = self.generator.generate(
            prompt,
            output_path
        )

        print("Running local output safety check...")

        safety_result = self.safety.check_image(
            generated_path
        )

        if not safety_result["safe"]:
            Path(generated_path).unlink(missing_ok=True)

            return {
                "status": "BLOCKED",
                "reason": "NSFW content detected",
                "prompt_safety": prompt_result,
                "output": None,
                "safety": safety_result,
                "privacy_receipt": None
            }

        receipt_path = self.receipt.create(
            operation="Text-to-Image",
            model="stable-diffusion-v1-5/stable-diffusion-v1-5",
            output_path=generated_path,
            safety_result={
                "prompt": prompt_result,
                "image": safety_result
            }
        )

        return {
            "status": "ALLOWED",
            "output": generated_path,
            "prompt_safety": prompt_result,
            "safety": safety_result,
            "privacy_receipt": receipt_path
        }
