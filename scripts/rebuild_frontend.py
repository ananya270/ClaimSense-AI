"""Script to generate clean frontend/app.js without merge conflict markers."""
import re

head_code = r'''/**
 * ClaimSense AI - Unified Frontend Controller
 * Complete Phase 1-5 Implementation:
 *   - Phase 1 & 2: Health Monitoring, Multi-Source Evidence Upload, Real-Time Validation
 *   - Phase 3: User Authentication, Session Rotation, CSRF Protection, XSS Sanitization, PDF Receipts
 *   - Phase 4: Three-Section Dashboard, Policy & Claim Lookup, Replacement Vehicle Image Handling
 *   - Phase 5: YOLOv8 Computer Vision Damage Detection & Automated Visual Inspection
 */

document.addEventListener("DOMContentLoaded", () => {
    let currentUser = null;
    let currentActiveClaimId = null;
    let activeSection = "submit";
    let mySubmissionsData = [];
    let csrfToken = null;

    // -------------------------------------------------------------
    // Helper: HTML Entity Escaping (Prevent Stored & Reflected XSS)
    // -------------------------------------------------------------
    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    const escapeHTML = escapeHtml;

    // -------------------------------------------------------------
    // Helper: Format File Sizes
    // -------------------------------------------------------------
    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }

    // -------------------------------------------------------------
    // Robust CSRF Token Management & Input Synchronization
    // -------------------------------------------------------------
    function getCsrfToken() {
        if (csrfToken) return csrfToken;
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content && meta.content.trim()) {
            csrfToken = meta.content.trim();
            return csrfToken;
        }
        const match = document.cookie.match(/(?:^|;\s*)claimsense_csrf_token=([^;]+)/);
        if (match && match[1]) {
            csrfToken = decodeURIComponent(match[1]).trim();
            return csrfToken;
        }
        const input = document.querySelector('input[name="csrf_token"]');
        if (input && input.value && input.value.trim()) {
            csrfToken = input.value.trim();
            return csrfToken;
        }
        return null;
    }

    function syncCsrfInputs(token) {
        if (!token) return;
        csrfToken = token;
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) meta.content = token;
        document.querySelectorAll('input[name="csrf_token"]').forEach((input) => {
            input.value = token;
        });
    }

    async function fetchCsrfToken() {
        try {
            const res = await fetch("/api/auth/csrf-token", { credentials: "same-origin" });
            if (res.ok) {
                const data = await res.json();
                if (data && data.csrf_token) {
                    syncCsrfInputs(data.csrf_token);
                    return data.csrf_token;
                }
            }
        } catch (err) {
            console.warn("Could not retrieve CSRF token from endpoint:", err);
        }
        const fallback = getCsrfToken();
        if (fallback) syncCsrfInputs(fallback);
        return fallback;
    }

    // Synchronize initial CSRF token immediately on page load
    const initialCsrf = getCsrfToken();
    if (initialCsrf) {
        syncCsrfInputs(initialCsrf);
    }
    fetchCsrfToken();

    // -------------------------------------------------------------
    // 1. Lightweight Backend Health Monitor (Header Status)
    // -------------------------------------------------------------
    const statusIndicator = document.getElementById("status-indicator");
    const statusBadge = document.getElementById("status-badge");

    async function checkBackendHealth() {
        if (statusIndicator) statusIndicator.className = "status-indicator";
        if (statusBadge) statusBadge.textContent = "Checking backend...";

        try {
            const res = await fetch("/api/health");
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (statusIndicator) statusIndicator.className = "status-indicator connected";
            if (statusBadge) statusBadge.textContent = "Backend Connected";
        } catch (err) {
            if (statusIndicator) statusIndicator.className = "status-indicator error";
            if (statusBadge) statusBadge.textContent = "Backend Disconnected";
        }
    }
    checkBackendHealth();
    setInterval(checkBackendHealth, 30000);

    // -------------------------------------------------------------
    // 2. Theme Toggle (Dark / Light Theme Persistence)
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById("theme-toggle");

    function getPreferredTheme() {
        const saved = localStorage.getItem("claimsense_theme");
        if (saved) return saved;
        return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    }

    function applyTheme(theme) {
        if (theme === "light") {
            document.documentElement.setAttribute("data-theme", "light");
        } else {
            document.documentElement.removeAttribute("data-theme");
        }
        localStorage.setItem("claimsense_theme", theme);
        updateThemeToggleUI(theme);
    }

    function updateThemeToggleUI(theme) {
        if (!themeToggleBtn) return;
        const label = themeToggleBtn.querySelector(".theme-label");
        const icon = themeToggleBtn.querySelector(".theme-icon");
        if (theme === "light") {
            if (icon) {
                icon.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
            }
            if (label) label.textContent = "Light";
            themeToggleBtn.setAttribute("aria-label", "Switch to Dark Mode");
            themeToggleBtn.setAttribute("title", "Switch to Dark Theme");
        } else {
            if (icon) {
                icon.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
            }
            if (label) label.textContent = "Dark";
            themeToggleBtn.setAttribute("aria-label", "Switch to Light Mode");
            themeToggleBtn.setAttribute("title", "Switch to Light Theme");
        }
    }

    applyTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
            applyTheme(current === "light" ? "dark" : "light");
        });
    }

    // -------------------------------------------------------------
    // 3. User Authentication & Session Management
    // -------------------------------------------------------------
    const authModal = document.getElementById("auth-modal");
    const authModalClose = document.getElementById("btn-close-auth-modal") || document.getElementById("auth-modal-close");
    const tabBtnLogin = document.getElementById("tab-btn-login");
    const tabBtnSignup = document.getElementById("tab-btn-signup");
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const authAlert = document.getElementById("auth-alert");
    const headerAuth = document.getElementById("header-auth");

    const linkSwitchToSignup = document.getElementById("link-switch-to-signup");
    const linkSwitchToLogin = document.getElementById("link-switch-to-login");

    function showAuthAlert(msg) {
        if (!authAlert) return;
        authAlert.textContent = msg;
        authAlert.style.display = "block";
    }

    function clearAuthAlert() {
        if (!authAlert) return;
        authAlert.textContent = "";
        authAlert.style.display = "none";
    }

    function openAuthModal(tab = "login") {
        if (!authModal) return;
        clearAuthAlert();
        switchAuthTab(tab);
        authModal.style.display = "flex";
        fetchCsrfToken();
    }
    const showAuthModal = openAuthModal;

    function closeAuthModal() {
        if (!authModal) return;
        authModal.style.display = "none";
        clearAuthAlert();
        if (loginForm) loginForm.reset();
        if (signupForm) signupForm.reset();
    }

    function switchAuthTab(tab) {
        clearAuthAlert();
        if (tab === "login") {
            if (tabBtnLogin) tabBtnLogin.classList.add("active");
            if (tabBtnSignup) tabBtnSignup.classList.remove("active");
            if (loginForm) loginForm.style.display = "block";
            if (signupForm) signupForm.style.display = "none";
            const title = document.getElementById("modal-title");
            if (title) title.textContent = "Account Sign In";
        } else {
            if (tabBtnSignup) tabBtnSignup.classList.add("active");
            if (tabBtnLogin) tabBtnLogin.classList.remove("active");
            if (loginForm) loginForm.style.display = "none";
            if (signupForm) signupForm.style.display = "block";
            const title = document.getElementById("modal-title");
            if (title) title.textContent = "Create New Account";
        }
    }

    if (authModalClose) authModalClose.addEventListener("click", closeAuthModal);
    if (tabBtnLogin) tabBtnLogin.addEventListener("click", () => switchAuthTab("login"));
    if (tabBtnSignup) tabBtnSignup.addEventListener("click", () => switchAuthTab("signup"));
    if (linkSwitchToSignup) {
        linkSwitchToSignup.addEventListener("click", (e) => {
            e.preventDefault();
            switchAuthTab("signup");
        });
    }
    if (linkSwitchToLogin) {
        linkSwitchToLogin.addEventListener("click", (e) => {
            e.preventDefault();
            switchAuthTab("login");
        });
    }

    // Modal background click to close
    window.addEventListener("click", (e) => {
        if (e.target === authModal) closeAuthModal();
        const modalClaimDetails = document.getElementById("modal-claim-details");
        const modalClaimEvidence = document.getElementById("modal-claim-evidence");
        if (e.target === modalClaimDetails && typeof closeClaimDetailsModal === "function") closeClaimDetailsModal();
        if (e.target === modalClaimEvidence && typeof closeClaimEvidenceModal === "function") closeClaimEvidenceModal();
    });

    function renderHeaderAuth() {
        if (!headerAuth) return;
        if (currentUser) {
            headerAuth.innerHTML = `
                <div class="user-badge" id="user-badge">
                    <span class="user-role-pill">${escapeHtml(currentUser.role || "user")}</span>
                    <span>${escapeHtml(currentUser.full_name || currentUser.username)}</span>
                </div>
                <button type="button" id="btn-header-logout" class="btn btn-outline btn-sm">Sign Out</button>
            `;
            const btnLogout = document.getElementById("btn-header-logout");
            if (btnLogout) {
                btnLogout.addEventListener("click", handleLogout);
            }
        } else {
            headerAuth.innerHTML = `
                <button type="button" id="btn-nav-login" class="btn btn-secondary btn-sm">Sign In</button>
                <button type="button" id="btn-nav-signup" class="btn btn-primary btn-sm">Register</button>
            `;
            const btnLogin = document.getElementById("btn-nav-login");
            const btnSignup = document.getElementById("btn-nav-signup");
            if (btnLogin) btnLogin.addEventListener("click", () => openAuthModal("login"));
            if (btnSignup) btnSignup.addEventListener("click", () => openAuthModal("signup"));
        }
    }

    async function checkCurrentUserSession() {
        try {
            const res = await fetch("/api/auth/me", { credentials: "same-origin" });
            if (res.ok) {
                const data = await res.json();
                if (data.authenticated && data.user) {
                    currentUser = data.user;
                } else {
                    currentUser = null;
                }
            } else {
                currentUser = null;
            }
        } catch {
            currentUser = null;
        } finally {
            renderHeaderAuth();
        }
    }
    checkCurrentUserSession();

    // Login Form Submit
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();
            const idInput = document.getElementById("login-identifier");
            const pwdInput = document.getElementById("login-password");
            const identifier = idInput ? idInput.value.trim() : "";
            const password = pwdInput ? pwdInput.value : "";

            if (!identifier || !password) {
                showAuthAlert("Please enter both identifier and password.");
                return;
            }

            let token = getCsrfToken();
            if (!token) token = await fetchCsrfToken();
            if (token) syncCsrfInputs(token);

            const headers = { "Content-Type": "application/json" };
            if (token) {
                headers["X-CSRFToken"] = token;
                headers["X-CSRF-Token"] = token;
            }

            const payload = { identifier, password };
            if (token) payload["csrf_token"] = token;

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    credentials: "same-origin",
                    headers,
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    showAuthAlert(data.message || "Invalid username or password.");
                    return;
                }

                currentUser = data.user;
                renderHeaderAuth();
                if (data.csrf_token) syncCsrfInputs(data.csrf_token);
                closeAuthModal();

                if (activeSection === "myclaims" && typeof loadMyClaims === "function") {
                    loadMyClaims();
                }
            } catch (err) {
                showAuthAlert(`Login failed: ${err.message}`);
            }
        });
    }

    // Signup Form Submit
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const fullNameInput = document.getElementById("signup-fullname");
            const usernameInput = document.getElementById("signup-username");
            const emailInput = document.getElementById("signup-email");
            const passwordInput = document.getElementById("signup-password");
            const confirmInput = document.getElementById("signup-confirm");

            const full_name = fullNameInput ? fullNameInput.value.trim() : "";
            const username = usernameInput ? usernameInput.value.trim() : "";
            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";
            const confirm_password = confirmInput ? confirmInput.value : "";

            if (!full_name || !username || !email || !password || !confirm_password) {
                showAuthAlert("All fields are required.");
                return;
            }

            if (password.length < 8 || !/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
                showAuthAlert("Password must be at least 8 characters and include both letters and numbers.");
                return;
            }

            if (password !== confirm_password) {
                showAuthAlert("Passwords do not match.");
                return;
            }

            let token = getCsrfToken();
            if (!token) token = await fetchCsrfToken();
            if (token) syncCsrfInputs(token);

            const headers = { "Content-Type": "application/json" };
            if (token) {
                headers["X-CSRFToken"] = token;
                headers["X-CSRF-Token"] = token;
            }

            const payload = {
                full_name,
                username,
                email,
                password,
                confirm_password,
            };
            if (token) payload["csrf_token"] = token;

            try {
                const res = await fetch("/api/auth/signup", {
                    method: "POST",
                    credentials: "same-origin",
                    headers,
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    showAuthAlert(data.message || "Failed to create account.");
                    return;
                }

                if (data.csrf_token) syncCsrfInputs(data.csrf_token);

                // Auto login after successful signup
                const loginToken = getCsrfToken();
                const loginHeaders = { "Content-Type": "application/json" };
                if (loginToken) {
                    loginHeaders["X-CSRFToken"] = loginToken;
                    loginHeaders["X-CSRF-Token"] = loginToken;
                }
                const loginPayload = { identifier: username, password };
                if (loginToken) loginPayload["csrf_token"] = loginToken;

                try {
                    const loginRes = await fetch("/api/auth/login", {
                        method: "POST",
                        credentials: "same-origin",
                        headers: loginHeaders,
                        body: JSON.stringify(loginPayload),
                    });
                    const loginData = await loginRes.json();
                    if (loginRes.ok && loginData.success) {
                        currentUser = loginData.user;
                        renderHeaderAuth();
                        if (loginData.csrf_token) syncCsrfInputs(loginData.csrf_token);
                    }
                } catch {
                    // Fallback to switching tab
                }

                closeAuthModal();
                if (activeSection === "myclaims" && typeof loadMyClaims === "function") {
                    loadMyClaims();
                }
            } catch (err) {
                showAuthAlert(`Account registration failed: ${err.message}`);
            }
        });
    }

    async function handleLogout() {
        try {
            let token = getCsrfToken();
            if (!token) token = await fetchCsrfToken();
            const headers = {};
            if (token) {
                headers["X-CSRFToken"] = token;
                headers["X-CSRF-Token"] = token;
            }
            await fetch("/api/auth/logout", {
                method: "POST",
                credentials: "same-origin",
                headers,
            });
        } catch {
            // ignore network error on logout
        } finally {
            currentUser = null;
            renderHeaderAuth();
            fetchCsrfToken();
            if (activeSection === "myclaims") {
                switchView("submit");
            }
        }
    }

    // -------------------------------------------------------------
    // 4. Three-Section Navigation Architecture
    // -------------------------------------------------------------
    const pillSubmit = document.getElementById("pill-nav-submit");
    const pillSearch = document.getElementById("pill-nav-search");
    const pillMyClaims = document.getElementById("pill-nav-myclaims");

    const sectionSubmit = document.getElementById("section-submit");
    const sectionLookup = document.getElementById("section-lookup");
    const sectionMyClaims = document.getElementById("section-myclaims");

    const submissionCard = document.getElementById("submission-card");
    const successCard = document.getElementById("submission-success-card");

    function switchView(sectionName) {
        activeSection = sectionName;

        // Reset pills
        [pillSubmit, pillSearch, pillMyClaims].forEach((p) => {
            if (p) {
                p.classList.remove("active");
                p.setAttribute("aria-selected", "false");
            }
        });

        // Hide all 3 sections
        if (sectionSubmit) sectionSubmit.style.display = "none";
        if (sectionLookup) sectionLookup.style.display = "none";
        if (sectionMyClaims) sectionMyClaims.style.display = "none";

        if (sectionName === "submit") {
            if (pillSubmit) {
                pillSubmit.classList.add("active");
                pillSubmit.setAttribute("aria-selected", "true");
            }
            if (sectionSubmit) sectionSubmit.style.display = "block";
        } else if (sectionName === "search") {
            if (pillSearch) {
                pillSearch.classList.add("active");
                pillSearch.setAttribute("aria-selected", "true");
            }
            if (sectionLookup) sectionLookup.style.display = "block";
        } else if (sectionName === "myclaims") {
            if (pillMyClaims) {
                pillMyClaims.classList.add("active");
                pillMyClaims.setAttribute("aria-selected", "true");
            }
            if (sectionMyClaims) sectionMyClaims.style.display = "block";
            if (typeof loadMyClaims === "function") loadMyClaims();
        }
    }

    if (pillSubmit) pillSubmit.addEventListener("click", () => switchView("submit"));
    if (pillSearch) pillSearch.addEventListener("click", () => switchView("search"));
    if (pillMyClaims) pillMyClaims.addEventListener("click", () => {
        if (!currentUser) {
            openAuthModal("login");
            showAuthAlert("Please sign in to view your submitted claims.");
            return;
        }
        switchView("myclaims");
    });

    // -------------------------------------------------------------
    // 5. Selected Filenames Badges & Size Formatting
    // -------------------------------------------------------------
    function setupFileBadge(inputId, badgeId) {
        const input = document.getElementById(inputId);
        const badge = document.getElementById(badgeId);
        if (!input || !badge) return;

        input.addEventListener("change", () => {
            if (input.files && input.files.length > 0) {
                const file = input.files[0];
                const nameSpan = badge.querySelector(".selected-filename");
                const sizeSpan = badge.querySelector(".selected-filesize");
                if (nameSpan) nameSpan.textContent = file.name;
                if (sizeSpan) sizeSpan.textContent = `(${formatBytes(file.size)})`;
                badge.style.display = "inline-flex";
            } else {
                badge.style.display = "none";
            }
        });
    }

    setupFileBadge("policy_document", "badge-policy_document");
    setupFileBadge("claim_form_file", "badge-claim_form_file");
    setupFileBadge("invoice_document", "badge-invoice_document");
    setupFileBadge("vehicle_image", "badge-vehicle_image");

    function refreshFileBadges() {
        ["policy_document", "claim_form_file", "invoice_document", "vehicle_image"].forEach((id) => {
            const input = document.getElementById(id);
            const badge = document.getElementById(`badge-${id}`);
            if (input && badge && input.files && input.files.length > 0) {
                const file = input.files[0];
                const nameSpan = badge.querySelector(".selected-filename");
                const sizeSpan = badge.querySelector(".selected-filesize");
                if (nameSpan) nameSpan.textContent = file.name;
                if (sizeSpan) sizeSpan.textContent = `(${formatBytes(file.size)})`;
                badge.style.display = "inline-flex";
            } else if (badge) {
                badge.style.display = "none";
            }
        });
    }

    // -------------------------------------------------------------
    // 6. Section 1: Submit Claim Evidence
    // -------------------------------------------------------------
    const claimForm = document.getElementById("claim-form");
    const btnSubmitClaim = document.getElementById("btn-submit-claim");
    const errorAlert = document.getElementById("form-error-alert") || document.getElementById("error-alert");
    const errorMessage = document.getElementById("error-message");

    const resClaimId = document.getElementById("res-claim-id");
    const resClaimantName = document.getElementById("res-claimant-name");
    const resPolicyNumber = document.getElementById("res-policy-number");
    const resVehicleNumber = document.getElementById("res-vehicle-number");
    const resAccidentDate = document.getElementById("res-accident-date");
    const resIncidentLocation = document.getElementById("res-incident-location");
    const resClaimDescription = document.getElementById("res-claim-description");
    const resFileCount = document.getElementById("res-file-count");
    const resTimestamp = document.getElementById("res-timestamp");
    const btnDownloadReceipt = document.getElementById("btn-download-receipt");
    const btnDownloadDocumentReport = document.getElementById("btn-download-document-report");
    const btnViewClaimModal = document.getElementById("btn-view-claim-modal");

    const btnNewClaim = document.getElementById("btn-new-claim");
    const btnCopyClaimId = document.getElementById("btn-copy-claim-id");
    const btnFillSample = document.getElementById("btn-fill-sample");

    function showError(msg) {
        if (!errorAlert) return;
        if (errorMessage) {
            errorMessage.textContent = msg;
        } else {
            errorAlert.textContent = msg;
        }
        errorAlert.style.display = "block";
        errorAlert.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function clearError() {
        if (!errorAlert) return;
        if (errorMessage) errorMessage.textContent = "";
        errorAlert.textContent = "";
        errorAlert.style.display = "none";
    }

    function setSubmittingState(isSubmitting) {
        if (!btnSubmitClaim) return;
        btnSubmitClaim.disabled = isSubmitting;
        const btnText = btnSubmitClaim.querySelector(".btn-text");
        const btnSpinner = btnSubmitClaim.querySelector(".btn-spinner");
        if (btnText && btnSpinner) {
            btnText.style.display = isSubmitting ? "none" : "inline";
            btnSpinner.style.display = isSubmitting ? "inline-flex" : "none";
        }
    }

    if (claimForm) {
        claimForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearError();

            // Client-side authentication check
            if (!currentUser) {
                showError("Authentication required: Please sign in or create an account before submitting claim evidence.");
                openAuthModal("login");
                return;
            }

            const formData = new FormData(claimForm);
            const claimantName = formData.get("claimant_name")?.trim();
            const policyNumber = formData.get("policy_number")?.trim();
            const vehicleNumber = formData.get("vehicle_number")?.trim();
            const accidentDate = formData.get("accident_date")?.trim();
            const claimDesc = formData.get("claim_description")?.trim();

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

            let token = getCsrfToken();
            if (!token) token = await fetchCsrfToken();
            if (token) {
                syncCsrfInputs(token);
                formData.set("csrf_token", token);
            }

            const headers = {};
            if (token) {
                headers["X-CSRFToken"] = token;
                headers["X-CSRF-Token"] = token;
            }

            try {
                const response = await fetch("/api/claims", {
                    method: "POST",
                    credentials: "same-origin",
                    headers,
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

                // Populate success summary
                if (resClaimId) resClaimId.textContent = result.claim_id;
                if (resClaimantName) resClaimantName.textContent = result.data.claimant_name || "-";
                if (resPolicyNumber) resPolicyNumber.textContent = result.data.policy_number || "-";
                if (resVehicleNumber) resVehicleNumber.textContent = result.data.vehicle_number || "-";
                if (resAccidentDate) resAccidentDate.textContent = result.data.accident_date || "-";
                if (resIncidentLocation) {
                    resIncidentLocation.textContent = result.data.incident_location || "Not specified";
                }
                if (resClaimDescription) resClaimDescription.textContent = result.data.claim_description || "-";
                if (resFileCount) resFileCount.textContent = `${result.data.files_count || 4} evidence files safely saved`;
                if (resTimestamp) resTimestamp.textContent = new Date(result.data.created_at).toLocaleString();

                // Download buttons
                if (btnDownloadReceipt) {
                    btnDownloadReceipt.href = `/api/claims/${result.claim_id}/receipt`;
                }
                if (btnDownloadDocumentReport) {
                    btnDownloadDocumentReport.href = `/api/claims/${result.claim_id}/document-report`;
                }
                currentActiveClaimId = result.claim_id;

                // Reset replacement photo box status
                const replaceStatus = document.getElementById("replace-image-status");
                if (replaceStatus) {
                    replaceStatus.style.display = "none";
                    replaceStatus.textContent = "";
                }

                // Switch views within Section 1
                if (submissionCard) submissionCard.style.display = "none";
                if (successCard) {
                    successCard.style.display = "block";
                    successCard.scrollIntoView({ behavior: "smooth" });
                }

            } catch (err) {
                showError(`Submission rejected: ${err.message}`);
            } finally {
                setSubmittingState(false);
            }
        });
    }

    if (btnViewClaimModal) {
        btnViewClaimModal.addEventListener("click", () => {
            if (currentActiveClaimId && typeof openClaimDetailsModal === "function") {
                openClaimDetailsModal(currentActiveClaimId);
            }
        });
    }

    if (btnNewClaim) {
        btnNewClaim.addEventListener("click", () => {
            if (claimForm) claimForm.reset();
            clearError();
            refreshFileBadges();
            if (successCard) successCard.style.display = "none";
            if (submissionCard) {
                submissionCard.style.display = "block";
                submissionCard.scrollIntoView({ behavior: "smooth" });
            }
        });
    }

    if (btnCopyClaimId) {
        btnCopyClaimId.addEventListener("click", async () => {
            const cid = resClaimId ? resClaimId.textContent : "";
            if (!cid) return;
            try {
                await navigator.clipboard.writeText(cid);
                const originalText = btnCopyClaimId.textContent;
                btnCopyClaimId.textContent = "Copied! ✓";
                setTimeout(() => {
                    btnCopyClaimId.textContent = originalText;
                }, 2000);
            } catch {
                alert(`Claim ID: ${cid}`);
            }
        });
    }

    // Replacement Vehicle Photograph Upload
    const formReplaceImage = document.getElementById("form-replace-image");
    const inputReplaceImage = document.getElementById("input-replace-image");
    const replaceImageStatus = document.getElementById("replace-image-status");
    const btnSubmitReplaceImage = document.getElementById("btn-submit-replace-image");

    if (formReplaceImage) {
        formReplaceImage.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!currentActiveClaimId) {
                alert("No active claim identifier found.");
                return;
            }
            if (!inputReplaceImage || !inputReplaceImage.files || inputReplaceImage.files.length === 0) {
                alert("Please select a JPEG or PNG vehicle photograph to upload.");
                return;
            }

            const formData = new FormData();
            formData.append("vehicle_image", inputReplaceImage.files[0]);

            let token = getCsrfToken();
            if (!token) token = await fetchCsrfToken();
            if (token) {
                syncCsrfInputs(token);
                formData.set("csrf_token", token);
            }

            const headers = {};
            if (token) {
                headers["X-CSRFToken"] = token;
                headers["X-CSRF-Token"] = token;
            }

            if (btnSubmitReplaceImage) btnSubmitReplaceImage.disabled = true;
            if (replaceImageStatus) {
                replaceImageStatus.style.display = "block";
                replaceImageStatus.className = "alert alert-info mt-2";
                replaceImageStatus.textContent = "Uploading and validating replacement photograph...";
            }

            try {
                const res = await fetch(`/api/claims/${currentActiveClaimId}/replace-image`, {
                    method: "POST",
                    credentials: "same-origin",
                    headers,
                    body: formData,
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Failed to replace vehicle photograph.");
                }

                if (replaceImageStatus) {
                    if (data.validation && data.validation.is_valid_vehicle_photo) {
                        replaceImageStatus.className = "alert alert-success mt-2";
                        replaceImageStatus.textContent = `✓ Replacement photograph verified as authentic vehicle damage photograph! (${data.validation.resolution || ""})`;
                    } else {
                        replaceImageStatus.className = "alert alert-error mt-2";
                        replaceImageStatus.textContent = `⚠ Uploaded replacement image flagged: ${data.validation ? data.validation.reason : "Invalid photograph format"}`;
                    }
                }
            } catch (err) {
                if (replaceImageStatus) {
                    replaceImageStatus.className = "alert alert-error mt-2";
                    replaceImageStatus.textContent = `Error: ${err.message}`;
                }
            } finally {
                if (btnSubmitReplaceImage) btnSubmitReplaceImage.disabled = false;
            }
        });
    }

    // Fill Sample Demo Data
    if (btnFillSample) {
        btnFillSample.addEventListener("click", () => {
            const elName = document.getElementById("claimant_name");
            const elPolicy = document.getElementById("policy_number");
            const elVehicle = document.getElementById("vehicle_number");
            const elDate = document.getElementById("accident_date");
            const elDesc = document.getElementById("claim_description");
            const locInput = document.getElementById("incident_location");

            if (elName) elName.value = "Rajesh Sharma";
            if (elPolicy) elPolicy.value = "POL-2024-88391";
            if (elVehicle) elVehicle.value = "MH-12-DE-4052";
            if (elDate) elDate.value = "2026-09-28";
            if (locInput) locInput.value = "MG Road, Pune, Maharashtra";
            if (elDesc) {
                elDesc.value = "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.";
            }

            const escapePdfText = (text) => text.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");

            const createSyntheticPdfFile = (name, lines) => {
                const content = lines.map((line, index) => `BT /F1 12 Tf 50 ${760 - index * 20} Td (${escapePdfText(line)}) Tj ET`).join("\n");
                const objects = [
                    "<< /Type /Catalog /Pages 2 0 R >>",
                    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
                    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 4 0 R >> >> >>",
                    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
                    `<< /Length ${content.length} >>\nstream\n${content}\nendstream`
                ];

                let pdf = "%PDF-1.4\n";
                const offsets = [0];
                for (let i = 0; i < objects.length; i += 1) {
                    offsets.push(pdf.length);
                    pdf += `${i + 1} 0 obj\n${objects[i]}\nendobj\n`;
                }
                const xrefStart = pdf.length;
                pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
                for (let i = 1; i <= objects.length; i += 1) {
                    pdf += `${String(offsets[i]).padStart(10, "0")} 00000 n \n`;
                }
                pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;

                return new File([new Blob([pdf], { type: "application/pdf" })], name, { type: "application/pdf" });
            };

            const createSyntheticImageFile = (name) => {
                const canvas = document.createElement("canvas");
                canvas.width = 900;
                canvas.height = 600;
                const ctx = canvas.getContext("2d");
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#1d4ed8";
                ctx.fillRect(60, 70, 220, 80);
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 34px sans-serif";
                ctx.fillText("Rear Bumper", 90, 120);
                ctx.font = "28px sans-serif";
                ctx.fillStyle = "#0f172a";
                ctx.fillText("Policy POL-2024-88391", 60, 240);
                ctx.fillText("Vehicle MH-12-DE-4052", 60, 285);
                ctx.fillText("Accident 2026-09-28", 60, 330);
                const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
                const base64 = dataUrl.split(",")[1];
                const binary = atob(base64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i += 1) {
                    bytes[i] = binary.charCodeAt(i);
                }
                return new File([bytes], name, { type: "image/jpeg" });
            };

            const setFileInput = (id, file) => {
                const input = document.getElementById(id);
                if (input) {
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                }
            };

            setFileInput("policy_document", createSyntheticPdfFile("policy_schedule_88391.pdf", ["CLAIMSENSE AI", "Policy Number: POL-2024-88391", "Vehicle Registration: MH-12-DE-4052", "Accident Date: 2026-09-28"]));
            setFileInput("claim_form_file", createSyntheticPdfFile("signed_claim_form.pdf", ["Claimant: Rajesh Sharma", "Policy Number: POL-2024-88391", "Claim Description: Rear-end collision at MG Road intersection.", "Accident Date: 2026-09-28"]));
            setFileInput("invoice_document", createSyntheticPdfFile("garage_estimate_4052.pdf", ["Garage Estimate", "Claim Amount: INR 84500", "Bodywork and paint: 38500", "Tail lamp replacement: 16000", "Labor and miscellaneous: 30000"]));
            setFileInput("vehicle_image", createSyntheticImageFile("rear_bumper_damage.jpg"));

            refreshFileBadges();
            clearError();
        });
    }
'''

with open("frontend/app.js", "r", encoding="utf-8") as f:
    orig_text = f.read()

# Locate section 7 start
marker = "// 7. Shared Claim Card HTML Renderer"
tail_idx = orig_text.find(marker)
if tail_idx != -1:
    # include the comment divider before it if present
    divider = "// -------------------------------------------------------------\n    " + marker
    if divider in orig_text:
        tail_code = orig_text[orig_text.find(divider):]
    else:
        tail_code = orig_text[tail_idx:]
else:
    raise ValueError("Could not find section 7 marker")

clean_full_code = head_code + "\n\n    " + tail_code

with open("frontend/app.js", "w", encoding="utf-8") as f:
    f.write(clean_full_code)

print("frontend/app.js updated successfully! Line count:", len(clean_full_code.splitlines()))
