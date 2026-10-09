from dataclasses import dataclass, field
from typing import List


@dataclass
class Diagnosis:
    case_id: str
    root_cause: str
    osi_layer: str
    concept: str
    confidence: float
    evidence_used: List[str] = field(default_factory=list)
    next_command: str = ""
    fix_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "root_cause": self.root_cause,
            "osi_layer": self.osi_layer,
            "concept": self.concept,
            "confidence": self.confidence,
            "evidence_used": self.evidence_used,
            "next_command": self.next_command,
            "fix_steps": self.fix_steps,
        }