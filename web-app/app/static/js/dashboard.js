async function refreshDashboardTable() {
  const tableBody = document.getElementById("recent-table-body");

  if (!tableBody) {
    return;
  }

  try {
    const response = await fetch("/api/history?limit=10");
    const payload = await response.json();

    if (!response.ok || payload.status !== "ok") {
      return;
    }

    const rows = payload.records
      .map((item) => {
        const confidence =
          typeof item.confidence === "number"
            ? item.confidence.toFixed(2)
            : "--";

        return `
          <tr>
            <td>${item.timestamp ?? ""}</td>
            <td>${item.face_shape ?? "Unknown"}</td>
            <td>${confidence}</td>
            <td>${item.face_detected ?? ""}</td>
          </tr>
        `;
      })
      .join("");

    tableBody.innerHTML = rows;
  } catch (error) {
    console.error("Dashboard refresh failed:", error);
  }
}

async function saveDashboardPreferences(event) {
  event.preventDefault();

  const payload = {
    hair_length: document.getElementById("dashboard-hair-length").value,
    hair_texture: document.getElementById("dashboard-hair-texture").value,
    maintenance_level: document.getElementById("dashboard-maintenance-level").value
  };

  const status = document.getElementById("dashboard-preferences-status");

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
      status.textContent = "Preferences updated.";
    } else {
      status.textContent = "Could not update preferences.";
    }
  } catch (error) {
    status.textContent = "Could not update preferences.";
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

const dashboardPreferencesForm = document.getElementById("dashboard-preferences-form");
if (dashboardPreferencesForm) {
  dashboardPreferencesForm.addEventListener("submit", saveDashboardPreferences);
}

setInterval(refreshDashboardTable, 5000);
