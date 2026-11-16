/**
 * ClaimSense AI - Unified Frontend Controller
 * Complete Phase 1-5 Implementation:
 *   - Phase 1 & 2: Health Monitoring, Multi-Source Evidence Upload, Real-Time Validation
 *   - Phase 3: User Authentication, Session Rotation, CSRF Protection, XSS Sanitization, PDF Receipts
 *   - Phase 4: Three-Section Dashboard, Policy & Claim Lookup, Replacement Vehicle Image Handling
 *   - Phase 5: YOLOv8 Computer Vision Damage Detection & Automated Visual Inspection
 */

function initClaimSenseApp() {
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
        const saved = localStorage.getItem("claimsense-theme") || localStorage.getItem("claimsense_theme");
        if (saved === "light" || saved === "dark") return saved;
        const currentAttr = document.documentElement.getAttribute("data-theme");
        if (currentAttr === "light" || currentAttr === "dark") return currentAttr;
        return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    }

    function applyTheme(theme) {
        const targetTheme = theme === "light" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", targetTheme);
        localStorage.setItem("claimsense-theme", targetTheme);
        localStorage.setItem("claimsense_theme", targetTheme);
        updateThemeToggleUI(targetTheme);
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

    // -------------------------------------------------------------
    // 7. Shared Claim Card HTML Renderer
    // -------------------------------------------------------------
    function renderClaimCard(claim) {
        const dateStr = claim.created_at ? new Date(claim.created_at).toLocaleDateString() : "-";
        const filesCount = claim.files_count || (claim.documents ? claim.documents.length + (claim.images ? claim.images.length : 0) : 4);
        const locationBadge = `
            <div class="meta-item wide">
                <span class="meta-label">Incident Location</span>
                <span class="meta-val">${claim.incident_location ? escapeHtml(claim.incident_location) : '<span style="color: var(--text-muted); font-weight: normal;">Not specified</span>'}</span>
            </div>`;

        return `
            <div class="claim-result-card" data-claim-id="${escapeHtml(claim.claim_id)}">
                <div class="result-card-header">
                    <div class="claim-id-group">
                        <span class="claim-id-badge">${escapeHtml(claim.claim_id)}</span>
                        <button type="button" class="btn-copy-card-id" data-id="${escapeHtml(claim.claim_id)}" title="Copy Claim ID">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        </button>
                    </div>
                    <span class="status-pill status-ready">
                        <span class="status-dot"></span>
                        ${escapeHtml(claim.status || "SUBMITTED")}
                    </span>
                </div>
                <div class="result-details-grid">
                    <div class="meta-item">
                        <span class="meta-label">Claimant</span>
                        <span class="meta-val">${escapeHtml(claim.claimant_name || "-")}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Policy Number</span>
                        <span class="meta-val monospace-val">${escapeHtml(claim.policy_number || "-")}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Vehicle Registration #</span>
                        <span class="meta-val monospace-val">${escapeHtml(claim.vehicle_number || "-")}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Accident Date</span>
                        <span class="meta-val">${escapeHtml(claim.accident_date || "-")}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Submitted On</span>
                        <span class="meta-val">${escapeHtml(dateStr)}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Evidence Files</span>
                        <span class="meta-val">${filesCount} files attached</span>
                    </div>
                    ${locationBadge}
                </div>
                <div class="result-card-footer">
                    <div class="action-buttons-group">
                        <button type="button" class="btn btn-secondary btn-sm btn-action-details" data-claim-id="${escapeHtml(claim.claim_id)}">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                            <span>View Details</span>
                        </button>
                        <button type="button" class="btn btn-secondary btn-sm btn-action-evidence" data-claim-id="${escapeHtml(claim.claim_id)}">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                            <span>View Evidence</span>
                        </button>
                    </div>
                    <div class="download-buttons-group">
                        <a href="/api/claims/${escapeHtml(claim.claim_id)}/receipt" target="_blank" class="btn btn-outline btn-sm">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                            <span>Receipt</span>
                        </a>
                        <a href="/api/claims/${escapeHtml(claim.claim_id)}/document-report" target="_blank" class="btn btn-primary btn-sm">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                            <span>Report</span>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    function attachCardActionListeners(container) {
        if (!container) return;
        container.querySelectorAll(".btn-action-details").forEach((btn) => {
            btn.addEventListener("click", () => {
                const claimId = btn.getAttribute("data-claim-id");
                if (claimId) openClaimDetailsModal(claimId);
            });
        });
        container.querySelectorAll(".btn-action-evidence").forEach((btn) => {
            btn.addEventListener("click", () => {
                const claimId = btn.getAttribute("data-claim-id");
                if (claimId) openClaimEvidenceModal(claimId);
            });
        });
        container.querySelectorAll(".btn-copy-card-id").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const cid = btn.getAttribute("data-id");
                if (!cid) return;
                try {
                    await navigator.clipboard.writeText(cid);
                    btn.style.color = "var(--success)";
                    setTimeout(() => { btn.style.color = ""; }, 1500);
                } catch {
                    alert(`Claim ID: ${cid}`);
                }
            });
        });
    }

    // -------------------------------------------------------------
    // 8. Section 2: Policy & Claim ID Lookup
    // -------------------------------------------------------------
    const policySearchForm = document.getElementById("policy-search-form");
    const searchPolicyInput = document.getElementById("search-policy-input");
    const policySearchAlert = document.getElementById("policy-search-alert");
    const policySearchResults = document.getElementById("policy-search-results");
    const policyResultsList = document.getElementById("policy-results-list");
    const resultsCount = document.getElementById("results-count");
    const lookupInitialState = document.getElementById("lookup-initial-state");
    const btnClearLookup = document.getElementById("btn-clear-lookup");

    if (btnClearLookup) {
        btnClearLookup.addEventListener("click", () => {
            if (searchPolicyInput) searchPolicyInput.value = "";
            if (policySearchAlert) policySearchAlert.style.display = "none";
            if (policySearchResults) policySearchResults.style.display = "none";
            if (lookupInitialState) lookupInitialState.style.display = "block";
            btnClearLookup.style.display = "none";
        });
    }

    if (policySearchForm) {
        policySearchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!searchPolicyInput) return;
            const query = searchPolicyInput.value.trim();
            if (!query) return;

            if (policySearchAlert) policySearchAlert.style.display = "none";
            if (policySearchResults) policySearchResults.style.display = "none";
            if (policyResultsList) policyResultsList.innerHTML = "";
            if (lookupInitialState) lookupInitialState.style.display = "none";
            if (btnClearLookup) btnClearLookup.style.display = "inline-flex";

            // Determine search mode: auto, claim_id, or policy
            const modeRadio = document.querySelector('input[name="search-mode"]:checked');
            const mode = modeRadio ? modeRadio.value : "auto";

            const isClaimIdPattern = /^CLM-\d{8}-[A-Za-z0-9]{4}$/i.test(query) || query.toUpperCase().startsWith("CLM-");
            const searchByClaimId = mode === "claim_id" || (mode === "auto" && isClaimIdPattern);

            if (searchByClaimId) {
                // Search by Claim ID
                try {
                    const res = await fetch(`/api/claims/${encodeURIComponent(query)}`);
                    const data = await res.json();

                    if (!res.ok || !data.success) {
                        if (res.status === 401) {
                            openAuthModal("login");
                            showAuthAlert("Authentication required to view this claim.");
                            return;
                        }
                        if (res.status === 403) {
                            showLookupError("Access Restricted: You are not authorized to view claim records belonging to another policyholder.");
                            return;
                        }
                        showLookupError(data.message || `No claim record found matching identifier '${query}'.`);
                        return;
                    }

                    const claim = data.data;
                    if (resultsCount) resultsCount.textContent = "1";
                    if (policyResultsList) {
                        policyResultsList.innerHTML = renderClaimCard(claim);
                        attachCardActionListeners(policyResultsList);
                    }
                    if (policySearchResults) policySearchResults.style.display = "block";

                } catch (err) {
                    showLookupError(`Lookup request failed: ${err.message}`);
                }
            } else {
                // Search by Policy Number
                if (!currentUser) {
                    openAuthModal("login");
                    showAuthAlert("Authentication required to search claims by policy number.");
                    return;
                }

                try {
                    const res = await fetch(`/api/claims/policy/${encodeURIComponent(query)}`);
                    const data = await res.json();

                    if (!res.ok || !data.success) {
                        if (res.status === 401) {
                            openAuthModal("login");
                            showAuthAlert("Authentication required to search claims.");
                            return;
                        }
                        showLookupError(data.message || `No claims found for policy '${query}' under your account.`);
                        return;
                    }

                    if (resultsCount) resultsCount.textContent = data.count || data.claims.length;
                    if (policyResultsList) {
                        policyResultsList.innerHTML = data.claims
                            .map((claim) => renderClaimCard(claim))
                            .join("");
                        attachCardActionListeners(policyResultsList);
                    }
                    if (policySearchResults) policySearchResults.style.display = "block";

                } catch (err) {
                    showLookupError(`Search failed: ${err.message}`);
                }
            }
        });
    }

    function showLookupError(msg) {
        if (!policySearchAlert) return;
        policySearchAlert.textContent = msg;
        policySearchAlert.style.display = "block";
    }

    // -------------------------------------------------------------
    // 9. Section 3: My Submissions
    // -------------------------------------------------------------
    const myClaimsList = document.getElementById("my-claims-list");
    const myClaimsAlert = document.getElementById("my-claims-alert");
    const btnRefreshMyClaims = document.getElementById("btn-refresh-my-claims");
    const myClaimsFilterInput = document.getElementById("myclaims-filter-input");
    const myClaimsSortSelect = document.getElementById("myclaims-sort-select");
    const myClaimsCountDisplay = document.getElementById("myclaims-count-display");

    async function loadMyClaims() {
        if (!myClaimsList) return;
        if (!currentUser) {
            myClaimsList.innerHTML = `
                <div class="empty-state-card">
                    <div class="empty-state-icon-wrapper">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    </div>
                    <h3>Authentication Required</h3>
                    <p>Please sign in to view and manage claims submitted under your account profile.</p>
                    <button type="button" class="btn btn-primary" id="btn-submissions-login">Sign In / Register</button>
                </div>
            `;
            const loginBtn = document.getElementById("btn-submissions-login");
            if (loginBtn) loginBtn.addEventListener("click", () => openAuthModal("login"));
            if (myClaimsCountDisplay) myClaimsCountDisplay.textContent = "0 Submissions";
            return;
        }

        myClaimsList.innerHTML = `
            <div class="empty-state-card">
                <div class="empty-state-icon-wrapper">
                    <span class="spinner-circle" style="width: 24px; height: 24px; border-width: 3px; margin: 0;"></span>
                </div>
                <h3>Loading Submissions...</h3>
                <p>Retrieving your secured claim submissions...</p>
            </div>
        `;
        if (myClaimsAlert) myClaimsAlert.style.display = "none";

        try {
            const res = await fetch("/api/my-claims");
            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.message || "Failed to load claim history.");
            }

            mySubmissionsData = data.claims || [];
            applySubmissionsFilterAndSort();

        } catch (err) {
            if (myClaimsAlert) {
                myClaimsAlert.textContent = `Error loading claims: ${err.message}`;
                myClaimsAlert.style.display = "block";
            }
            myClaimsList.innerHTML = `<p class="empty-state">Could not fetch submissions.</p>`;
        }
    }

    function applySubmissionsFilterAndSort() {
        if (!myClaimsList) return;

        const filterQuery = (myClaimsFilterInput ? myClaimsFilterInput.value : "").trim().toLowerCase();
        const sortOrder = myClaimsSortSelect ? myClaimsSortSelect.value : "newest";

        let filtered = [...mySubmissionsData];

        // Filter
        if (filterQuery) {
            filtered = filtered.filter((c) => {
                const cid = (c.claim_id || "").toLowerCase();
                const pol = (c.policy_number || "").toLowerCase();
                const name = (c.claimant_name || "").toLowerCase();
                const veh = (c.vehicle_number || "").toLowerCase();
                const desc = (c.claim_description || "").toLowerCase();
                const loc = (c.incident_location || "").toLowerCase();
                return cid.includes(filterQuery) ||
                       pol.includes(filterQuery) ||
                       name.includes(filterQuery) ||
                       veh.includes(filterQuery) ||
                       desc.includes(filterQuery) ||
                       loc.includes(filterQuery);
            });
        }

        // Sort
        filtered.sort((a, b) => {
            const timeA = new Date(a.created_at || 0).getTime();
            const timeB = new Date(b.created_at || 0).getTime();
            return sortOrder === "oldest" ? timeA - timeB : timeB - timeA;
        });

        if (myClaimsCountDisplay) {
            myClaimsCountDisplay.textContent = `${filtered.length} of ${mySubmissionsData.length} Submissions`;
        }

        if (filtered.length === 0) {
            if (mySubmissionsData.length === 0) {
                myClaimsList.innerHTML = `
                    <div class="empty-state-card">
                        <div class="empty-state-icon-wrapper">
                            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                        </div>
                        <h3>No Claims Submitted Yet</h3>
                        <p>You haven't submitted any insurance claims under this account. Click below to submit your first claim evidence.</p>
                        <button type="button" class="btn btn-primary" id="btn-submit-first-claim">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                            <span>Submit Claim Evidence</span>
                        </button>
                    </div>
                `;
                const firstBtn = document.getElementById("btn-submit-first-claim");
                if (firstBtn) firstBtn.addEventListener("click", () => switchView("submit"));
            } else {
                myClaimsList.innerHTML = `
                    <div class="empty-state-card">
                        <div class="empty-state-icon-wrapper">
                            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        </div>
                        <h3>No Matching Submissions</h3>
                        <p>No claims match your filter query "<strong>${escapeHtml(filterQuery)}</strong>". Try clearing your search.</p>
                    </div>
                `;
            }
            return;
        }

        myClaimsList.innerHTML = filtered
            .map((claim) => renderClaimCard(claim))
            .join("");
        attachCardActionListeners(myClaimsList);
    }

    if (btnRefreshMyClaims) btnRefreshMyClaims.addEventListener("click", loadMyClaims);

    const btnClearMyClaimsFilter = document.getElementById("btn-clear-myclaims-filter");
    if (myClaimsFilterInput) {
        myClaimsFilterInput.addEventListener("input", () => {
            if (btnClearMyClaimsFilter) {
                btnClearMyClaimsFilter.style.display = myClaimsFilterInput.value ? "flex" : "none";
            }
            applySubmissionsFilterAndSort();
        });
    }

    if (btnClearMyClaimsFilter) {
        btnClearMyClaimsFilter.addEventListener("click", () => {
            if (myClaimsFilterInput) myClaimsFilterInput.value = "";
            btnClearMyClaimsFilter.style.display = "none";
            applySubmissionsFilterAndSort();
        });
    }

    if (myClaimsSortSelect) myClaimsSortSelect.addEventListener("change", applySubmissionsFilterAndSort);

    // -------------------------------------------------------------
    // 10. Modals: Claim Details & Evidence Inspection
    // -------------------------------------------------------------
    const modalClaimDetails = document.getElementById("modal-claim-details");
    const btnCloseDetailsModal = document.getElementById("btn-close-details-modal");
    const btnModalClose = document.getElementById("btn-modal-close");

    const modalClaimEvidence = document.getElementById("modal-claim-evidence");
    const btnCloseEvidenceModal = document.getElementById("btn-close-evidence-modal");
    const btnEvidenceModalClose = document.getElementById("btn-evidence-modal-close");

    let claimDetailsScrollPos = 0;

    function lockClaimDetailsScroll() {
        if (!document.body.classList.contains("modal-open")) {
            claimDetailsScrollPos = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
            document.documentElement.classList.add("modal-open");
            document.body.classList.add("modal-open");
        }
    }

    function unlockClaimDetailsScroll() {
        document.documentElement.classList.remove("modal-open");
        document.body.classList.remove("modal-open");
        const prevBehavior = document.documentElement.style.scrollBehavior;
        document.documentElement.style.scrollBehavior = "auto";
        try {
            window.scrollTo({
                top: claimDetailsScrollPos,
                left: 0,
                behavior: "instant"
            });
        } catch (e) {
            window.scrollTo(0, claimDetailsScrollPos);
        }
        document.documentElement.style.scrollBehavior = prevBehavior;
    }

    function closeClaimDetailsModal() {
        if (modalClaimDetails) modalClaimDetails.style.display = "none";
        unlockClaimDetailsScroll();
    }

    function closeClaimEvidenceModal() {
        if (modalClaimEvidence) modalClaimEvidence.style.display = "none";
    }

    if (btnCloseDetailsModal) btnCloseDetailsModal.addEventListener("click", closeClaimDetailsModal);
    if (btnModalClose) btnModalClose.addEventListener("click", closeClaimDetailsModal);
    if (btnCloseEvidenceModal) btnCloseEvidenceModal.addEventListener("click", closeClaimEvidenceModal);
    if (btnEvidenceModalClose) btnEvidenceModalClose.addEventListener("click", closeClaimEvidenceModal);

    // Close Claim Details modal with Escape key
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" || e.keyCode === 27) {
            if (modalClaimDetails && modalClaimDetails.style.display === "flex") {
                closeClaimDetailsModal();
            }
        }
    });

    async function openClaimDetailsModal(claimId) {
        if (!modalClaimDetails) return;

        lockClaimDetailsScroll();

        const idSpan = document.getElementById("modal-details-id");
        if (idSpan) idSpan.textContent = claimId;

        // Reset details
        document.getElementById("detail-claimant-name").textContent = "Loading...";
        document.getElementById("detail-policy-number").textContent = "Loading...";
        document.getElementById("detail-vehicle-number").textContent = "Loading...";
        document.getElementById("detail-accident-date").textContent = "Loading...";
        document.getElementById("detail-incident-location").textContent = "-";
        document.getElementById("detail-status").textContent = "Loading...";
        document.getElementById("detail-description").textContent = "Loading claim narrative...";

        const btnReceipt = document.getElementById("btn-modal-receipt");
        const btnReport = document.getElementById("btn-modal-report");
        if (btnReceipt) btnReceipt.href = `/api/claims/${claimId}/receipt`;
        if (btnReport) btnReport.href = `/api/claims/${claimId}/document-report`;

        const extractedSection = document.getElementById("modal-extracted-section");
        const extractedRows = document.getElementById("modal-extracted-rows");
        if (extractedSection) extractedSection.style.display = "none";
        if (extractedRows) extractedRows.innerHTML = "";

        modalClaimDetails.style.display = "flex";
        const modalBody = modalClaimDetails.querySelector(".modal-body");
        if (modalBody) modalBody.scrollTop = 0;

        try {
            const res = await fetch(`/api/claims/${claimId}`);
            const json = await res.json();
            if (!res.ok || !json.success) throw new Error(json.message || "Failed to load claim details.");

            const claim = json.data;
            document.getElementById("detail-claimant-name").textContent = claim.claimant_name || "-";
            document.getElementById("detail-policy-number").textContent = claim.policy_number || "-";
            document.getElementById("detail-vehicle-number").textContent = claim.vehicle_number || "-";
            document.getElementById("detail-accident-date").textContent = claim.accident_date || "-";
            document.getElementById("detail-incident-location").textContent = claim.incident_location || "Not specified";
            document.getElementById("detail-status").textContent = claim.status || "SUBMITTED";
            document.getElementById("detail-description").textContent = claim.claim_description || "No narrative provided.";

            // Fetch extracted fields if present (Phase 4 OCR)
            try {
                const extRes = await fetch(`/api/claims/${claimId}/extracted`);
                if (extRes.ok) {
                    const extData = await extRes.json();
                    if (extData.fields && extData.fields.length > 0 && extractedRows && extractedSection) {
                        extractedRows.innerHTML = extData.fields.map((f) => `
                            <tr>
                                <td><strong>${escapeHtml(f.field_name || "-")}</strong></td>
                                <td>${escapeHtml(f.extracted_value || "-")}</td>
                                <td><code>${escapeHtml(f.source_filename || "-")}</code> (p.${f.page_number || 1})</td>
                                <td>${escapeHtml(f.extraction_method || "OCR/Regex")}</td>
                                <td>${f.confidence_score ? (f.confidence_score * 100).toFixed(0) + "%" : "90%"}</td>
                                <td><span class="status-pill status-ready">${escapeHtml(f.field_status || "Consistent")}</span></td>
                            </tr>
                        `).join("");
                        extractedSection.style.display = "block";
                    }
                }
            } catch {
                // optional
            }

            // Phase 5: Load and display AI Vehicle Damage Inspection (CarDD)
            const damageSection = document.getElementById("modal-damage-section");
            const btnAnalyzeDamage = document.getElementById("btn-analyze-damage");
            const btnDamageText = document.getElementById("btn-damage-text");
            const btnDamageSpinner = document.getElementById("btn-damage-spinner");
            const damageStatusBanner = document.getElementById("damage-status-banner");
            const damageVisualContainer = document.getElementById("damage-visual-container");
            const damageOriginalImg = document.getElementById("damage-original-img");
            const damageAnnotatedImg = document.getElementById("damage-annotated-img");
            const damageAnnotatedPlaceholder = document.getElementById("damage-annotated-placeholder");
            const btnDownloadAnnotated = document.getElementById("btn-download-annotated");
            const damageMetricsContainer = document.getElementById("damage-metrics-container");
            const metricDamageCount = document.getElementById("metric-damage-count");
            const metricDamagePeakConf = document.getElementById("metric-damage-peak-conf");
            const metricDamageLatency = document.getElementById("metric-damage-latency");
            const metricDamageModel = document.getElementById("metric-damage-model");
            const damageTableContainer = document.getElementById("damage-table-container");
            const damageDetectionsRows = document.getElementById("damage-detections-rows");
            const damageHistoryContainer = document.getElementById("damage-history-container");
            const damageHistoryList = document.getElementById("damage-history-list");
            const modelBenchmarkSubtitle = document.getElementById("model-benchmark-subtitle");

            if (modelBenchmarkSubtitle) {
                modelBenchmarkSubtitle.innerHTML = "Model: <b>YOLOv8n-CarDD</b> (v1.0) &bull; Dataset: <b>CarDD-300</b> &bull; Precision: <b>31.4%</b> &bull; Recall: <b>34.6%</b> &bull; mAP@50: <b>19.3%</b> &bull; mAP@50-95: <b>12.2%</b>";
            }

            function getPillClass(cat) {
                const c = (cat || "").toLowerCase();
                if (c.includes("dent")) return "damage-dent";
                if (c.includes("scratch")) return "damage-scratch";
                if (c.includes("crack")) return "damage-crack";
                if (c.includes("glass")) return "damage-glass";
                if (c.includes("lamp")) return "damage-lamp";
                if (c.includes("tire")) return "damage-tire";
                return "damage-dent";
            }

            function displayDamageAnalysis(analysis) {
                if (!damageVisualContainer) return;

                if (damageOriginalImg) {
                    damageOriginalImg.src = `/api/claims/${claimId}/evidence/image?t=${Date.now()}`;
                }

                if (analysis && (analysis.total_detections !== undefined || analysis.detections)) {
                    const count = analysis.total_detections !== undefined ? analysis.total_detections : (analysis.detections ? analysis.detections.length : 0);
                    const peak = (analysis.highest_confidence !== undefined ? analysis.highest_confidence : (analysis.max_confidence || 0)) * 100;
                    const latency = analysis.processing_time_ms || analysis.inference_time_ms || 0;

                    if (damageAnnotatedImg) {
                        damageAnnotatedImg.src = `/api/claims/${claimId}/annotated-image?t=${Date.now()}`;
                        damageAnnotatedImg.style.display = "block";
                    }
                    if (damageAnnotatedPlaceholder) damageAnnotatedPlaceholder.style.display = "none";
                    if (btnDownloadAnnotated) {
                        btnDownloadAnnotated.href = `/api/claims/${claimId}/annotated-image?download=1`;
                        btnDownloadAnnotated.style.display = "inline-flex";
                    }

                    if (metricDamageCount) metricDamageCount.textContent = count;
                    if (metricDamagePeakConf) metricDamagePeakConf.textContent = peak.toFixed(1) + "%";
                    if (metricDamageLatency) metricDamageLatency.textContent = latency > 0 ? latency.toFixed(0) + " ms" : "-";
                    if (metricDamageModel) metricDamageModel.textContent = analysis.model_name || "YOLOv8n-CarDD";

                    damageVisualContainer.style.display = "grid";
                    if (damageMetricsContainer) damageMetricsContainer.style.display = "grid";

                    const detections = analysis.detections || [];
                    if (detections.length > 0 && damageDetectionsRows && damageTableContainer) {
                        damageDetectionsRows.innerHTML = detections.map((d, idx) => {
                            const conf = d.confidence ? (d.confidence * 100).toFixed(1) + "%" : "-";
                            const bbox = d.bbox || (d.bbox_x1 !== undefined ? [d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2] : null);
                            const bboxStr = bbox ? `[${bbox.map(v => Math.round(v)).join(", ")}]` : "-";
                            const reg = (d.location_region || d.region || "center").replace(/_/g, " ").toUpperCase();
                            const cat = (d.category || "damage").toUpperCase();
                            const pillCls = getPillClass(d.category);
                            return `
                                <tr>
                                    <td><strong>${d.detection_index || (idx + 1)}</strong></td>
                                    <td><span class="damage-pill ${pillCls}">${escapeHtml(cat)}</span></td>
                                    <td><strong>${escapeHtml(conf)}</strong></td>
                                    <td>${escapeHtml(reg)}</td>
                                    <td><code>${escapeHtml(bboxStr)}</code></td>
                                </tr>
                            `;
                        }).join("");
                        damageTableContainer.style.display = "block";
                    } else if (damageTableContainer) {
                        damageTableContainer.style.display = "none";
                    }

                    if (damageStatusBanner) {
                        damageStatusBanner.className = "damage-banner success mt-2";
                        damageStatusBanner.textContent = `✓ AI Damage Analysis completed: ${count} damage regions localized with YOLOv8n-CarDD (Peak: ${peak.toFixed(1)}%).`;
                        damageStatusBanner.style.display = "block";
                    }
                } else {
                    if (damageAnnotatedImg) damageAnnotatedImg.style.display = "none";
                    if (damageAnnotatedPlaceholder) damageAnnotatedPlaceholder.style.display = "flex";
                    if (btnDownloadAnnotated) btnDownloadAnnotated.style.display = "none";
                    if (damageMetricsContainer) damageMetricsContainer.style.display = "none";
                    if (damageTableContainer) damageTableContainer.style.display = "none";
                    damageVisualContainer.style.display = "grid";

                    if (damageStatusBanner) {
                        damageStatusBanner.className = "damage-banner info mt-2";
                        damageStatusBanner.textContent = 'ℹ Vehicle photograph loaded. Click "Analyze Vehicle Damage" to execute YOLOv8 detection.';
                        damageStatusBanner.style.display = "block";
                    }
                }
            }

            // Wire up analyze button
            if (btnAnalyzeDamage) {
                btnAnalyzeDamage.onclick = async () => {
                    btnAnalyzeDamage.disabled = true;
                    if (btnDamageSpinner) btnDamageSpinner.style.display = "inline-block";
                    if (btnDamageText) btnDamageText.textContent = "Analyzing Damage...";
                    if (damageStatusBanner) {
                        damageStatusBanner.className = "damage-banner info mt-2";
                        damageStatusBanner.textContent = "Running YOLOv8n-CarDD computer vision inference...";
                        damageStatusBanner.style.display = "block";
                    }

                    try {
                        const anRes = await fetch(`/api/claims/${claimId}/analyze-damage`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" }
                        });
                        const anData = await anRes.json();
                        if (!anRes.ok || !anData.success) {
                            throw new Error(anData.message || "Failed to analyze damage.");
                        }
                        displayDamageAnalysis(anData.analysis);
                        loadDamageHistory();
                    } catch (err) {
                        if (damageStatusBanner) {
                            damageStatusBanner.className = "damage-banner danger mt-2";
                            damageStatusBanner.textContent = `Error: ${err.message}`;
                            damageStatusBanner.style.display = "block";
                        }
                    } finally {
                        btnAnalyzeDamage.disabled = false;
                        if (btnDamageSpinner) btnDamageSpinner.style.display = "none";
                        if (btnDamageText) btnDamageText.textContent = "🔍 Analyze Vehicle Damage";
                    }
                };
            }

            async function loadDamageHistory() {
                if (!damageHistoryContainer || !damageHistoryList) return;
                try {
                    const hRes = await fetch(`/api/claims/${claimId}/damage-history`);
                    if (hRes.ok) {
                        const hData = await hRes.json();
                        if (hData.analyses && hData.analyses.length > 0) {
                            damageHistoryList.innerHTML = hData.analyses.map((a, i) => `
                                <span class="history-tag">Run #${hData.analyses.length - i} &bull; ${a.total_detections || 0} damages &bull; ${(a.highest_confidence * 100 || 0).toFixed(1)}% conf &bull; ${Math.round(a.processing_time_ms || 0)}ms</span>
                            `).join("");
                            damageHistoryContainer.style.display = "block";
                        } else {
                            damageHistoryContainer.style.display = "none";
                        }
                    }
                } catch {
                    // optional
                }
            }

            // Initial load of damage analysis
            if (claim.damage_analysis) {
                displayDamageAnalysis(claim.damage_analysis);
            } else {
                try {
                    const daRes = await fetch(`/api/claims/${claimId}/damage-analysis`);
                    if (daRes.ok) {
                        const daData = await daRes.json();
                        if (daData.analysis) {
                            displayDamageAnalysis(daData.analysis);
                        } else {
                            displayDamageAnalysis(null);
                        }
                    } else {
                        displayDamageAnalysis(null);
                    }
                } catch {
                    displayDamageAnalysis(null);
                }
            }

            loadDamageHistory();

            // -------------------------------------------------------------
            // Phase 6: Load and display AI Claim Description Analysis (NLP)
            // -------------------------------------------------------------
            const btnAnalyzeNlp = document.getElementById("btn-analyze-nlp");
            const btnNlpText = document.getElementById("btn-nlp-text");
            const btnNlpSpinner = document.getElementById("btn-nlp-spinner");
            const nlpStatusBanner = document.getElementById("nlp-status-banner");
            const nlpResultsContainer = document.getElementById("nlp-results-container");
            const nlpNarrativeText = document.getElementById("nlp-narrative-text");
            const nlpMetricType = document.getElementById("nlp-metric-type");
            const nlpMetricConfidence = document.getElementById("nlp-metric-confidence");
            const nlpMetricEntities = document.getElementById("nlp-metric-entities");
            const nlpMetricConsistency = document.getElementById("nlp-metric-consistency");
            const nlpEntitiesList = document.getElementById("nlp-entities-list");
            const nlpChronologyBadge = document.getElementById("nlp-chronology-badge");
            const nlpTimelineContainer = document.getElementById("nlp-timeline-container");
            const nlpDamagesRows = document.getElementById("nlp-damages-rows");
            const nlpConsistencyRows = document.getElementById("nlp-consistency-rows");
            const nlpMissingContainer = document.getElementById("nlp-missing-container");
            const nlpMissingList = document.getElementById("nlp-missing-list");

            function displayNlpAnalysis(analysis) {
                if (!nlpResultsContainer) return;

                if (analysis && (analysis.accident_type || analysis.entities || analysis.timeline)) {
                    if (nlpNarrativeText) {
                        nlpNarrativeText.textContent = `"${analysis.original_narrative || claim.claim_description || ""}"`;
                    }
                    if (nlpMetricType) nlpMetricType.textContent = analysis.accident_type || "UNKNOWN";
                    if (nlpMetricConfidence) {
                        const confVal = (analysis.accident_type_confidence || 0) * 100;
                        nlpMetricConfidence.textContent = `${confVal.toFixed(0)}%`;
                    }
                    if (nlpMetricEntities) {
                        nlpMetricEntities.textContent = (analysis.entities ? analysis.entities.length : 0);
                    }
                    if (nlpMetricConsistency) {
                        const consVal = analysis.consistency ? analysis.consistency.consistency_score : 0;
                        nlpMetricConsistency.textContent = `${(consVal || 0)}%`;
                    }

                    // Render Entities
                    if (nlpEntitiesList) {
                        const ents = analysis.entities || [];
                        if (ents.length > 0) {
                            nlpEntitiesList.innerHTML = ents.map((e) => {
                                const t = e.entity_type || "ENTITY";
                                let badgeClass = "badge-location";
                                if (t.includes("ROAD")) badgeClass = "badge-road";
                                else if (t.includes("VEHICLE")) badgeClass = "badge-vehicle";
                                else if (t.includes("OTHER")) badgeClass = "badge-other";
                                else if (t.includes("CLAIMANT")) badgeClass = "badge-claimant";
                                else if (t.includes("DATE") || t.includes("TIME")) badgeClass = "badge-date";
                                else if (t.includes("WEATHER")) badgeClass = "badge-weather";
                                return `<span class="entity-chip"><span class="entity-type-badge ${badgeClass}">${escapeHtml(t)}</span><strong>${escapeHtml(e.text)}</strong></span>`;
                            }).join("");
                        } else {
                            nlpEntitiesList.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">No distinct domain entities found in narrative.</span>`;
                        }
                    }

                    // Render Chronology Timeline
                    if (nlpTimelineContainer) {
                        const steps = analysis.timeline || [];
                        if (steps.length > 0) {
                            nlpTimelineContainer.innerHTML = steps.map((s) => `
                                <div class="timeline-item">
                                    <div class="timeline-step-num">${s.step_number || 1}</div>
                                    <div class="timeline-content">
                                        <div class="timeline-header">
                                            <span class="badge badge-primary">${escapeHtml(s.event_type || "EVENT")}</span>
                                            <span class="timeline-phase">${escapeHtml(s.phase || s.time_reference || "")}</span>
                                        </div>
                                        <div class="timeline-desc">${escapeHtml(s.description || "")}</div>
                                        <div class="timeline-quote">"${escapeHtml(s.supporting_sentence || "")}"</div>
                                    </div>
                                </div>
                            `).join("");
                        } else {
                            nlpTimelineContainer.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted);">No sequential timeline events extracted.</span>`;
                        }
                    }

                    // Render Claimant-Reported Damages
                    if (nlpDamagesRows) {
                        const dmgs = analysis.reported_damages || [];
                        if (dmgs.length > 0) {
                            nlpDamagesRows.innerHTML = dmgs.map((d) => `
                                <tr>
                                    <td><strong>${escapeHtml(d.component || "-")}</strong></td>
                                    <td><span class="badge badge-info">${escapeHtml(d.reported_condition || "Damaged")}</span></td>
                                    <td>${escapeHtml((d.spatial_region || "rear").replace(/_/g, " ").toUpperCase())}</td>
                                    <td><i>"${escapeHtml(d.supporting_sentence || "-")}"</i></td>
                                </tr>
                            `).join("");
                        } else {
                            nlpDamagesRows.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No vehicle damage items mentioned in narrative statement.</td></tr>`;
                        }
                    }

                    // Render Consistency Corroboration
                    if (nlpConsistencyRows) {
                        const comps = (analysis.consistency && analysis.consistency.comparisons) || [];
                        if (comps.length > 0) {
                            nlpConsistencyRows.innerHTML = comps.map((c) => {
                                const st = c.status || "INFO";
                                let pillCls = "status-ready";
                                if (st === "MATCH") pillCls = "status-ready";
                                else if (st === "CONTRADICTORY") pillCls = "status-failed";
                                else if (st === "MISSING_IN_NARRATIVE") pillCls = "status-pending";
                                return `
                                    <tr>
                                        <td><strong>${escapeHtml(c.field || "-")}</strong></td>
                                        <td>${escapeHtml(c.narrative_value || "-")}</td>
                                        <td>${escapeHtml(c.document_value || "-")}<br/><small style="color: var(--text-muted);">${escapeHtml(c.source_document || "")}</small></td>
                                        <td><span class="status-pill ${pillCls}">${escapeHtml(st)}</span></td>
                                        <td>${escapeHtml(c.explanation || "-")}</td>
                                    </tr>
                                `;
                            }).join("");
                        } else {
                            nlpConsistencyRows.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No cross-source comparisons recorded.</td></tr>`;
                        }
                    }

                    // Missing / Ambiguous Notes
                    const missing = analysis.missing_information || [];
                    if (missing.length > 0 && nlpMissingContainer && nlpMissingList) {
                        nlpMissingList.innerHTML = missing.map((m) => `<li>${escapeHtml(m)}</li>`).join("");
                        nlpMissingContainer.style.display = "block";
                    } else if (nlpMissingContainer) {
                        nlpMissingContainer.style.display = "none";
                    }

                    if (nlpStatusBanner) {
                        nlpStatusBanner.className = "damage-banner success mt-2";
                        nlpStatusBanner.textContent = `✓ NLP Claim Narrative Analysis complete: ${analysis.accident_type || 'Accident'} classified with ${analysis.entities ? analysis.entities.length : 0} entities and ${analysis.timeline ? analysis.timeline.length : 0} chronological events.`;
                        nlpStatusBanner.style.display = "block";
                    }

                    nlpResultsContainer.style.display = "block";
                } else {
                    nlpResultsContainer.style.display = "none";
                    if (nlpStatusBanner) {
                        nlpStatusBanner.className = "damage-banner info mt-2";
                        nlpStatusBanner.textContent = 'ℹ Claimant statement ready. Click "Analyze Narrative" to run NLP entity, chronology, and classification extraction.';
                        nlpStatusBanner.style.display = "block";
                    }
                }
            }

            // Wire up NLP analyze button
            if (btnAnalyzeNlp) {
                btnAnalyzeNlp.onclick = async () => {
                    btnAnalyzeNlp.disabled = true;
                    if (btnNlpSpinner) btnNlpSpinner.style.display = "inline-block";
                    if (btnNlpText) btnNlpText.textContent = "Analyzing Narrative...";
                    if (nlpStatusBanner) {
                        nlpStatusBanner.className = "damage-banner info mt-2";
                        nlpStatusBanner.textContent = "Executing NLP entity extraction and event timeline reconstruction...";
                        nlpStatusBanner.style.display = "block";
                    }

                    try {
                        const anRes = await fetch(`/api/claims/${claimId}/analyze-description`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" }
                        });
                        const anData = await anRes.json();
                        if (!anRes.ok || !anData.success) {
                            throw new Error(anData.message || "Failed to analyze claim description.");
                        }
                        displayNlpAnalysis(anData.analysis);
                    } catch (err) {
                        if (nlpStatusBanner) {
                            nlpStatusBanner.className = "damage-banner danger mt-2";
                            nlpStatusBanner.textContent = `Error: ${err.message}`;
                            nlpStatusBanner.style.display = "block";
                        }
                    } finally {
                        btnAnalyzeNlp.disabled = false;
                        if (btnNlpSpinner) btnNlpSpinner.style.display = "none";
                        if (btnNlpText) btnNlpText.textContent = "🔍 Analyze Narrative";
                    }
                };
            }

            // Initial load of NLP analysis
            if (claim.nlp_analysis) {
                displayNlpAnalysis(claim.nlp_analysis);
            } else {
                try {
                    const nlpRes = await fetch(`/api/claims/${claimId}/nlp-analysis`);
                    if (nlpRes.ok) {
                        const nlpData = await nlpRes.json();
                        if (nlpData.analysis) {
                            displayNlpAnalysis(nlpData.analysis);
                        } else {
                            displayNlpAnalysis(null);
                        }
                    } else {
                        displayNlpAnalysis(null);
                    }
                } catch {
                    displayNlpAnalysis(null);
                }
            }

            // =========================================================
            // PHASE 7: Cross-Source Verification Logic
            // =========================================================
            const btnRunVerification = document.getElementById("btn-run-verification");
            const verifPendingBanner = document.getElementById("verif-pending-banner");
            const verifContentContainer = document.getElementById("verif-content-container");
            const verifMetricStatus = document.getElementById("verif-metric-status");
            const verifMetricScore = document.getElementById("verif-metric-score");
            const verifMetricMatched = document.getElementById("verif-metric-matched");
            const verifMetricMismatched = document.getElementById("verif-metric-mismatched");
            const verifMetricMissing = document.getElementById("verif-metric-missing");
            const verifFindingsRows = document.getElementById("verif-findings-rows");
            const verifRecommendationsContainer = document.getElementById("verif-recommendations-container");
            const verifRecommendationsList = document.getElementById("verif-recommendations-list");

            function displayVerificationResults(verif) {
                if (!verif || !verif.total_comparisons) {
                    if (verifPendingBanner) verifPendingBanner.style.display = "block";
                    if (verifContentContainer) verifContentContainer.style.display = "none";
                    return;
                }

                if (verifPendingBanner) verifPendingBanner.style.display = "none";
                if (verifContentContainer) verifContentContainer.style.display = "block";

                // Populate metrics
                if (verifMetricStatus) {
                    verifMetricStatus.textContent = verif.overall_status || "CONSISTENT";
                    if (verif.overall_status === "CONSISTENT") {
                        verifMetricStatus.style.color = "var(--success)";
                    } else if (verif.overall_status === "REVIEW_REQUIRED") {
                        verifMetricStatus.style.color = "var(--danger)";
                    } else {
                        verifMetricStatus.style.color = "var(--warning)";
                    }
                }
                if (verifMetricScore) {
                    const score = verif.consistency_score != null ? Number(verif.consistency_score).toFixed(1) : "100.0";
                    verifMetricScore.textContent = `${score}%`;
                    verifMetricScore.style.color = Number(score) >= 75 ? "var(--success)" : (Number(score) >= 50 ? "var(--warning)" : "var(--danger)");
                }
                if (verifMetricMatched) verifMetricMatched.textContent = verif.matched_comparisons || 0;
                if (verifMetricMismatched) verifMetricMismatched.textContent = verif.mismatched_comparisons || 0;
                if (verifMetricMissing) verifMetricMissing.textContent = verif.missing_evidence_count || 0;

                // Populate findings table
                if (verifFindingsRows) {
                    verifFindingsRows.innerHTML = "";
                    const findings = verif.findings || [];
                    if (findings.length === 0) {
                        verifFindingsRows.innerHTML = `<tr><td colspan="7" class="text-center text-muted p-3">No comparison findings generated.</td></tr>`;
                    } else {
                        findings.forEach(f => {
                            const tr = document.createElement("tr");

                            // Status badge
                            let stClass = "badge-neutral";
                            if (f.comparison_status === "MATCH") stClass = "badge-success";
                            else if (f.comparison_status === "MISMATCH") stClass = "badge-danger";
                            else if (f.comparison_status === "POTENTIAL_DISCREPANCY") stClass = "badge-warning";
                            else if (f.comparison_status === "VISUAL_ONLY_FINDING") stClass = "badge-info";

                            // Severity badge
                            let sevClass = "badge-neutral";
                            if (f.severity === "CRITICAL" || f.severity === "HIGH") sevClass = "badge-danger";
                            else if (f.severity === "MEDIUM") sevClass = "badge-warning";

                            tr.innerHTML = `
                                <td>
                                    <strong>${escapeHtml(f.source_a || '')}</strong><br/>
                                    <small class="text-muted">vs ${escapeHtml(f.source_b || '')}</small>
                                </td>
                                <td>
                                    <strong>${escapeHtml(f.field_name || '')}</strong><br/>
                                    <small class="text-muted monospace">${escapeHtml(f.comparison_id || '')}</small>
                                </td>
                                <td><span style="font-size: 0.85rem;">${escapeHtml(f.original_value_a || '—')}</span></td>
                                <td><span style="font-size: 0.85rem;">${escapeHtml(f.original_value_b || '—')}</span></td>
                                <td><span class="badge ${stClass}">${escapeHtml(f.comparison_status || '')}</span></td>
                                <td><span class="badge ${sevClass}">${escapeHtml(f.severity || '')}</span></td>
                                <td><small>${escapeHtml(f.explanation || '')}</small></td>
                            `;
                            verifFindingsRows.appendChild(tr);
                        });
                    }
                }

                // Recommendations
                if (verifRecommendationsContainer && verifRecommendationsList) {
                    verifRecommendationsList.innerHTML = "";
                    const recs = verif.recommendations || [];
                    if (recs.length > 0) {
                        recs.forEach(r => {
                            const li = document.createElement("li");
                            li.textContent = r;
                            verifRecommendationsList.appendChild(li);
                        });
                        verifRecommendationsContainer.style.display = "block";
                    } else {
                        verifRecommendationsContainer.style.display = "none";
                    }
                }
            }

            // Wire up Run Verification button
            if (btnRunVerification) {
                btnRunVerification.onclick = async () => {
                    btnRunVerification.disabled = true;
                    btnRunVerification.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Verifying...`;

                    try {
                        const vRes = await fetch(`/api/claims/${claimId}/verify-cross-source`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ force: true })
                        });
                        const vData = await vRes.json();
                        if (!vRes.ok || !vData.success) {
                            throw new Error(vData.message || "Failed to execute cross-source verification.");
                        }
                        displayVerificationResults(vData.verification);
                    } catch (err) {
                        if (verifPendingBanner) {
                            verifPendingBanner.className = "damage-banner banner-danger mt-2";
                            verifPendingBanner.textContent = `Verification Error: ${err.message}`;
                            verifPendingBanner.style.display = "block";
                        }
                    } finally {
                        btnRunVerification.disabled = false;
                        btnRunVerification.innerHTML = `<span class="btn-icon">⚡</span> Run Verification`;
                    }
                };
            }

            // Initial load of verification data
            if (claim.verification) {
                displayVerificationResults(claim.verification);
            } else {
                try {
                    const vGet = await fetch(`/api/claims/${claimId}/verification`);
                    if (vGet.ok) {
                        const vJson = await vGet.json();
                        if (vJson.verified && vJson.verification) {
                            displayVerificationResults(vJson.verification);
                        } else {
                            displayVerificationResults(null);
                        }
                    } else {
                        displayVerificationResults(null);
                    }
                } catch {
                    displayVerificationResults(null);
                }
            }

        } catch (err) {
            document.getElementById("detail-description").textContent = `Error: ${err.message}`;
        }
    }

    async function openClaimEvidenceModal(claimId) {
        if (!modalClaimEvidence) return;

        const idSpan = document.getElementById("modal-evidence-id");
        if (idSpan) idSpan.textContent = claimId;

        const evidenceList = document.getElementById("modal-evidence-list");
        if (evidenceList) {
            evidenceList.innerHTML = `<div class="empty-state">Loading evidence packages for ${escapeHtml(claimId)}...</div>`;
        }

        modalClaimEvidence.style.display = "flex";

        try {
            const res = await fetch(`/api/claims/${claimId}`);
            const json = await res.json();
            if (!res.ok || !json.success) throw new Error(json.message || "Failed to load evidence.");

            const claim = json.data;
            const docs = claim.documents || [];
            const imgs = claim.images || [];

            let cardsHtml = "";

            // Helper to get doc
            const findDoc = (type) => docs.find((d) => d.document_type === type);

            const policyDoc = findDoc("POLICY_DOCUMENT") || docs[0];
            const claimFormDoc = findDoc("CLAIM_FORM") || docs[1];
            const invoiceDoc = findDoc("INVOICE") || docs[2];
            const vehicleImg = imgs[0];

            cardsHtml += `
                <div class="evidence-card">
                    <div class="evidence-card-header">
                        <span class="evidence-type-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg></span>
                        <div class="evidence-title-block">
                            <span class="evidence-type-title">Policy Document</span>
                            <span class="evidence-filename">${escapeHtml(policyDoc ? policyDoc.original_filename : "policy_document.pdf")}</span>
                        </div>
                    </div>
                    <div class="evidence-meta-row">
                        <span>Format: <strong>${escapeHtml((policyDoc ? policyDoc.file_extension : "pdf").toUpperCase())}</strong></span>
                        <span>Size: ${formatBytes(policyDoc ? policyDoc.file_size : 124000)}</span>
                    </div>
                    <a href="/api/claims/${claimId}/evidence/policy?download=1" target="_blank" class="btn btn-secondary btn-sm full-width mt-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        <span>Download Document</span>
                    </a>
                </div>

                <div class="evidence-card">
                    <div class="evidence-card-header">
                        <span class="evidence-type-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg></span>
                        <div class="evidence-title-block">
                            <span class="evidence-type-title">Claim Application Form</span>
                            <span class="evidence-filename">${escapeHtml(claimFormDoc ? claimFormDoc.original_filename : "signed_claim_form.pdf")}</span>
                        </div>
                    </div>
                    <div class="evidence-meta-row">
                        <span>Format: <strong>${escapeHtml((claimFormDoc ? claimFormDoc.file_extension : "pdf").toUpperCase())}</strong></span>
                        <span>Size: ${formatBytes(claimFormDoc ? claimFormDoc.file_size : 98000)}</span>
                    </div>
                    <a href="/api/claims/${claimId}/evidence/claim_form?download=1" target="_blank" class="btn btn-secondary btn-sm full-width mt-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        <span>Download Document</span>
                    </a>
                </div>

                <div class="evidence-card">
                    <div class="evidence-card-header">
                        <span class="evidence-type-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg></span>
                        <div class="evidence-title-block">
                            <span class="evidence-type-title">Repair Invoice / Estimate</span>
                            <span class="evidence-filename">${escapeHtml(invoiceDoc ? invoiceDoc.original_filename : "garage_estimate.pdf")}</span>
                        </div>
                    </div>
                    <div class="evidence-meta-row">
                        <span>Format: <strong>${escapeHtml((invoiceDoc ? invoiceDoc.file_extension : "pdf").toUpperCase())}</strong></span>
                        <span>Size: ${formatBytes(invoiceDoc ? invoiceDoc.file_size : 76000)}</span>
                    </div>
                    <a href="/api/claims/${claimId}/evidence/invoice?download=1" target="_blank" class="btn btn-secondary btn-sm full-width mt-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        <span>Download Document</span>
                    </a>
                </div>

                <div class="evidence-card">
                    <div class="evidence-card-header">
                        <span class="evidence-type-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg></span>
                        <div class="evidence-title-block">
                            <span class="evidence-type-title">Vehicle Accident Photo</span>
                            <span class="evidence-filename">${escapeHtml(vehicleImg ? vehicleImg.original_filename : "rear_bumper_damage.jpg")}</span>
                        </div>
                    </div>
                    <div class="evidence-preview-box">
                        <img src="/api/claims/${claimId}/evidence/image" alt="Vehicle Damage Preview" class="evidence-preview-img" onerror="this.style.display='none';">
                    </div>
                    <div class="evidence-meta-row">
                        <span>Format: <strong>${escapeHtml((vehicleImg ? vehicleImg.file_extension : "jpg").toUpperCase())}</strong></span>
                        <span>Size: ${formatBytes(vehicleImg ? vehicleImg.file_size : 245000)}</span>
                    </div>
                    <a href="/api/claims/${claimId}/evidence/image?download=1" target="_blank" class="btn btn-secondary btn-sm full-width mt-2">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        <span>Download Photograph</span>
                    </a>
                </div>
            `;

            if (evidenceList) evidenceList.innerHTML = cardsHtml;

        } catch (err) {
            if (evidenceList) evidenceList.innerHTML = `<div class="empty-state">Error: ${escapeHtml(err.message)}</div>`;
        }
    }

    // -------------------------------------------------------------
    // 11. HTML Escaping Utility (XSS Prevention)
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
}

if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initClaimSenseApp);
    } else {
        initClaimSenseApp();
    }
}
