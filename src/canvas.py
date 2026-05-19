import math
import cv2
import numpy as np


class AirCanvas:
    def __init__(self, height, width, stroke_thickness=8, stroke_color=(255, 255, 255)):
        self.height = height
        self.width = width
        self.stroke_thickness = stroke_thickness
        self.stroke_color = stroke_color
        # Black background, white strokes — OCR likes high contrast.
        self.image = np.zeros((height, width, 3), dtype=np.uint8)
        self._last_point = None

    def add_point(self, point):
        if point is None:
            self._last_point = None
            return
        if self._last_point is not None:
            # Skip absurd jumps (hand teleporting frame-to-frame).
            if math.dist(self._last_point, point) < self.width * 0.4:
                cv2.line(
                    self.image,
                    self._last_point,
                    point,
                    self.stroke_color,
                    self.stroke_thickness,
                    cv2.LINE_AA,
                )
        self._last_point = point

    def pen_up(self):
        self._last_point = None

    def render(self, frame_bgr):
        # Overlay where the canvas has ink (any non-zero pixel).
        mask = self.image.any(axis=2)
        frame_bgr[mask] = self.image[mask]

    def get_image_for_ocr(self):
        return self.image.copy()

    def is_empty(self):
        return not self.image.any()

    def clear(self):
        self.image[:] = 0
        self._last_point = None
