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
        const label = themeToggleBtn.querySelector(".theme-label");
        if (theme === "dark") {
            if (icon) {
                icon.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
            }
            if (label) label.textContent = "Light";
            themeToggleBtn.setAttribute("title", "Switch to Light Mode");
        } else {
            if (icon) {
                icon.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
            }
            if (label) label.textContent = "Dark";
            themeToggleBtn.setAttribute("title", "Switch to Dark Mode");
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
    // 2. Authentication & Session Management (Phase 3)
    // -------------------------------------------------------------
    const headerAuth = document.getElementById("header-auth");
    const authModal = document.getElementById("auth-modal");
    const btnCloseAuthModal = document.getElementById("btn-close-auth-modal");
    const tabBtnLogin = document.getElementById("tab-btn-login");
    const tabBtnSignup = document.getElementById("tab-btn-signup");
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const authAlert = document.getElementById("auth-alert");
    const linkSwitchToSignup = document.getElementById("link-switch-to-signup");
    const linkSwitchToLogin = document.getElementById("link-switch-to-login");
    const authRequiredNotice = document.getElementById("auth-required-notice");
    const linkSubmissionLogin = document.getElementById("link-submission-login");
    const linkSubmissionSignup = document.getElementById("link-submission-signup");

    function showAuthAlert(msg, isSuccess = false) {
        if (!authAlert) return;
        authAlert.textContent = msg;
        authAlert.className = isSuccess ? "alert alert-success" : "alert alert-error";
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
        authModal.style.display = "flex";
        switchAuthTab(tab);
    }

    function closeAuthModal() {
        if (!authModal) return;
        authModal.style.display = "none";
        clearAuthAlert();
    }

    function switchAuthTab(tab) {
        clearAuthAlert();
        if (tab === "login") {
            tabBtnLogin.classList.add("active");
            tabBtnSignup.classList.remove("active");
            loginForm.style.display = "block";
            signupForm.style.display = "none";
            document.getElementById("modal-title").textContent = "Account Sign In";
        } else {
            tabBtnSignup.classList.add("active");
            tabBtnLogin.classList.remove("active");
            loginForm.style.display = "none";
            signupForm.style.display = "block";
            document.getElementById("modal-title").textContent = "Create New Account";
        }
    }

    if (tabBtnLogin) tabBtnLogin.addEventListener("click", () => switchAuthTab("login"));
    if (tabBtnSignup) tabBtnSignup.addEventListener("click", () => switchAuthTab("signup"));
    if (linkSwitchToSignup) linkSwitchToSignup.addEventListener("click", (e) => { e.preventDefault(); switchAuthTab("signup"); });
    if (linkSwitchToLogin) linkSwitchToLogin.addEventListener("click", (e) => { e.preventDefault(); switchAuthTab("login"); });
    if (btnCloseAuthModal) btnCloseAuthModal.addEventListener("click", closeAuthModal);

    if (linkSubmissionLogin) linkSubmissionLogin.addEventListener("click", (e) => { e.preventDefault(); openAuthModal("login"); });
    if (linkSubmissionSignup) linkSubmissionSignup.addEventListener("click", (e) => { e.preventDefault(); openAuthModal("signup"); });

    window.addEventListener("click", (e) => {
        if (e.target === authModal) closeAuthModal();
    });

    function renderHeaderAuth() {
        if (!headerAuth) return;
        if (currentUser) {
            const safeName = escapeHTML(currentUser.full_name || currentUser.username);
            const safeRole = escapeHTML(currentUser.role || "user");
            headerAuth.innerHTML = `
                <div class="user-badge" id="user-badge">
                    <span class="user-role-pill">${safeRole}</span>
                    <span>${safeName}</span>
                </div>
                <button type="button" id="btn-header-logout" class="btn btn-outline btn-sm">Sign Out</button>
            `;
            const btnLogout = document.getElementById("btn-header-logout");
            if (btnLogout) {
                btnLogout.addEventListener("click", handleLogout);
            }
            if (authRequiredNotice) authRequiredNotice.style.display = "none";
        } else {
            headerAuth.innerHTML = `
                <button type="button" id="btn-open-login" class="btn btn-secondary btn-sm">Sign In</button>
                <button type="button" id="btn-open-signup" class="btn btn-primary btn-sm">Sign Up</button>
            `;
            const btnLogin = document.getElementById("btn-open-login");
            const btnSignup = document.getElementById("btn-open-signup");
            if (btnLogin) btnLogin.addEventListener("click", () => openAuthModal("login"));
            if (btnSignup) btnSignup.addEventListener("click", () => openAuthModal("signup"));
            if (authRequiredNotice) authRequiredNotice.style.display = "block";
        }
    }

    async function checkCurrentSession() {
        try {
            const res = await fetch("/api/auth/me");
            if (res.ok) {
                const data = await res.json();
                currentUser = data.user;
            } else {
                currentUser = null;
            }
        } catch {
            currentUser = null;
        }
        renderHeaderAuth();
    }
    checkCurrentSession();

    // Login Form Submit
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();
            const identifier = document.getElementById("login-identifier").value.trim();
            const password = document.getElementById("login-password").value;

            try {
                const headers = { "Content-Type": "application/json" };
                if (csrfToken) headers["X-CSRFToken"] = csrfToken;

                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({ identifier, password }),
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Invalid credentials.");
                }

                currentUser = data.user;
                renderHeaderAuth();
                closeAuthModal();
                loginForm.reset();
                await fetchCsrfToken(); // Refresh CSRF token for new session

                if (activeView === "myclaims") {
                    loadMyClaims();
                }
            } catch (err) {
                showAuthAlert(err.message);
            }
        });
    }

    // Signup Form Submit
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();
            const fullName = document.getElementById("signup-fullname").value.trim();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value;
            const confirm = document.getElementById("signup-confirm").value;

            try {
                const headers = { "Content-Type": "application/json" };
                if (csrfToken) headers["X-CSRFToken"] = csrfToken;

                const res = await fetch("/api/auth/signup", {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify({
                        full_name: fullName,
                        username: username,
                        email: email,
                        password: password,
                        confirm_password: confirm,
                    }),
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Registration failed.");
                }

                signupForm.reset();
                switchAuthTab("login");
                showAuthAlert("Registration successful! Please sign in with your credentials.", true);
            } catch (err) {
                showAuthAlert(err.message);
            }
        });
    }

    async function handleLogout() {
        try {
            const headers = {};
            if (csrfToken) headers["X-CSRFToken"] = csrfToken;
            await fetch("/api/auth/logout", { method: "POST", headers: headers });
        } catch {
            // ignore network err
        }
        currentUser = null;
        renderHeaderAuth();
        await fetchCsrfToken(); // Refresh CSRF token for anonymous session
        if (activeView === "myclaims") {
            switchView("submit");
        }
    }

    // -------------------------------------------------------------
    // 3. Navigation View Switching (Phase 3)
    // -------------------------------------------------------------
    let activeView = "submit";
    const pillSubmit = document.getElementById("pill-nav-submit");
    const pillSearch = document.getElementById("pill-nav-search");
    const pillMyClaims = document.getElementById("pill-nav-myclaims");

    const submissionCard = document.getElementById("submission-card");
    const policyLookupCard = document.getElementById("policy-lookup-card");
    const myClaimsCard = document.getElementById("my-claims-card");
    const successCard = document.getElementById("submission-success-card");

    function switchView(viewName) {
        activeView = viewName;
        [pillSubmit, pillSearch, pillMyClaims].forEach((p) => p && p.classList.remove("active"));
        if (submissionCard) submissionCard.style.display = "none";
        if (policyLookupCard) policyLookupCard.style.display = "none";
        if (myClaimsCard) myClaimsCard.style.display = "none";
        if (successCard) successCard.style.display = "none";

        if (viewName === "submit") {
            if (pillSubmit) pillSubmit.classList.add("active");
            if (submissionCard) submissionCard.style.display = "block";
        } else if (viewName === "search") {
            if (pillSearch) pillSearch.classList.add("active");
            if (policyLookupCard) policyLookupCard.style.display = "block";
        } else if (viewName === "myclaims") {
            if (pillMyClaims) pillMyClaims.classList.add("active");
            if (myClaimsCard) myClaimsCard.style.display = "block";
            loadMyClaims();
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
    // 4. Policy Number Claim Lookup (Phase 3)
    // -------------------------------------------------------------
    const policySearchForm = document.getElementById("policy-search-form");
    const searchPolicyInput = document.getElementById("search-policy-input");
    const policySearchAlert = document.getElementById("policy-search-alert");
    const policySearchResults = document.getElementById("policy-search-results");
    const policyResultsList = document.getElementById("policy-results-list");
    const resultsCount = document.getElementById("results-count");

    if (policySearchForm) {
        policySearchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!searchPolicyInput) return;
            const policyNum = searchPolicyInput.value.trim();
            if (!policyNum) return;

            policySearchAlert.style.display = "none";
            policySearchResults.style.display = "none";
            policyResultsList.innerHTML = "";

            if (!currentUser) {
                openAuthModal("login");
                showAuthAlert("Authentication required to search claims by policy number.");
                return;
            }

            try {
                const res = await fetch(`/api/claims/policy/${encodeURIComponent(policyNum)}`);
                const data = await res.json();

                if (!res.ok || !data.success) {
                    policySearchAlert.textContent = data.message || `No claims found for policy '${policyNum}'.`;
                    policySearchAlert.style.display = "block";
                    return;
                }

                resultsCount.textContent = data.count || data.claims.length;
                policyResultsList.innerHTML = data.claims
                    .map((claim) => renderClaimCard(claim))
                    .join("");
                policySearchResults.style.display = "block";
            } catch (err) {
                policySearchAlert.textContent = `Search failed: ${err.message}`;
                policySearchAlert.style.display = "block";
            }
        });
    }

    function renderClaimCard(claim) {
        const safeClaimId = escapeHTML(claim.claim_id);
        const safeStatus = escapeHTML(claim.status || "SUBMITTED");
        const safePolicy = escapeHTML(claim.policy_number);
        const safeClaimant = escapeHTML(claim.claimant_name);
        const safeVehicle = escapeHTML(claim.vehicle_number);
        const safeAccidentDate = escapeHTML(claim.accident_date);
        const dateStr = claim.created_at ? escapeHTML(new Date(claim.created_at).toLocaleDateString()) : "-";
        const filesCount = claim.files_count || (claim.documents ? claim.documents.length + (claim.images ? claim.images.length : 0) : 4);

        return `
            <div class="claim-result-card">
                <div class="result-info">
                    <div class="result-title-line">
                        <span class="result-claim-id">${safeClaimId}</span>
                        <span class="status-pill status-ready">${safeStatus}</span>
                    </div>
                    <div class="result-meta-line">
                        <span><strong>Policy:</strong> ${safePolicy}</span>
                        <span><strong>Claimant:</strong> ${safeClaimant}</span>
                        <span><strong>Vehicle:</strong> ${safeVehicle}</span>
                        <span><strong>Accident Date:</strong> ${safeAccidentDate}</span>
                        <span><strong>Submitted:</strong> ${dateStr}</span>
                        <span><strong>Evidence:</strong> ${filesCount} files</span>
                    </div>
                </div>
                <div class="result-actions">
                    <a href="/api/claims/${safeClaimId}/receipt" target="_blank" class="btn btn-secondary btn-sm" title="Download Official Submission Receipt (PDF)">
                        📄 Download Receipt (PDF)
                    </a>
                </div>
            </div>
        `;
    }

    // -------------------------------------------------------------
    // 5. My Registered Claims (Phase 3)
    // -------------------------------------------------------------
    const myClaimsList = document.getElementById("my-claims-list");
    const myClaimsAlert = document.getElementById("my-claims-alert");
    const btnRefreshMyClaims = document.getElementById("btn-refresh-my-claims");

    async function loadMyClaims() {
        if (!myClaimsList) return;
        if (!currentUser) {
            myClaimsList.innerHTML = `<p class="empty-state">Please <a href="#" id="link-login-now">sign in</a> to view your registered claims.</p>`;
            const linkLoginNow = document.getElementById("link-login-now");
            if (linkLoginNow) linkLoginNow.addEventListener("click", (e) => { e.preventDefault(); openAuthModal("login"); });
            return;
        }

        myClaimsList.innerHTML = `<p class="empty-state">Loading your registered claims...</p>`;
        if (myClaimsAlert) myClaimsAlert.style.display = "none";

        try {
            const res = await fetch("/api/my-claims");
            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.message || "Failed to load claim history.");
            }

            if (!data.claims || data.claims.length === 0) {
                myClaimsList.innerHTML = `<p class="empty-state">No claims registered under this account yet. Click "Submit Claim Evidence" to create one.</p>`;
                return;
            }

            myClaimsList.innerHTML = data.claims
                .map((claim) => renderClaimCard(claim))
                .join("");
        } catch (err) {
            if (myClaimsAlert) {
                myClaimsAlert.textContent = `Error loading claims: ${err.message}`;
                myClaimsAlert.style.display = "block";
            }
            myClaimsList.innerHTML = `<p class="empty-state">Could not fetch claims.</p>`;
        }
    }

    if (btnRefreshMyClaims) {
        btnRefreshMyClaims.addEventListener("click", loadMyClaims);
    }

    // -------------------------------------------------------------
    // 6. Claim Submission Handling (Phase 2 & 3)
    // -------------------------------------------------------------
    const claimForm = document.getElementById("claim-form");
    const formErrorAlert = document.getElementById("form-error-alert");
    const btnSubmitClaim = document.getElementById("btn-submit-claim");
    const btnText = btnSubmitClaim ? btnSubmitClaim.querySelector(".btn-text") : null;
    const btnSpinner = btnSubmitClaim ? btnSubmitClaim.querySelector(".btn-spinner") : null;

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

            // Authentication verification check before submission
            if (!currentUser) {
                showError("Authentication Required: You must be signed in with an active account to submit an insurance claim.");
                openAuthModal("login");
                showAuthAlert("Please sign in or create an account to proceed with claim submission.");
                return;
            }

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
                const headers = {};
                if (csrfToken) headers["X-CSRFToken"] = csrfToken;

                const response = await fetch("/api/claims", {
                    method: "POST",
                    headers: headers,
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
