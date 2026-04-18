const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const faceLabel = document.getElementById("face-label");
const faceShapeLabel = document.getElementById("face-shape-label");
const confidenceLabel = document.getElementById("confidence-label");
const hairstyleList = document.getElementById("hairstyle-list");
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
    faceLabel.textContent = "--";
    faceShapeLabel.textContent = "Scanning...";
    confidenceLabel.textContent = "--";

    if (!analysisInterval) {
      analysisInterval = setInterval(captureAndAnalyzeFrame, 1500);
    }
  } catch (error) {
    faceShapeLabel.textContent = "Camera access failed";
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
  faceLabel.textContent = "--";
  faceShapeLabel.textContent = "Stopped";
  confidenceLabel.textContent = "--";
  hairstyleList.innerHTML = "<li>No recommendations yet.</li>";
}

function updateRecommendationList(recommendations) {
  if (!recommendations || recommendations.length === 0) {
    hairstyleList.innerHTML = "<li>No recommendations available.</li>";
    return;
  }

  hairstyleList.innerHTML = recommendations
    .map((style) => `<li>${style}</li>`)
    .join("");
}

function updateUiFromResult(result) {
  faceLabel.textContent = result.face_detected ? "Yes" : "No";
  faceShapeLabel.textContent = result.face_shape || "Unknown";
  confidenceLabel.textContent =
    typeof result.confidence === "number" ? result.confidence.toFixed(2) : "--";

  updateRecommendationList(result.recommended_hairstyles);
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
