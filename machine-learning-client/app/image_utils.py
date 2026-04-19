"""Utility helpers for image decoding."""

# pylint: disable=no-member

import base64

import cv2
import numpy as np


def decode_base64_image(image_b64):
    """Decode a base64 image, fallback to passthrough for invalid inputs."""

    if image_b64 is None:
        return None

    if image_b64 == "":
        return ""

    try:
        if "," in image_b64:
            image_b64 = image_b64.split(",", maxsplit=1)[1]

        image_bytes = base64.b64decode(image_b64)
        np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            return image_b64

        return image

    except Exception:  # pylint: disable=broad-except
        return image_b64
