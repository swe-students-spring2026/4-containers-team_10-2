import sys
import types
import pytest
import os

# FULL mediapipe mock (complete)
mp = types.ModuleType("mediapipe")

solutions = types.ModuleType("solutions")
face_mesh = types.ModuleType("face_mesh")

# 🔥 add FaceMesh class (this fixes your current error)
class FakeFaceMesh:
    def __init__(self, *args, **kwargs):
        pass

    def process(self, image):
        return None

face_mesh.FaceMesh = FakeFaceMesh
solutions.face_mesh = face_mesh
mp.solutions = solutions

sys.modules["mediapipe"] = mp
sys.modules["mediapipe.solutions"] = solutions
sys.modules["mediapipe.solutions.face_mesh"] = face_mesh

# mock cv2
sys.modules["cv2"] = types.ModuleType("cv2")

# path fix
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()