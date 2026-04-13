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
              <td>${item.emotion ?? ""}</td>
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
  
  setInterval(refreshDashboardTable, 5000);