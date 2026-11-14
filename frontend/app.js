/**
 * ClaimSense AI - Frontend Controller (Hardened)
 * Phase 1, 2 & 3: Health Monitoring, Claim Submission, Authentication,
 *                 Policy Claim Lookup, CSRF Token Handling, XSS Sanitization,
 *                 and Official PDF Receipt Engine.
 */

document.addEventListener("DOMContentLoaded", () => {
    let currentUser = null;
    let csrfToken = null;

    // -------------------------------------------------------------
    // Helper: HTML Entity Escaping (Prevent Stored & Reflected XSS)
    // -------------------------------------------------------------
    function escapeHTML(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // -------------------------------------------------------------
    // CSRF Token Management
    // -------------------------------------------------------------
    async function fetchCsrfToken() {
        try {
            const res = await fetch("/api/auth/csrf-token");
            if (res.ok) {
                const data = await res.json();
                csrfToken = data.csrf_token;
            }
        } catch (err) {
            console.warn("Could not retrieve CSRF token:", err);
        }
    }
    fetchCsrfToken();

    // -------------------------------------------------------------
    // 1. Health Monitoring (Phase 1)
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
        if (statusIndicator) statusIndicator.className = "status-indicator";
        if (statusBadge) statusBadge.textContent = "Checking backend...";
        if (healthStatus) healthStatus.textContent = "Connecting...";

        try {
            const response = await fetch("/api/health");
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}`);
            }

            const data = await response.json();
            if (statusIndicator) statusIndicator.className = "status-indicator connected";
            if (statusBadge) statusBadge.textContent = "Backend Connected";
            if (healthStatus) {
                healthStatus.textContent = `${escapeHTML(data.status).toUpperCase()} (HTTP 200)`;
                healthStatus.style.color = "var(--success)";
            }
            if (healthPhase) healthPhase.textContent = data.phase || "Active";
            if (healthVersion) healthVersion.textContent = data.version || "1.0.0";
            if (healthEnv) healthEnv.textContent = data.environment || "development";
            if (healthTimestamp) healthTimestamp.textContent = new Date(data.timestamp).toLocaleString();
        } catch (err) {
            if (statusIndicator) statusIndicator.className = "status-indicator error";
            if (statusBadge) statusBadge.textContent = "Backend Offline";
            if (healthStatus) {
                healthStatus.textContent = "Connection Failed";
                healthStatus.style.color = "var(--danger)";
            }
            if (healthPhase) healthPhase.textContent = "-";
            if (healthVersion) healthVersion.textContent = "-";
            if (healthEnv) healthEnv.textContent = "-";
            if (healthTimestamp) healthTimestamp.textContent = `Error: ${err.message}`;
        }
    }

    if (btnRefresh) {
        btnRefresh.addEventListener("click", checkBackendHealth);
    }
    checkBackendHealth();

    // -------------------------------------------------------------
    // Theme Switcher (Light / Dark)
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById("theme-toggle");

    function getPreferredTheme() {
        const saved = localStorage.getItem("claimsense-theme");
        if (saved) return saved;
        return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("claimsense-theme", theme);
        updateThemeToggleUI(theme);
    }

    function updateThemeToggleUI(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector(".theme-icon");
        const text = themeToggleBtn.querySelector(".theme-text");
        if (theme === "dark") {
            if (icon) icon.textContent = "☀️";
            if (text) text.textContent = "Light";
            themeToggleBtn.setAttribute("aria-label", "Switch to Light Mode");
        } else {
            if (icon) icon.textContent = "🌙";
            if (text) text.textContent = "Dark";
            themeToggleBtn.setAttribute("aria-label", "Switch to Dark Mode");
        }
    }

    applyTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "light";
            const next = current === "dark" ? "light" : "dark";
            applyTheme(next);
        });
    }

    // -------------------------------------------------------------
    // 2. Authentication & User Session Management (Phase 3)
    // -------------------------------------------------------------
    const authLoggedOut = document.getElementById("auth-logged-out");
    const authLoggedIn = document.getElementById("auth-logged-in");
    const authUsernameSpan = document.getElementById("auth-username");
    const authRoleBadge = document.getElementById("auth-role-badge");
    const btnOpenLogin = document.getElementById("btn-open-login");
    const btnOpenSignup = document.getElementById("btn-open-signup");
    const btnLogout = document.getElementById("btn-logout");
    const btnNavMyClaims = document.getElementById("btn-nav-my-claims");
    const authNotice = document.getElementById("auth-required-notice");

    // Modal elements
    const authModal = document.getElementById("auth-modal");
    const authModalTitle = document.getElementById("auth-modal-title");
    const authModalClose = document.getElementById("auth-modal-close");
    const tabLogin = document.getElementById("tab-login");
    const tabSignup = document.getElementById("tab-signup");
    const formLogin = document.getElementById("form-login");
    const formSignup = document.getElementById("form-signup");
    const authModalError = document.getElementById("auth-modal-error");
    const btnModalSwitchSignup = document.getElementById("btn-modal-switch-signup");
    const btnModalSwitchLogin = document.getElementById("btn-modal-switch-login");

    function renderHeaderAuth(user) {
        currentUser = user;
        if (user) {
            if (authLoggedOut) authLoggedOut.style.display = "none";
            if (authLoggedIn) authLoggedIn.style.display = "flex";
            if (authUsernameSpan) authUsernameSpan.textContent = escapeHTML(user.username);
            if (authRoleBadge) {
                authRoleBadge.textContent = escapeHTML(user.role.toUpperCase());
                authRoleBadge.className = `role-badge ${user.role === "assessor" ? "role-assessor" : user.role === "admin" ? "role-admin" : "role-user"}`;
            }
            if (btnNavMyClaims) btnNavMyClaims.style.display = "inline-flex";
            if (authNotice) authNotice.style.display = "none";
        } else {
            if (authLoggedOut) authLoggedOut.style.display = "flex";
            if (authLoggedIn) authLoggedIn.style.display = "none";
            if (btnNavMyClaims) btnNavMyClaims.style.display = "none";
            if (authNotice) authNotice.style.display = "block";
        }
    }

    async function checkCurrentUserSession() {
        try {
            const res = await fetch("/api/auth/me");
            if (res.ok) {
                const data = await res.json();
                renderHeaderAuth(data.user);
            } else {
                renderHeaderAuth(null);
            }
        } catch {
            renderHeaderAuth(null);
        }
    }
    checkCurrentUserSession();

    function showAuthModal(mode = "login") {
        if (!authModal) return;
        authModal.style.display = "flex";
        if (authModalError) {
            authModalError.style.display = "none";
            authModalError.textContent = "";
        }
        if (mode === "login") {
            if (tabLogin) tabLogin.classList.add("active");
            if (tabSignup) tabSignup.classList.remove("active");
            if (formLogin) formLogin.style.display = "block";
            if (formSignup) formSignup.style.display = "none";
            if (authModalTitle) authModalTitle.textContent = "Sign In to ClaimSense";
        } else {
            if (tabSignup) tabSignup.classList.add("active");
            if (tabLogin) tabLogin.classList.remove("active");
            if (formSignup) formSignup.style.display = "block";
            if (formLogin) formLogin.style.display = "none";
            if (authModalTitle) authModalTitle.textContent = "Create an Account";
        }
    }

    function closeAuthModal() {
        if (!authModal) return;
        authModal.style.display = "none";
        if (formLogin) formLogin.reset();
        if (formSignup) formSignup.reset();
        if (authModalError) {
            authModalError.style.display = "none";
            authModalError.textContent = "";
        }
    }

    if (btnOpenLogin) btnOpenLogin.addEventListener("click", () => showAuthModal("login"));
    if (btnOpenSignup) btnOpenSignup.addEventListener("click", () => showAuthModal("signup"));
    if (authModalClose) authModalClose.addEventListener("click", closeAuthModal);
    if (btnModalSwitchSignup) btnModalSwitchSignup.addEventListener("click", () => showAuthModal("signup"));
    if (btnModalSwitchLogin) btnModalSwitchLogin.addEventListener("click", () => showAuthModal("login"));

    if (tabLogin) tabLogin.addEventListener("click", () => showAuthModal("login"));
    if (tabSignup) tabSignup.addEventListener("click", () => showAuthModal("signup"));

    if (authModal) {
        authModal.addEventListener("click", (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }

    // Login Form Submit
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const identifier = document.getElementById("login-identifier").value.trim();
            const password = document.getElementById("login-password").value;

            if (!csrfToken) await fetchCsrfToken();

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                    },
                    body: JSON.stringify({ identifier, password }),
                });

                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.message || "Failed to log in.");
                }

                renderHeaderAuth(data.user);
                closeAuthModal();
                fetchCsrfToken(); // refresh token after session rotation
            } catch (err) {
                if (authModalError) {
                    authModalError.textContent = err.message;
                    authModalError.style.display = "block";
                }
            }
        });
    }

    // Signup Form Submit
    if (formSignup) {
        formSignup.addEventListener("submit", async (e) => {
            e.preventDefault();
            const full_name = document.getElementById("signup-fullname").value.trim();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value;
            const confirm_password = document.getElementById("signup-confirm").value;

            if (password !== confirm_password) {
                if (authModalError) {
                    authModalError.textContent = "Passwords do not match.";
                    authModalError.style.display = "block";
                }
                return;
            }

            if (!csrfToken) await fetchCsrfToken();

            try {
                const res = await fetch("/api/auth/signup", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                    },
                    body: JSON.stringify({
                        full_name,
                        username,
                        email,
                        password,
                        confirm_password,
                    }),
                });

                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.message || "Registration failed.");
                }

                // Automatically log in
                const loginRes = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                    },
                    body: JSON.stringify({ identifier: username, password }),
                });
                const loginData = await loginRes.json();
                if (loginRes.ok) {
                    renderHeaderAuth(loginData.user);
                }
                closeAuthModal();
                fetchCsrfToken();
            } catch (err) {
                if (authModalError) {
                    authModalError.textContent = err.message;
                    authModalError.style.display = "block";
                }
            }
        });
    }

    // Logout
    if (btnLogout) {
        btnLogout.addEventListener("click", async () => {
            try {
                if (!csrfToken) await fetchCsrfToken();
                await fetch("/api/auth/logout", {
                    method: "POST",
                    headers: {
                        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                    },
                });
            } finally {
                renderHeaderAuth(null);
                fetchCsrfToken();
            }
        });
    }

    // -------------------------------------------------------------
    // 3. Policy Number Claim Lookup (Phase 3)
    // -------------------------------------------------------------
    const formPolicySearch = document.getElementById("form-policy-search");
    const inputPolicySearch = document.getElementById("input-policy-search");
    const policyResultsContainer = document.getElementById("policy-search-results");
    const policyResultsList = document.getElementById("policy-results-list");

    if (formPolicySearch) {
        formPolicySearch.addEventListener("submit", async (e) => {
            e.preventDefault();
            const policyNo = inputPolicySearch.value.trim();
            if (!policyNo) return;

            if (policyResultsContainer) policyResultsContainer.style.display = "block";
            if (policyResultsList) policyResultsList.innerHTML = `<div class="loading-spinner">Searching claims for policy '${escapeHTML(policyNo)}'...</div>`;

            try {
                const res = await fetch(`/api/claims/policy/${encodeURIComponent(policyNo)}`);
                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.message || `No claims found for policy '${policyNo}'`);
                }

                renderClaimResults(data.claims, policyResultsList, `Policy: ${policyNo}`);
            } catch (err) {
                if (policyResultsList) {
                    policyResultsList.innerHTML = `
                        <div class="search-empty-state">
                            <span class="empty-icon">🔍</span>
                            <p>${escapeHTML(err.message)}</p>
                        </div>
                    `;
                }
            }
        });
    }

    // -------------------------------------------------------------
    // 4. "My Claims" Dashboard View (Phase 3)
    // -------------------------------------------------------------
    const myClaimsModal = document.getElementById("my-claims-modal");
    const myClaimsClose = document.getElementById("my-claims-close");
    const myClaimsList = document.getElementById("my-claims-list");

    if (btnNavMyClaims) {
        btnNavMyClaims.addEventListener("click", async (e) => {
            e.preventDefault();
            if (!myClaimsModal) return;
            myClaimsModal.style.display = "flex";
            if (myClaimsList) myClaimsList.innerHTML = `<div class="loading-spinner">Loading your submitted claims...</div>`;

            try {
                const res = await fetch("/api/my-claims");
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.message || "Failed to fetch claim history.");
                }

                renderClaimResults(data.claims, myClaimsList, "Your Claim History");
            } catch (err) {
                if (myClaimsList) {
                    myClaimsList.innerHTML = `
                        <div class="search-empty-state">
                            <span class="empty-icon">⚠️</span>
                            <p>${escapeHTML(err.message)}</p>
                        </div>
                    `;
                }
            }
        });
    }

    if (myClaimsClose) {
        myClaimsClose.addEventListener("click", () => {
            if (myClaimsModal) myClaimsModal.style.display = "none";
        });
    }

    if (myClaimsModal) {
        myClaimsModal.addEventListener("click", (e) => {
            if (e.target === myClaimsModal) myClaimsModal.style.display = "none";
        });
    }

    function renderClaimResults(claims, container, headingText = "") {
        if (!container) return;
        if (!claims || claims.length === 0) {
            container.innerHTML = `
                <div class="search-empty-state">
                    <span class="empty-icon">📂</span>
                    <p>No claims found under this record.</p>
                </div>
            `;
            return;
        }

        let html = "";
        claims.forEach((claim) => {
            const dateStr = claim.created_at ? new Date(claim.created_at).toLocaleDateString() : "N/A";
            const docCount = claim.documents ? claim.documents.length : (claim.files ? Object.keys(claim.files).length : 0);
            html += `
                <div class="claim-result-card">
                    <div class="claim-card-header">
                        <span class="claim-card-id">${escapeHTML(claim.claim_id)}</span>
                        <span class="claim-card-status">${escapeHTML(claim.status || "SUBMITTED")}</span>
                    </div>
                    <div class="claim-card-body">
                        <div class="claim-card-row">
                            <span class="card-label">Claimant:</span>
                            <span class="card-val">${escapeHTML(claim.claimant_name)}</span>
                        </div>
                        <div class="claim-card-row">
                            <span class="card-label">Policy Number:</span>
                            <span class="card-val">${escapeHTML(claim.policy_number)}</span>
                        </div>
                        <div class="claim-card-row">
                            <span class="card-label">Vehicle:</span>
                            <span class="card-val">${escapeHTML(claim.vehicle_number)}</span>
                        </div>
                        <div class="claim-card-row">
                            <span class="card-label">Accident Date:</span>
                            <span class="card-val">${escapeHTML(claim.accident_date)}</span>
                        </div>
                        <div class="claim-card-desc">
                            ${escapeHTML(claim.claim_description)}
                        </div>
                    </div>
                    <div class="claim-card-footer">
                        <span class="card-footer-meta">Submitted: ${escapeHTML(dateStr)} &bull; ${docCount} files</span>
                        <div class="card-actions">
                            <a href="/api/claims/${encodeURIComponent(claim.claim_id)}/receipt" target="_blank" class="btn btn-sm btn-outline">
                                📄 Receipt (PDF)
                            </a>
                            <a href="/api/claims/${encodeURIComponent(claim.claim_id)}/receipt?format=json" target="_blank" class="btn btn-sm btn-ghost">
                                { JSON }
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // -------------------------------------------------------------
    // 5. File Upload Previews & Drag-and-Drop
    // -------------------------------------------------------------
    const fileDropZones = document.querySelectorAll(".file-drop-zone");

    fileDropZones.forEach((zone) => {
        const input = zone.querySelector("input[type='file']");
        const preview = zone.querySelector(".file-preview");

        if (!input || !preview) return;

        zone.addEventListener("click", (e) => {
            if (e.target !== input) input.click();
        });

        zone.addEventListener("dragover", (e) => {
            e.preventDefault();
            zone.classList.add("drag-over");
        });

        zone.addEventListener("dragleave", () => {
            zone.classList.remove("drag-over");
        });

        zone.addEventListener("drop", (e) => {
            e.preventDefault();
            zone.classList.remove("drag-over");
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                updateFilePreview(input, preview);
            }
        });

        input.addEventListener("change", () => {
            updateFilePreview(input, preview);
        });
    });

    function updateFilePreview(input, previewElement) {
        if (!input.files || input.files.length === 0) {
            previewElement.textContent = "";
            previewElement.style.display = "none";
            return;
        }

        const file = input.files[0];
        const sizeKb = (file.size / 1024).toFixed(1);
        previewElement.textContent = `✓ Selected: ${file.name} (${sizeKb} KB)`;
        previewElement.style.display = "block";
    }

    // -------------------------------------------------------------
    // 6. Claim Submission Form (Phase 2 & 3)
    // -------------------------------------------------------------
    const claimForm = document.getElementById("claim-form");
    const btnSubmit = document.getElementById("btn-submit-claim");
    const errorAlert = document.getElementById("error-alert");
    const errorMessage = document.getElementById("error-message");
    const submissionCard = document.getElementById("submission-card");
    const successCard = document.getElementById("success-card");

    const resClaimId = document.getElementById("res-claim-id");
    const resClaimantName = document.getElementById("res-claimant-name");
    const resPolicyNumber = document.getElementById("res-policy-number");
    const resVehicleNumber = document.getElementById("res-vehicle-number");
    const resAccidentDate = document.getElementById("res-accident-date");
    const resClaimDescription = document.getElementById("res-claim-description");
    const resFileCount = document.getElementById("res-file-count");
    const resTimestamp = document.getElementById("res-timestamp");
    const btnDownloadReceipt = document.getElementById("btn-download-receipt");

    const btnNewClaim = document.getElementById("btn-new-claim");
    const btnCopyClaimId = document.getElementById("btn-copy-claim-id");
    const btnFillSample = document.getElementById("btn-fill-sample");

    function showError(msg) {
        if (!errorAlert || !errorMessage) return;
        errorMessage.textContent = msg;
        errorAlert.style.display = "flex";
        errorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function clearError() {
        if (!errorAlert || !errorMessage) return;
        errorMessage.textContent = "";
        errorAlert.style.display = "none";
    }

    function setSubmittingState(isSubmitting) {
        if (!btnSubmit) return;
        btnSubmit.disabled = isSubmitting;
        const btnText = btnSubmit.querySelector(".btn-text");
        const btnSpinner = btnSubmit.querySelector(".btn-spinner");
        if (btnText) btnText.textContent = isSubmitting ? "Validating & Submitting..." : "Submit Claim for Verification";
        if (btnSpinner) btnSpinner.style.display = isSubmitting ? "inline-block" : "none";
    }

    if (claimForm) {
        claimForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearError();

            // Client-side authentication check
            if (!currentUser) {
                showError("Authentication required: Please sign in or create an account before submitting a claim.");
                showAuthModal("login");
                return;
            }

            // Client-side validation
            const claimantName = document.getElementById("claimant_name")?.value.trim();
            const policyNumber = document.getElementById("policy_number")?.value.trim();
            const vehicleNumber = document.getElementById("vehicle_number")?.value.trim();
            const accidentDate = document.getElementById("accident_date")?.value.trim();
            const claimDesc = document.getElementById("claim_description")?.value.trim();

            if (!claimantName || !policyNumber || !vehicleNumber || !accidentDate || !claimDesc) {
                showError("Please fill out all required text fields.");
                return;
            }

            const requiredFiles = [
                { id: "policy_document", label: "Policy Document" },
                { id: "claim_form_file", label: "Claim Form" },
                { id: "invoice_document", label: "Invoice / Repair Estimate" },
                { id: "vehicle_image", label: "Accident / Vehicle Image" },
            ];

            for (const rf of requiredFiles) {
                const el = document.getElementById(rf.id);
                if (!el || !el.files || el.files.length === 0) {
                    showError(`Missing required file: ${rf.label}`);
                    return;
                }
            }

            setSubmittingState(true);

            const formData = new FormData();
            formData.append("claimant_name", claimantName);
            formData.append("policy_number", policyNumber);
            formData.append("vehicle_number", vehicleNumber);
            formData.append("accident_date", accidentDate);
            formData.append("claim_description", claimDesc);

            formData.append("policy_document", document.getElementById("policy_document").files[0]);
            formData.append("claim_form", document.getElementById("claim_form_file").files[0]);
            formData.append("invoice_document", document.getElementById("invoice_document").files[0]);
            formData.append("vehicle_image", document.getElementById("vehicle_image").files[0]);

            if (!csrfToken) await fetchCsrfToken();

            try {
                const response = await fetch("/api/claims", {
                    method: "POST",
                    headers: {
                        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                    },
                    body: formData,
                });

                const result = await response.json();

                if (!response.ok) {
                    let errMsg = result.message || "Failed to submit claim.";
                    if (result.details && Array.isArray(result.details)) {
                        errMsg += ` (${result.details.join("; ")})`;
                    }
                    throw new Error(errMsg);
                }

                // Render success details
                resClaimId.textContent = result.claim_id;
                resClaimantName.textContent = result.data.claimant_name;
                resPolicyNumber.textContent = result.data.policy_number;
                resVehicleNumber.textContent = result.data.vehicle_number;
                resAccidentDate.textContent = result.data.accident_date;
                resClaimDescription.textContent = result.data.claim_description;
                resFileCount.textContent = `${result.data.files_count || 4} evidence files safely saved`;
                resTimestamp.textContent = new Date(result.data.created_at).toLocaleString();

                // Set receipt download link
                if (btnDownloadReceipt) {
                    btnDownloadReceipt.href = `/api/claims/${result.claim_id}/receipt`;
                }

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
    // 7. Reset / Submit Another Claim
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
    // 8. Copy Claim ID to Clipboard
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
    // 9. Fill Sample Demo Data
    // -------------------------------------------------------------
    if (btnFillSample) {
        btnFillSample.addEventListener("click", () => {
            document.getElementById("claimant_name").value = "Rajesh Sharma";
            document.getElementById("policy_number").value = "POL-2024-88391";
            document.getElementById("vehicle_number").value = "MH-12-DE-4052";
            document.getElementById("accident_date").value = "2026-09-28";
            document.getElementById("claim_description").value =
                "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.";

            // Helper to create synthetic files with valid magic signatures for file inputs
            const createDummyFile = (name, type, headerBytes, contentStr) => {
                const enc = new TextEncoder();
                const textBytes = enc.encode(contentStr);
                const combined = new Uint8Array(headerBytes.length + textBytes.length);
                combined.set(headerBytes, 0);
                combined.set(textBytes, headerBytes.length);
                const blob = new Blob([combined], { type: type });
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

            // Valid signatures: PDF (%PDF), JPEG (\xff\xd8\xff)
            const pdfSig = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x34]); // %PDF-1.4
            const jpgSig = new Uint8Array([0xFF, 0xD8, 0xFF, 0xE0]);

            setFileInput("policy_document", createDummyFile("policy_schedule_88391.pdf", "application/pdf", pdfSig, " sample policy"));
            setFileInput("claim_form_file", createDummyFile("signed_claim_form.pdf", "application/pdf", pdfSig, " claim application"));
            setFileInput("invoice_document", createDummyFile("garage_estimate_4052.pdf", "application/pdf", pdfSig, " itemized estimate"));
            setFileInput("vehicle_image", createDummyFile("rear_bumper_damage.jpg", "image/jpeg", jpgSig, " sample image bytes"));

            clearError();
        });
    }
});
