import cv2
import easyocr


class Recognizer:
    def __init__(self, languages=("en",), use_gpu=False):
        self.reader = easyocr.Reader(list(languages), gpu=use_gpu)

    def recognize(self, canvas_image):
        gray = cv2.cvtColor(canvas_image, cv2.COLOR_BGR2GRAY)
        results = self.reader.readtext(gray, detail=1, paragraph=False)
        if not results:
            return ""
        results.sort(key=lambda r: r[0][0][0])
        return " ".join(text for _, text, conf in results if conf >= 0.2).strip()
