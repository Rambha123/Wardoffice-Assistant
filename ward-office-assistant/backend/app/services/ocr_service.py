"""
OCR service placeholder. The OCR engine is not chosen yet.
Keep the OcrResult / extract_text interface stable so the rest of the
readiness pipeline doesn't change when an engine is plugged in.

Privacy: callers delete the temp file right after extract_text returns.
"""

from dataclasses import dataclass


@dataclass
class OcrResult:
    full_text: str
    line_confidences: list[float]

    @property
    def average_confidence(self) -> float:
        return sum(self.line_confidences) / len(self.line_confidences) if self.line_confidences else 0.0


def extract_text(image_path: str) -> OcrResult:
    raise NotImplementedError("No OCR engine configured yet. See ocr_service.py.")