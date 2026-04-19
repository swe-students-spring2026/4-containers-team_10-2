const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const faceLabel = document.getElementById("face-label");
const faceShapeLabel = document.getElementById("face-shape-label");
const confidenceLabel = document.getElementById("confidence-label");
const maleHairstyleList = document.getElementById("male-hairstyle-list");
const femaleHairstyleList = document.getElementById("female-hairstyle-list");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const preferencesForm = document.getElementById("preferences-form");
const preferencesStatus = document.getElementById("preferences-status");

let mediaStream = null;
let analysisInterval = null;
let sessionId = crypto.randomUUID();

function styleCardHtml(style, faceShape) {
  const buttonText = style.favorited ? "★ Saved" : "☆ Save";
  const buttonClass = style.favorited ? "favorite-btn favorite-active" : "favorite-btn";
  const favoritedValue = style.favorited ? "true" : "false";

  return `
    <div class="style-card">
      <div class="style-card-top">
        <strong>${style.name}</strong>
        <button
          class="${buttonClass}"
          data-name="${style.name}"
          data-category="${style.category}"
          data-face-shape="${faceShape}"
          data-barber-notes="${style.barber_notes}"
          data-favorited="${favoritedValue}"
        >
          ${buttonText}
        </button>
      </div>
      <p class="style-meta">
        Length: ${style.lengths.join(", ")} ·
        Texture: ${style.textures.join(", ")} ·
        Maintenance: ${style.maintenance}
      </p>
      <p class="style-notes">${style.barber_notes}</p>
    </div>
  `;
}

function renderRecommendationGroup(element, styles, faceShape) {
  if (!styles || styles.length === 0) {
    element.innerHTML = `<p class="muted-copy">No recommendations available.</p>`;
    return;
  }

  element.innerHTML = styles.map((style) => styleCardHtml(style, faceShape)).join("");
}

function updateUiFromResult(result) {
  faceLabel.textContent = result.face_detected ? "Yes" : "No";
  faceShapeLabel.textContent = result.face_shape || "Unknown";
  confidenceLabel.textContent =
    typeof result.confidence === "number" ? result.confidence.toFixed(2) : "--";

  const recommendations = result.recommended_hairstyles || {};
  renderRecommendationGroup(maleHairstyleList, recommendations.male || [], result.face_shape || "Unknown");
  renderRecommendationGroup(femaleHairstyleList, recommendations.female || [], result.face_shape || "Unknown");
}

async function savePreferences(event) {
  event.preventDefault();

  const payload = {
    hair_length: document.getElementById("hair-length").value,
    hair_texture: document.getElementById("hair-texture").value,
    maintenance_level: document.getElementById("maintenance-level").value
  };

  try {
    const response = await fetch("/api/preferences", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (response.ok && result.status === "ok") {
      preferencesStatus.textContent = "Preferences saved.";
    } else {
      preferencesStatus.textContent = "Could not save preferences.";
    }
  } catch (error) {
    preferencesStatus.textContent = "Could not save preferences.";
    console.error(error);
  }
}

async function toggleFavorite(button) {
  const isFavorited = button.dataset.favorited === "true";

  const payload = {
    action: isFavorited ? "remove" : "add",
    name: button.dataset.name,
    category: button.dataset.category,
    face_shape: button.dataset.faceShape,
    barber_notes: button.dataset.barberNotes
  };

  try {
    const response = await fetch("/api/favorites", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok || result.status !== "ok") {
      return;
    }

    if (isFavorited) {
      button.dataset.favorited = "false";
      button.textContent = "☆ Save";
      button.classList.remove("favorite-active");
    } else {
      button.dataset.favorited = "true";
      button.textContent = "★ Saved";
      button.classList.add("favorite-active");
    }
  } catch (error) {
    console.error(error);
  }
}

document.addEventListener("click", (event) => {
  if (event.target.classList.contains("favorite-btn")) {
    toggleFavorite(event.target);
  }
});

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
    maleHairstyleList.innerHTML = `<p class="muted-copy">No recommendations yet.</p>`;
    femaleHairstyleList.innerHTML = `<p class="muted-copy">No recommendations yet.</p>`;

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
  maleHairstyleList.innerHTML = `<p class="muted-copy">No recommendations yet.</p>`;
  femaleHairstyleList.innerHTML = `<p class="muted-copy">No recommendations yet.</p>`;
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

if (preferencesForm) {
  preferencesForm.addEventListener("submit", savePreferences);
}
