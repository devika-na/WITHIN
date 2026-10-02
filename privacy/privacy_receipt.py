import hashlib
import json
from datetime import datetime
from pathlib import Path


class PrivacyReceipt:
    def __init__(self):
        self.receipts_dir = Path(__file__).resolve().parent.parent / "receipts"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        operation,
        model,
        output_path,
        safety_result
    ):
        timestamp = datetime.now().astimezone().isoformat()

        output_path = Path(output_path)

        sha256 = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha256.update(chunk)

        output_hash = sha256.hexdigest()

        receipt = {
            "within": {
                "name": "WITHIN",
                "version": "MVP"
            },
            "operation": operation,
            "model": model,
            "privacy": {
                "processing": "local",
                "cloud_ai_api": False,
                "network_required": False,
                "network_status": "offline"
            },
            "timestamp": timestamp,
            "safety": safety_result,
            "output": str(output_path),
            "output_sha256": output_hash
        }

        filename = (
            "within_receipt_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".json"
        )

        receipt_path = self.receipts_dir / filename

        with open(receipt_path, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=4)

        return str(receipt_path)
