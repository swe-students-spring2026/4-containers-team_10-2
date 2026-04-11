import requests

def submit_frame_for_analysis(ml_client_url, image_b64, session_id):
    response = requests.post(
        f"{ml_client_url}/analyze",
        json={
            "session_id": session_id,
            "image_b64": image_b64,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()