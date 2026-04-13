const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const videoShell = document.getElementById("video-shell");
const emotionLabel = document.getElementById("emotion-label");
const confidenceLabel = document.getElementById("confidence-label");
const faceLabel = document.getElementById("face-label");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");

let mediaStream = null;
let analysisInterval = null;
let sessionId = crypto.randomUUID();

async function startCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false
    });

    video.srcObject = mediaStream;
    emotionLabel.textContent = "Camera running";
    confidenceLabel.textContent = "--";
    faceLabel.textContent = "--";

    if (!analysisInterval) {
      analysisInterval = setInterval(captureAndAnalyzeFrame, 1000);
    }
  } catch (error) {
    emotionLabel.textContent = "Camera access failed";
    faceLabel.textContent = "No";
    console.error(error);
  }
}

function stopCamera() {
  if (analysisInterval) {
    clearInterval(analysisInterval);
    analysisInterval = null;
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }

  video.srcObject = null;
  emotionLabel.textContent = "Stopped";
  confidenceLabel.textContent = "--";
  faceLabel.textContent = "--";
  videoShell.className = "video-shell neutral";
}

function updateUiFromResult(result) {
  emotionLabel.textContent = result.emotion || "unknown";
  confidenceLabel.textContent =
    typeof result.confidence === "number" ? result.confidence.toFixed(2) : "--";
  faceLabel.textContent = result.face_detected ? "Yes" : "No";

  const emotion = result.emotion || "neutral";
  videoShell.className = `video-shell ${emotion}`;
}

async function captureAndAnalyzeFrame() {
  if (!mediaStream || video.videoWidth === 0 || video.videoHeight === 0) {
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageB64 = canvas.toDataURL("image/jpeg", 0.8);

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: sessionId,
        image_b64: imageB64
      })
    });

    const result = await response.json();

    if (response.ok && result.status === "ok") {
      updateUiFromResult(result);
    } else {
      console.error("Analyze request failed:", result);
    }
  } catch (error) {
    console.error("Error sending frame:", error);
  }
}

startBtn.addEventListener("click", startCamera);
stopBtn.addEventListener("click", stopCamera);