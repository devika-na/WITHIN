import re
from pathlib import Path

from safety.instruction_safety import InstructionSafetyChecker


class PromptSafetyChecker:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.policy_path = base_dir / "INSTRUCTION.md"

        if not self.policy_path.exists():
            raise FileNotFoundError(
                f"WITHIN safety policy not found: {self.policy_path}"
            )

        self.instruction_checker = InstructionSafetyChecker()

        self.block_patterns = {
            "sexual content": [
                r"\bexplicit sexual\b",
                r"\bsex scene\b",
                r"\bsexual act\b",
                r"\bnude sex\b",
                r"\bexplicit nudity\b",
            ],
            "sexual content involving minors": [
                r"\bchild.*sexual\b",
                r"\bminor.*sexual\b",
                r"\bunderage.*sexual\b",
            ],
            "self-harm": [
                r"\bself[- ]harm\b",
                r"\bself[- ]harming\b",
                r"\bself[- ]harmed\b",
                r"\bsuicide\b",
                r"\bkill myself\b",
                r"\bself[- ]injury\b",
                r"\bhurting themselves\b",
                r"\bhurt themselves\b",
                r"\bharm themselves\b",
                r"\bharming themselves\b",
            ],
            "violent wrongdoing": [
                r"\bkilling someone\b",
                r"\bkill someone\b",
                r"\bmurder someone\b",
                r"\bmurder\b",
                r"\bassassinate\b",
                r"\bstab someone\b",
                r"\bshoot someone\b",
            ],
            "graphic violence": [
                r"\bgraphic violence\b",
                r"\bsevere injuries\b",
                r"\bsevere injury\b",
                r"\bbloody\b",
                r"\bblood\b.*\bwound\b",
                r"\bwound\b.*\bblood\b",
                r"\bblood\b.*\bviolence\b",
                r"\bviolence\b.*\bblood\b",
                r"\bblood\b.*\bviolent\b",
                r"\bviolent\b.*\bblood\b",
                r"\bblood\b.*\bcrash\b",
                r"\bcrash\b.*\bblood\b",
                r"\bbloody\b.*\bcrash\b",
                r"\bcrash\b.*\bbloody\b",
                r"\bgruesome\b",
                r"\bgory\b",
                r"\bdismemberment\b",
                r"\bdecapitation\b",
            ],
            "illegal activity": [
                r"\bhow to make.*bomb\b",
                r"\bhow to make.*explosive\b",
                r"\bdrug manufacturing\b",
            ],
        
            "non-consensual intimate content": [
                r"\bnon[- ]consensual.*intimate\b",
                r"\bnon[- ]consensual.*sexual\b",
            ],
        }

        self.restrict_patterns = {
            "non-graphic violence": [
                r"\bbattle scene\b",
                r"\bfighting\b",
                r"\bfight scene\b",
                r"\bcombat\b",
                r"\bsoldier.*explosion\b",
                r"\bsuperhero.*villain\b",
                r"\bviolent\b",
                r"\bviolence\b",
            ],
            "deceptive impersonation": [
                r"\bdeepfake\b",
                r"\bimpersonate\b",
                r"\bfake.*celebrity\b",
            ],
            }

    def check(self, prompt):
        normalized = " ".join(prompt.lower().split())

        # Deterministic rules provide a secondary enforcement layer.
        for category, patterns in self.block_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    return {
                        "decision": "BLOCK",
                        "category": category,
                        "reason": "Blocked by deterministic safety enforcement",
                        "policy": str(self.policy_path),
                        "evaluator": "local-policy-rules",
                    }

        # Primary instruction-based local AI evaluation.
        ai_result = self.instruction_checker.check(prompt)
        decision = ai_result["decision"]

        if decision == "BLOCK":
            return {
                "decision": "BLOCK",
                "category": "instruction-policy",
                "reason": "Blocked by local instruction-based safety evaluator",
                "policy": str(self.policy_path),
                "evaluator": "local-qwen-instruction-policy",
                "raw_response": ai_result["raw_response"],
            }

        if decision == "RESTRICT":
            return {
                "decision": "RESTRICT",
                "category": "instruction-policy",
                "reason": "Restricted by local instruction-based safety evaluator",
                "policy": str(self.policy_path),
                "evaluator": "local-qwen-instruction-policy",
                "raw_response": ai_result["raw_response"],
            }

        # Secondary deterministic restriction check.
        for category, patterns in self.restrict_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    return {
                        "decision": "RESTRICT",
                        "category": category,
                        "reason": "Restricted by deterministic safety enforcement",
                        "policy": str(self.policy_path),
                        "evaluator": "local-policy-rules",
                    }

        return {
            "decision": "ALLOW",
            "category": None,
            "reason": "Allowed by local instruction-based safety evaluator",
            "policy": str(self.policy_path),
            "evaluator": "local-qwen-instruction-policy",
            "raw_response": ai_result["raw_response"],
        }
