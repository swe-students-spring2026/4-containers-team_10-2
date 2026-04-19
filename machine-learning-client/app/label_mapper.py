"""Map face shapes to hairstyle recommendations."""

FACE_SHAPE_RECOMMENDATIONS = {
    "Oval": {
        "male": [
            {
                "name": "Textured quiff",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Short tapered sides with textured volume on top.",
            },
            {
                "name": "Classic side part",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Keep clean side part with moderate top length.",
            },
            {
                "name": "Pompadour",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "high",
                "barber_notes": "Leave strong volume on top with shorter sides.",
            },
        ],
        "female": [
            {
                "name": "Long soft layers",
                "lengths": ["medium", "long"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Soft face-framing layers with movement.",
            },
            {
                "name": "Center-part waves",
                "lengths": ["medium", "long"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Keep soft waves and balanced center part.",
            },
            {
                "name": "Shoulder-length lob",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Blunt-to-soft lob around the shoulders.",
            },
        ],
    },
    "Round": {
        "male": [
            {
                "name": "Pompadour",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "high",
                "barber_notes": "Add height on top and keep sides tight.",
            },
            {
                "name": "Angular fringe",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Use sharp fringe angles to add definition.",
            },
            {
                "name": "High fade with volume",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Keep high fade and fuller top for height.",
            },
        ],
        "female": [
            {
                "name": "Long layered cut",
                "lengths": ["long"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Long layers to visually lengthen the face.",
            },
            {
                "name": "Side-part waves",
                "lengths": ["medium", "long"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Deep side part with loose waves.",
            },
            {
                "name": "Voluminous lob",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Lob with crown lift and side volume.",
            },
        ],
    },
    "Square": {
        "male": [
            {
                "name": "Textured crop",
                "lengths": ["short"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Short crop with texture to soften edges.",
            },
            {
                "name": "Soft side part",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Use a side part with softer lines.",
            },
            {
                "name": "Medium messy top",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Leave more texture and looseness up top.",
            },
        ],
        "female": [
            {
                "name": "Soft layered bob",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Soft layers around jaw and cheekbone area.",
            },
            {
                "name": "Long curls with side part",
                "lengths": ["long"],
                "textures": ["curly", "coily"],
                "maintenance": "medium",
                "barber_notes": "Use curls and side part to soften angles.",
            },
            {
                "name": "Wispy shoulder-length cut",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Keep ends wispy and avoid blunt heaviness.",
            },
        ],
    },
    "Heart": {
        "male": [
            {
                "name": "Side-swept fringe",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Keep fringe angled and soft through the front.",
            },
            {
                "name": "Textured fringe",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Use fringe to balance a wider forehead.",
            },
            {
                "name": "Medium layered cut",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Layer around the sides for balance.",
            },
        ],
        "female": [
            {
                "name": "Chin-length bob",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Add fullness closer to chin and jaw.",
            },
            {
                "name": "Side-part waves",
                "lengths": ["medium", "long"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Soft side part and waves for balance.",
            },
            {
                "name": "Long layered cut with curtain bangs",
                "lengths": ["long"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Curtain bangs soften forehead width.",
            },
        ],
    },
    "Triangle": {
        "male": [
            {
                "name": "Side part with volume",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Keep more fullness above the temples.",
            },
            {
                "name": "Textured fringe",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Fringe helps balance a stronger jaw.",
            },
            {
                "name": "Medium-length layered style",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Keep volume on top and softer sides.",
            },
        ],
        "female": [
            {
                "name": "Layered lob",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Lift around crown and soften lower face.",
            },
            {
                "name": "Shoulder-length waves",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Add width around cheekbone level.",
            },
            {
                "name": "Volume-at-crown cut",
                "lengths": ["medium", "long"],
                "textures": ["straight", "wavy"],
                "maintenance": "high",
                "barber_notes": "Increase volume near top for balance.",
            },
        ],
    },
    "Diamond": {
        "male": [
            {
                "name": "Textured top with fringe",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Keep top textured and fringe soft.",
            },
            {
                "name": "Side part",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Classic side part with some crown volume.",
            },
            {
                "name": "Messy medium cut",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Use natural texture and avoid too-tight sides.",
            },
        ],
        "female": [
            {
                "name": "Textured bob",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Textured bob that softens cheek width.",
            },
            {
                "name": "Long layers with side part",
                "lengths": ["long"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Long layers and side part for balance.",
            },
            {
                "name": "Shoulder-length soft waves",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Soft waves reduce sharpness through the cheeks.",
            },
        ],
    },
    "Oblong": {
        "male": [
            {
                "name": "Classic crop",
                "lengths": ["short"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Keep a lower-profile top and fuller sides.",
            },
            {
                "name": "Medium textured cut",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Avoid too much vertical height.",
            },
            {
                "name": "Side part with low volume",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Keep neat structure without added height.",
            },
        ],
        "female": [
            {
                "name": "Shoulder-length layered cut",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "medium",
                "barber_notes": "Add side width and soft layering.",
            },
            {
                "name": "Soft waves with bangs",
                "lengths": ["medium", "long"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Use bangs to shorten perceived face length.",
            },
            {
                "name": "Collarbone lob",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Balanced length with fullness at the sides.",
            },
        ],
    },
    "Unknown": {
        "male": [
            {
                "name": "Classic side part",
                "lengths": ["short", "medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Versatile, clean cut with balanced proportions.",
            },
            {
                "name": "Textured crop",
                "lengths": ["short"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "low",
                "barber_notes": "Simple textured crop that suits many shapes.",
            },
            {
                "name": "Medium layered cut",
                "lengths": ["medium"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Soft layering that works for many faces.",
            },
        ],
        "female": [
            {
                "name": "Long soft layers",
                "lengths": ["medium", "long"],
                "textures": ["straight", "wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Universally flattering soft layers.",
            },
            {
                "name": "Shoulder-length lob",
                "lengths": ["medium"],
                "textures": ["straight", "wavy"],
                "maintenance": "low",
                "barber_notes": "Flexible mid-length cut with clean shape.",
            },
            {
                "name": "Side-part waves",
                "lengths": ["medium", "long"],
                "textures": ["wavy", "curly"],
                "maintenance": "medium",
                "barber_notes": "Side-part waves suit many face shapes.",
            },
        ],
    },
}


def normalize_face_shape(raw_shape):
    """Normalize a face-shape label."""
    supported_shapes = {
        "Oval",
        "Round",
        "Square",
        "Heart",
        "Triangle",
        "Diamond",
        "Oblong",
    }
    if raw_shape in supported_shapes:
        return raw_shape
    return "Unknown"


def get_hairstyle_recommendations(face_shape):
    """Return recommendations for a face shape."""
    normalized_shape = normalize_face_shape(face_shape)
    return FACE_SHAPE_RECOMMENDATIONS.get(
        normalized_shape,
        FACE_SHAPE_RECOMMENDATIONS["Unknown"],
    )
