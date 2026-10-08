/**
 * ClaimSense AI - Frontend Controller
 * Phase 1: Health Check & Backend Communication
 */

document.addEventListener("DOMContentLoaded", () => {
    const statusIndicator = document.getElementById("status-indicator");
    const statusBadge = document.getElementById("status-badge");
    const healthStatus = document.getElementById("health-status");
    const healthPhase = document.getElementById("health-phase");
    const healthVersion = document.getElementById("health-version");
    const healthEnv = document.getElementById("health-env");
    const healthTimestamp = document.getElementById("health-timestamp");
    const btnRefresh = document.getElementById("btn-refresh-health");

    async function checkBackendHealth() {
        statusIndicator.className = "status-indicator";
        statusBadge.textContent = "Checking backend...";
        healthStatus.textContent = "Connecting...";

        try {
            const response = await fetch("/api/health");
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}`);
            }

            const data = await response.json();

            // Update UI elements
            statusIndicator.className = "status-indicator connected";
            statusBadge.textContent = "Backend Connected";
            healthStatus.textContent = `${data.status.toUpperCase()} (HTTP 200)`;
            healthStatus.style.color = "#16a34a";
            healthPhase.textContent = data.phase || "Phase 1 - Project Foundation";
            healthVersion.textContent = data.version || "1.0.0";
            healthEnv.textContent = data.environment || "development";
            healthTimestamp.textContent = new Date(data.timestamp).toLocaleString();
        } catch (err) {
            statusIndicator.className = "status-indicator error";
            statusBadge.textContent = "Backend Offline";
            healthStatus.textContent = "Connection Failed";
            healthStatus.style.color = "#dc2626";
            healthPhase.textContent = "-";
            healthVersion.textContent = "-";
            healthEnv.textContent = "-";
            healthTimestamp.textContent = `Error: ${err.message}`;
        }
    }

    if (btnRefresh) {
        btnRefresh.addEventListener("click", checkBackendHealth);
    }

    // Initial check
    checkBackendHealth();
});
