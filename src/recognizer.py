import cv2
import numpy as np


class EasyOCRBackend:
    def __init__(self, languages=("en",), use_gpu=False):
        import easyocr
        self.reader = easyocr.Reader(list(languages), gpu=use_gpu)

    def recognize(self, canvas_image):
        gray = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)
        results = self.reader.readtext(gray, detail=1, paragraph=False)
        if not results:
            return ""
        results.sort(key=lambda r: r[0][0][0])
        return " ".join(text for _, text, conf in results if conf >= 0.2).strip()


class TrOCRBackend:
    def __init__(self, model_name="microsoft/trocr-base-handwritten"):
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            from PIL import Image  # noqa: F401  — checked here so error is clear at startup
        except ImportError as e:
            raise ImportError(
                "TrOCR backend needs 'transformers', 'torch', and 'pillow'. "
                "Install with: pip install transformers torch pillow"
            ) from e
        self.processor = TrOCRProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.eval()

    def recognize(self, canvas_image):
        from PIL import Image
        # TrOCR expects white-background black-text; our canvas is the opposite, so invert.
        inverted = cv2.bitwise_not(canvas_image)
        rgb = cv2.cvtColor(inverted, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        pixel_values = self.processor(images=pil_image, return_tensors="pt").pixel_values
        generated_ids = self.model.generate(pixel_values, max_new_tokens=64)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text.strip()


class Recognizer:
    def __init__(self, backend="easyocr", **kwargs):
        if backend == "easyocr":
            self.backend = EasyOCRBackend(**kwargs)
        elif backend == "trocr":
            self.backend = TrOCRBackend(**kwargs)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def recognize(self, canvas_image):
        return self.backend.recognize(canvas_image)
