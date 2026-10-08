/**
 * ClaimSense AI - Frontend Controller
 * Phase 1 & 2: Health Monitoring, Claim Submission & Tracking
 */

document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // 1. Health Monitoring
    // -------------------------------------------------------------
    const statusIndicator = document.getElementById("status-indicator");
    const statusBadge = document.getElementById("status-badge");
    const healthStatus = document.getElementById("health-status");
    const healthPhase = document.getElementById("health-phase");
    const healthVersion = document.getElementById("health-version");
    const healthEnv = document.getElementById("health-env");
    const healthTimestamp = document.getElementById("health-timestamp");
    const btnRefresh = document.getElementById("btn-refresh-health");

    async function checkBackendHealth() {
        if (!statusIndicator) return;
        statusIndicator.className = "status-indicator";
        statusBadge.textContent = "Checking backend...";
        healthStatus.textContent = "Connecting...";

        try {
            const response = await fetch("/api/health");
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}`);
            }

            const data = await response.json();
            statusIndicator.className = "status-indicator connected";
            statusBadge.textContent = "Backend Connected";
            healthStatus.textContent = `${data.status.toUpperCase()} (HTTP 200)`;
            healthStatus.style.color = "#16a34a";
            healthPhase.textContent = data.phase || "Active";
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
    checkBackendHealth();

    // -------------------------------------------------------------
    // 2. Claim Submission Handling (Phase 2)
    // -------------------------------------------------------------
    const claimForm = document.getElementById("claim-form");
    const formErrorAlert = document.getElementById("form-error-alert");
    const btnSubmitClaim = document.getElementById("btn-submit-claim");
    const btnText = btnSubmitClaim ? btnSubmitClaim.querySelector(".btn-text") : null;
    const btnSpinner = btnSubmitClaim ? btnSubmitClaim.querySelector(".btn-spinner") : null;

    const submissionCard = document.getElementById("submission-card");
    const successCard = document.getElementById("submission-success-card");
    const resClaimId = document.getElementById("res-claim-id");
    const resClaimantName = document.getElementById("res-claimant-name");
    const resPolicyNumber = document.getElementById("res-policy-number");
    const resVehicleNumber = document.getElementById("res-vehicle-number");
    const resAccidentDate = document.getElementById("res-accident-date");
    const resClaimDescription = document.getElementById("res-claim-description");
    const resFileCount = document.getElementById("res-file-count");
    const resTimestamp = document.getElementById("res-timestamp");

    const btnNewClaim = document.getElementById("btn-new-claim");
    const btnCopyClaimId = document.getElementById("btn-copy-claim-id");
    const btnFillSample = document.getElementById("btn-fill-sample");

    function showError(message) {
        if (!formErrorAlert) return;
        formErrorAlert.textContent = message;
        formErrorAlert.style.display = "block";
        formErrorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function clearError() {
        if (!formErrorAlert) return;
        formErrorAlert.textContent = "";
        formErrorAlert.style.display = "none";
    }

    function setSubmittingState(isSubmitting) {
        if (!btnSubmitClaim) return;
        btnSubmitClaim.disabled = isSubmitting;
        if (btnText && btnSpinner) {
            btnText.style.display = isSubmitting ? "none" : "inline";
            btnSpinner.style.display = isSubmitting ? "inline" : "none";
        }
    }

    if (claimForm) {
        claimForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearError();

            const formData = new FormData(claimForm);

            // Basic client-side check
            const claimantName = formData.get("claimant_name");
            const policyNumber = formData.get("policy_number");
            const vehicleNumber = formData.get("vehicle_number");
            const accidentDate = formData.get("accident_date");
            const claimDesc = formData.get("claim_description");

            if (!claimantName || !policyNumber || !vehicleNumber || !accidentDate || !claimDesc) {
                showError("Please fill in all required text fields before submitting.");
                return;
            }

            setSubmittingState(true);

            try {
                const response = await fetch("/api/claims", {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json();

                if (!response.ok || !result.success) {
                    const errorDetail = result.details
                        ? Array.isArray(result.details)
                            ? result.details.join("; ")
                            : JSON.stringify(result.details)
                        : result.message || "Failed to submit claim.";
                    throw new Error(errorDetail);
                }

                // Populate success card
                resClaimId.textContent = result.claim_id;
                resClaimantName.textContent = result.data.claimant_name;
                resPolicyNumber.textContent = result.data.policy_number;
                resVehicleNumber.textContent = result.data.vehicle_number;
                resAccidentDate.textContent = result.data.accident_date;
                resClaimDescription.textContent = result.data.claim_description;
                resFileCount.textContent = `${result.data.files_count || 4} evidence files safely saved`;
                resTimestamp.textContent = new Date(result.data.created_at).toLocaleString();

                // Switch views
                submissionCard.style.display = "none";
                successCard.style.display = "block";
                successCard.scrollIntoView({ behavior: "smooth" });

            } catch (err) {
                showError(`Submission rejected: ${err.message}`);
            } finally {
                setSubmittingState(false);
            }
        });
    }

    // -------------------------------------------------------------
    // 3. Reset / Submit Another Claim
    // -------------------------------------------------------------
    if (btnNewClaim) {
        btnNewClaim.addEventListener("click", () => {
            claimForm.reset();
            clearError();
            successCard.style.display = "none";
            submissionCard.style.display = "block";
            submissionCard.scrollIntoView({ behavior: "smooth" });
        });
    }

    // -------------------------------------------------------------
    // 4. Copy Claim ID to Clipboard
    // -------------------------------------------------------------
    if (btnCopyClaimId) {
        btnCopyClaimId.addEventListener("click", async () => {
            const cid = resClaimId.textContent;
            try {
                await navigator.clipboard.writeText(cid);
                const originalText = btnCopyClaimId.textContent;
                btnCopyClaimId.textContent = "Copied! ✓";
                setTimeout(() => {
                    btnCopyClaimId.textContent = originalText;
                }, 2000);
            } catch (err) {
                alert(`Claim ID: ${cid}`);
            }
        });
    }

    // -------------------------------------------------------------
    // 5. Fill Sample Demo Data
    // -------------------------------------------------------------
    if (btnFillSample) {
        btnFillSample.addEventListener("click", () => {
            document.getElementById("claimant_name").value = "Rajesh Sharma";
            document.getElementById("policy_number").value = "POL-2024-88391";
            document.getElementById("vehicle_number").value = "MH-12-DE-4052";
            document.getElementById("accident_date").value = "2026-09-28";
            document.getElementById("claim_description").value =
                "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.";

            // Helper to create synthetic files for file inputs
            const createDummyFile = (name, type, content) => {
                const blob = new Blob([content], { type: type });
                return new File([blob], name, { type: type });
            };

            const setFileInput = (id, file) => {
                const input = document.getElementById(id);
                if (input) {
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                }
            };

            setFileInput("policy_document", createDummyFile("policy_schedule_88391.pdf", "application/pdf", "%PDF-1.4 sample policy"));
            setFileInput("claim_form_file", createDummyFile("signed_claim_form.pdf", "application/pdf", "%PDF-1.4 claim application"));
            setFileInput("invoice_document", createDummyFile("garage_estimate_4052.pdf", "application/pdf", "%PDF-1.4 itemized estimate"));
            setFileInput("vehicle_image", createDummyFile("rear_bumper_damage.jpg", "image/jpeg", "sample image bytes"));

            clearError();
        });
    }
});
