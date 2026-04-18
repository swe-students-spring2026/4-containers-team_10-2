"""Helpers for mapping detected face shapes to hairstyle recommendations."""

FACE_SHAPE_RECOMMENDATIONS = {
    "Oval": [
        "Textured quiff",
        "Classic side part",
        "Layered medium cut",
    ],
    "Round": [
        "Pompadour",
        "Angular fringe",
        "High fade with volume",
    ],
    "Square": [
        "Textured crop",
        "Soft side part",
        "Layered fringe",
    ],
    "Heart": [
        "Side swept style",
        "Textured fringe",
        "Medium layered cut",
    ],
    "Oblong": [
        "Classic crop",
        "Fuller sides with less height",
        "Medium-length layered cut",
    ],
    "Diamond": [
        "Textured top with fringe",
        "Side part with medium length",
        "Messy layered cut",
    ],
    "Unknown": [
        "Classic side part",
        "Textured crop",
        "Medium layered cut",
    ],
}


def normalize_face_shape(raw_shape):
    """Normalize a raw face-shape label to supported values."""
    supported_shapes = {
        "Oval",
        "Round",
        "Square",
        "Heart",
        "Oblong",
        "Diamond",
    }
    if raw_shape in supported_shapes:
        return raw_shape
    return "Unknown"


def get_hairstyle_recommendations(face_shape):
    """Return the top hairstyle recommendations for a face shape."""
    normalized_shape = normalize_face_shape(face_shape)
    return FACE_SHAPE_RECOMMENDATIONS.get(
        normalized_shape,
        FACE_SHAPE_RECOMMENDATIONS["Unknown"],
    )
