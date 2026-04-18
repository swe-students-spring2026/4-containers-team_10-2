"""Simple dummy face-shape service."""

from app.label_mapper import get_hairstyle_recommendations


def detect_face_shape(_image):
    """
    Dummy implementation.

    Ignores the image and always returns a fixed result.
    """

    face_shape = "Oval"

    return {
        "face_detected": True,
        "face_shape": face_shape,
        "confidence": 0.9,
        "recommended_hairstyles": get_hairstyle_recommendations(face_shape),
        "face_box": {
            "x": 100,
            "y": 100,
            "width": 150,
            "height": 200,
        },
    }
