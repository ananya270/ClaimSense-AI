/**
<<<<<<< HEAD
 * ClaimSense AI - Frontend Controller (Hardened)
 * Phase 1, 2 & 3: Health Monitoring, Claim Submission, Authentication,
 *                 Policy Claim Lookup, CSRF Token Handling, XSS Sanitization,
 *                 and Official PDF Receipt Engine.
=======
 * ClaimSense AI - Frontend Controller
 * Three-Section Architecture:
 *   1. Submit Claim Evidence (Form, multi-source uploads, real-time validation, receipt & report access)
 *   2. Policy Claim Lookup (Search by Claim ID or Policy Number, access control, details & evidence modals)
 *   3. My Submissions (User claim history, live filtering, sorting, empty states)
>>>>>>> 772aeb2 (Phase 4)
 */

document.addEventListener("DOMContentLoaded", () => {
    let currentUser = null;
<<<<<<< HEAD
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
=======
    let currentActiveClaimId = null;
    let mySubmissionsData = [];
>>>>>>> 772aeb2 (Phase 4)

    // -------------------------------------------------------------
    // 1. Lightweight Backend Health Monitor (Header Status)
    // -------------------------------------------------------------
    const statusIndicator = document.getElementById("status-indicator");
    const statusBadge = document.getElementById("status-badge");

    async function checkBackendHealth() {
        if (statusIndicator) statusIndicator.className = "status-indicator";
        if (statusBadge) statusBadge.textContent = "Checking...";

        try {
            const response = await fetch("/api/health");
            if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
            const data = await response.json();
            if (statusIndicator) statusIndicator.className = "status-indicator connected";
            if (statusBadge) statusBadge.textContent = "Backend Connected";
<<<<<<< HEAD
            if (healthStatus) {
                healthStatus.textContent = `${escapeHTML(data.status).toUpperCase()} (HTTP 200)`;
                healthStatus.style.color = "var(--success)";
            }
            if (healthPhase) healthPhase.textContent = data.phase || "Active";
            if (healthVersion) healthVersion.textContent = data.version || "1.0.0";
            if (healthEnv) healthEnv.textContent = data.environment || "development";
            if (healthTimestamp) healthTimestamp.textContent = new Date(data.timestamp).toLocaleString();
=======
>>>>>>> 772aeb2 (Phase 4)
        } catch (err) {
            if (statusIndicator) statusIndicator.className = "status-indicator error";
            if (statusBadge) statusBadge.textContent = "Backend Offline";
        }
    }
    checkBackendHealth();

    // -------------------------------------------------------------
    // 2. Dual-Theme Switcher (Dark Navy Default & Light)
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById("theme-toggle");

    function getPreferredTheme() {
        return localStorage.getItem("claimsense-theme") || "dark";
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
<<<<<<< HEAD
            themeToggleBtn.setAttribute("aria-label", "Switch to Light Mode");
=======
            themeToggleBtn.setAttribute("title", "Switch to Light Theme");
>>>>>>> 772aeb2 (Phase 4)
        } else {
            if (icon) {
                icon.innerHTML = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
            }
            if (label) label.textContent = "Dark";
<<<<<<< HEAD
            themeToggleBtn.setAttribute("aria-label", "Switch to Dark Mode");
=======
            themeToggleBtn.setAttribute("title", "Switch to Dark Theme");
>>>>>>> 772aeb2 (Phase 4)
        }
    }

    applyTheme(getPreferredTheme());

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "dark";
            const next = current === "dark" ? "light" : "dark";
            applyTheme(next);
        });
    }

    // -------------------------------------------------------------
<<<<<<< HEAD
    // 2. Authentication & User Session Management (Phase 3)
=======
    // 3. User Authentication & Session Management
>>>>>>> 772aeb2 (Phase 4)
    // -------------------------------------------------------------
    const authLoggedOut = document.getElementById("auth-logged-out");
    const authLoggedIn = document.getElementById("auth-logged-in");
    const authUsernameSpan = document.getElementById("auth-username");
    const authRoleBadge = document.getElementById("auth-role-badge");
    const btnOpenLogin = document.getElementById("btn-open-login") || document.getElementById("btn-nav-login");
    const btnOpenSignup = document.getElementById("btn-open-signup") || document.getElementById("btn-nav-signup");
    const btnLogout = document.getElementById("btn-logout");
    const authNotice = document.getElementById("auth-required-notice");
    const linkSubmissionLogin = document.getElementById("link-submission-login");
    const linkSubmissionSignup = document.getElementById("link-submission-signup");

    // Modal elements
    const authModal = document.getElementById("auth-modal");
    const authModalTitle = document.getElementById("auth-modal-title") || document.getElementById("modal-title");
    const authModalClose = document.getElementById("auth-modal-close") || document.getElementById("btn-close-auth-modal");
    const tabLogin = document.getElementById("tab-login") || document.getElementById("tab-btn-login");
    const tabSignup = document.getElementById("tab-signup") || document.getElementById("tab-btn-signup");
    const formLogin = document.getElementById("form-login") || document.getElementById("login-form");
    const formSignup = document.getElementById("form-signup") || document.getElementById("signup-form");
    const authModalError = document.getElementById("auth-modal-error") || document.getElementById("auth-alert");
    const btnModalSwitchSignup = document.getElementById("btn-modal-switch-signup") || document.getElementById("link-switch-to-signup");
    const btnModalSwitchLogin = document.getElementById("btn-modal-switch-login") || document.getElementById("link-switch-to-login");

    function renderHeaderAuth(user) {
        currentUser = user;
        if (user) {
            if (authLoggedOut) authLoggedOut.style.display = "none";
            if (authLoggedIn) authLoggedIn.style.display = "flex";
            if (authUsernameSpan) authUsernameSpan.textContent = escapeHTML(user.full_name || user.username);
            if (authRoleBadge) {
                authRoleBadge.textContent = escapeHTML((user.role || "user").toUpperCase());
                authRoleBadge.className = "user-role-pill";
            }
            if (authNotice) authNotice.style.display = "none";
        } else {
            if (authLoggedOut) authLoggedOut.style.display = "flex";
            if (authLoggedIn) authLoggedIn.style.display = "none";
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
            authModalError.className = "alert alert-error";
        }
        if (mode === "login") {
            if (tabLogin) tabLogin.classList.add("active");
            if (tabSignup) tabSignup.classList.remove("active");
            if (formLogin) formLogin.style.display = "block";
            if (formSignup) formSignup.style.display = "none";
            if (authModalTitle) authModalTitle.textContent = "Sign In to ClaimSense";
            const idInput = document.getElementById("login-identifier");
            if (idInput) idInput.focus();
        } else {
            if (tabSignup) tabSignup.classList.add("active");
            if (tabLogin) tabLogin.classList.remove("active");
            if (formSignup) formSignup.style.display = "block";
            if (formLogin) formLogin.style.display = "none";
            if (authModalTitle) authModalTitle.textContent = "Create an Account";
            const nameInput = document.getElementById("signup-fullname");
            if (nameInput) nameInput.focus();
        }
    }

    function closeAuthModal() {
        if (!authModal) return;
        authModal.style.display = "none";
<<<<<<< HEAD
        if (formLogin) formLogin.reset();
        if (formSignup) formSignup.reset();
        if (authModalError) {
            authModalError.style.display = "none";
            authModalError.textContent = "";
=======
        clearAuthAlert();
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
>>>>>>> 772aeb2 (Phase 4)
        }
    }

    if (btnOpenLogin) btnOpenLogin.addEventListener("click", () => showAuthModal("login"));
    if (btnOpenSignup) btnOpenSignup.addEventListener("click", () => showAuthModal("signup"));
    if (authModalClose) authModalClose.addEventListener("click", closeAuthModal);

<<<<<<< HEAD
    if (btnModalSwitchSignup) {
        btnModalSwitchSignup.addEventListener("click", (e) => {
            e.preventDefault();
            showAuthModal("signup");
        });
    }
    if (btnModalSwitchLogin) {
        btnModalSwitchLogin.addEventListener("click", (e) => {
            e.preventDefault();
            showAuthModal("login");
        });
=======
    window.addEventListener("click", (e) => {
        if (e.target === authModal) closeAuthModal();
        if (e.target === modalClaimDetails) closeClaimDetailsModal();
        if (e.target === modalClaimEvidence) closeClaimEvidenceModal();
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
                <button type="button" id="btn-open-login" class="btn btn-secondary btn-sm">Sign In</button>
                <button type="button" id="btn-open-signup" class="btn btn-primary btn-sm">Register</button>
            `;
            const btnLogin = document.getElementById("btn-open-login");
            const btnSignup = document.getElementById("btn-open-signup");
            if (btnLogin) btnLogin.addEventListener("click", () => openAuthModal("login"));
            if (btnSignup) btnSignup.addEventListener("click", () => openAuthModal("signup"));
        }
>>>>>>> 772aeb2 (Phase 4)
    }

    if (tabLogin) tabLogin.addEventListener("click", () => showAuthModal("login"));
    if (tabSignup) tabSignup.addEventListener("click", () => showAuthModal("signup"));

    if (authModal) {
        authModal.addEventListener("click", (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }

    if (linkSubmissionLogin) {
        linkSubmissionLogin.addEventListener("click", (e) => {
            e.preventDefault();
            showAuthModal("login");
        });
    }
    if (linkSubmissionSignup) {
        linkSubmissionSignup.addEventListener("click", (e) => {
            e.preventDefault();
            showAuthModal("signup");
        });
    }

<<<<<<< HEAD
    // Login Form Submit
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
=======
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
>>>>>>> 772aeb2 (Phase 4)
            e.preventDefault();
            const idInput = document.getElementById("login-identifier");
            const passInput = document.getElementById("login-password");
            const identifier = idInput ? idInput.value.trim() : "";
            const password = passInput ? passInput.value : "";

            if (!identifier || !password) {
                if (authModalError) {
                    authModalError.textContent = "Please enter both identifier and password.";
                    authModalError.className = "alert alert-error";
                    authModalError.style.display = "block";
                }
                return;
            }

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
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Failed to log in.");
                }

                renderHeaderAuth(data.user);
                closeAuthModal();
                fetchCsrfToken(); // refresh token after session rotation

<<<<<<< HEAD
                if (activeView === "myclaims") {
=======
                if (activeSection === "myclaims") {
>>>>>>> 772aeb2 (Phase 4)
                    loadMyClaims();
                }
            } catch (err) {
                if (authModalError) {
                    authModalError.textContent = err.message;
                    authModalError.className = "alert alert-error";
                    authModalError.style.display = "block";
                }
            }
        });
    }

<<<<<<< HEAD
    // Signup Form Submit
    if (formSignup) {
        formSignup.addEventListener("submit", async (e) => {
=======
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
>>>>>>> 772aeb2 (Phase 4)
            e.preventDefault();
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

            if (password.length < 8 || !/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
                if (authModalError) {
                    authModalError.textContent = "Password must be at least 8 characters and include both letters and numbers.";
                    authModalError.className = "alert alert-error";
                    authModalError.style.display = "block";
                }
                return;
            }

            if (password !== confirm_password) {
                if (authModalError) {
                    authModalError.textContent = "Passwords do not match.";
                    authModalError.className = "alert alert-error";
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
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Registration failed.");
                }

                // Automatically attempt login
                try {
                    const loginRes = await fetch("/api/auth/login", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
                        },
                        body: JSON.stringify({ identifier: username, password }),
                    });
                    const loginData = await loginRes.json();
                    if (loginRes.ok && loginData.success) {
                        renderHeaderAuth(loginData.user);
                        closeAuthModal();
                        fetchCsrfToken();
                        if (activeView === "myclaims") {
                            loadMyClaims();
                        }
                        return;
                    }
                } catch {
                    // Fall back to login notice below
                }

                showAuthModal("login");
                if (authModalError) {
                    authModalError.textContent = "Registration successful! Please sign in with your credentials.";
                    authModalError.className = "alert alert-success";
                    authModalError.style.display = "block";
                }
                fetchCsrfToken();
            } catch (err) {
                if (authModalError) {
                    authModalError.textContent = err.message;
                    authModalError.className = "alert alert-error";
                    authModalError.style.display = "block";
                }
            }
        });
    }

<<<<<<< HEAD
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
                if (activeView === "myclaims") {
                    switchView("submit");
                }
            }
        });
=======
    async function handleLogout() {
        try {
            await fetch("/api/auth/logout", { method: "POST" });
        } catch {
            // ignore network err
        }
        currentUser = null;
        renderHeaderAuth();
        if (activeSection === "myclaims") {
            switchView("submit");
        }
>>>>>>> 772aeb2 (Phase 4)
    }

    // -------------------------------------------------------------
    // 4. Three Independent Navigation Sections
    // -------------------------------------------------------------
    let activeSection = "submit";
    const pillSubmit = document.getElementById("pill-nav-submit");
    const pillSearch = document.getElementById("pill-nav-search");
    const pillMyClaims = document.getElementById("pill-nav-myclaims");

    const sectionSubmit = document.getElementById("section-submit");
    const sectionLookup = document.getElementById("section-lookup");
    const sectionMyClaims = document.getElementById("section-myclaims");

    const submissionCard = document.getElementById("submission-card");
<<<<<<< HEAD
    const policyLookupCard = document.getElementById("policy-lookup-card");
    const myClaimsCard = document.getElementById("my-claims-card");
    const successCard = document.getElementById("submission-success-card") || document.getElementById("success-card");
=======
    const successCard = document.getElementById("submission-success-card");
>>>>>>> 772aeb2 (Phase 4)

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
            loadMyClaims();
        }
    }

    if (pillSubmit) pillSubmit.addEventListener("click", () => switchView("submit"));
    if (pillSearch) pillSearch.addEventListener("click", () => switchView("search"));
    if (pillMyClaims) pillMyClaims.addEventListener("click", () => {
        if (!currentUser) {
            showAuthModal("login");
            if (authModalError) {
                authModalError.textContent = "Please sign in to view your submitted claims.";
                authModalError.className = "alert alert-error";
                authModalError.style.display = "block";
            }
            return;
        }
        switchView("myclaims");
    });

    // -------------------------------------------------------------
    // 5. Selected Filenames Badges & Size Formatting
    // -------------------------------------------------------------
<<<<<<< HEAD
    const formPolicySearch = document.getElementById("policy-search-form") || document.getElementById("form-policy-search");
    const inputPolicySearch = document.getElementById("search-policy-input") || document.getElementById("input-policy-search");
    const policySearchAlert = document.getElementById("policy-search-alert");
    const policySearchResults = document.getElementById("policy-search-results");
    const policyResultsList = document.getElementById("policy-results-list");
    const resultsCount = document.getElementById("results-count");

    if (formPolicySearch) {
        formPolicySearch.addEventListener("submit", async (e) => {
            e.preventDefault();
            const policyNo = inputPolicySearch ? inputPolicySearch.value.trim() : "";
            if (!policyNo) return;

            if (policySearchAlert) policySearchAlert.style.display = "none";
            if (policySearchResults) policySearchResults.style.display = "none";
            if (policyResultsList) policyResultsList.innerHTML = `<div class="loading-spinner">Searching claims for policy '${escapeHTML(policyNo)}'...</div>`;

            if (!currentUser) {
                showAuthModal("login");
                if (authModalError) {
                    authModalError.textContent = "Authentication required to search claims by policy number.";
                    authModalError.className = "alert alert-error";
                    authModalError.style.display = "block";
                }
                return;
            }

            try {
                const res = await fetch(`/api/claims/policy/${encodeURIComponent(policyNo)}`);
                const data = await res.json();

                if (!res.ok || !data.success) {
                    throw new Error(data.message || `No claims found for policy '${policyNo}'`);
                }

                if (resultsCount) resultsCount.textContent = data.count || (data.claims ? data.claims.length : 0);
                renderClaimResults(data.claims, policyResultsList);
                if (policySearchResults) policySearchResults.style.display = "block";
            } catch (err) {
                if (policySearchAlert) {
                    policySearchAlert.textContent = err.message;
                    policySearchAlert.style.display = "block";
                }
=======
    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }

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
>>>>>>> 772aeb2 (Phase 4)
            }
        });
    }

<<<<<<< HEAD
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
            if (linkLoginNow) {
                linkLoginNow.addEventListener("click", (e) => {
                    e.preventDefault();
                    showAuthModal("login");
                });
            }
            return;
        }

        myClaimsList.innerHTML = `<div class="loading-spinner">Loading your registered claims...</div>`;
        if (myClaimsAlert) myClaimsAlert.style.display = "none";

        try {
            const res = await fetch("/api/my-claims");
            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.message || "Failed to load claim history.");
            }

            renderClaimResults(data.claims, myClaimsList);
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

    function renderClaimResults(claims, container) {
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
            const dateStr = claim.created_at ? new Date(claim.created_at).toLocaleDateString() : "-";
            const docCount = claim.files_count || (claim.documents ? claim.documents.length + (claim.images ? claim.images.length : 0) : (claim.files ? Object.keys(claim.files).length : 4));
            html += `
                <div class="claim-result-card">
                    <div class="result-info">
                        <div class="result-title-line">
                            <span class="result-claim-id">${escapeHTML(claim.claim_id)}</span>
                            <span class="status-pill status-ready">${escapeHTML(claim.status || "SUBMITTED")}</span>
                        </div>
                        <div class="result-meta-line">
                            <span><strong>Policy:</strong> ${escapeHTML(claim.policy_number)}</span>
                            <span><strong>Claimant:</strong> ${escapeHTML(claim.claimant_name)}</span>
                            <span><strong>Vehicle:</strong> ${escapeHTML(claim.vehicle_number)}</span>
                            <span><strong>Accident Date:</strong> ${escapeHTML(claim.accident_date)}</span>
                            <span><strong>Submitted:</strong> ${escapeHTML(dateStr)}</span>
                            <span><strong>Evidence:</strong> ${docCount} files</span>
                        </div>
                        ${claim.claim_description ? `<div class="claim-card-desc" style="margin-top: 8px; font-size: 0.85rem; color: var(--text-secondary);">${escapeHTML(claim.claim_description)}</div>` : ""}
                    </div>
                    <div class="result-actions" style="margin-top: 10px; display: flex; gap: 8px; align-items: center;">
                        <a href="/api/claims/${encodeURIComponent(claim.claim_id)}/receipt" target="_blank" class="btn btn-secondary btn-sm" title="Download Official Submission Receipt (PDF)">
                            📄 Download Receipt (PDF)
                        </a>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // -------------------------------------------------------------
    // 6. File Upload Previews & Drag-and-Drop
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
    // 7. Claim Submission Form (Phase 2 & 3)
=======
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
>>>>>>> 772aeb2 (Phase 4)
    // -------------------------------------------------------------
    const claimForm = document.getElementById("claim-form");
    const btnSubmit = document.getElementById("btn-submit-claim");
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
<<<<<<< HEAD
        if (!btnSubmit) return;
        btnSubmit.disabled = isSubmitting;
        const btnText = btnSubmit.querySelector(".btn-text");
        const btnSpinner = btnSubmit.querySelector(".btn-spinner");
        if (btnText) btnText.textContent = isSubmitting ? "Validating & Submitting..." : "Submit Claim for Verification";
        if (btnSpinner) btnSpinner.style.display = isSubmitting ? "inline-block" : "none";
=======
        if (!btnSubmitClaim) return;
        btnSubmitClaim.disabled = isSubmitting;
        if (btnText && btnSpinner) {
            btnText.style.display = isSubmitting ? "none" : "inline";
            btnSpinner.style.display = isSubmitting ? "inline-flex" : "none";
        }
>>>>>>> 772aeb2 (Phase 4)
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

<<<<<<< HEAD
            // Client-side validation
            const claimantName = document.getElementById("claimant_name")?.value.trim();
            const policyNumber = document.getElementById("policy_number")?.value.trim();
            const vehicleNumber = document.getElementById("vehicle_number")?.value.trim();
            const accidentDate = document.getElementById("accident_date")?.value.trim();
            const claimDesc = document.getElementById("claim_description")?.value.trim();
=======
            // Client-side required fields check
            const claimantName = formData.get("claimant_name");
            const policyNumber = formData.get("policy_number");
            const vehicleNumber = formData.get("vehicle_number");
            const accidentDate = formData.get("accident_date");
            const claimDesc = formData.get("claim_description");
>>>>>>> 772aeb2 (Phase 4)

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

<<<<<<< HEAD
                // Render success details
                if (resClaimId) resClaimId.textContent = result.claim_id;
                if (resClaimantName) resClaimantName.textContent = result.data.claimant_name;
                if (resPolicyNumber) resPolicyNumber.textContent = result.data.policy_number;
                if (resVehicleNumber) resVehicleNumber.textContent = result.data.vehicle_number;
                if (resAccidentDate) resAccidentDate.textContent = result.data.accident_date;
                if (resClaimDescription) resClaimDescription.textContent = result.data.claim_description;
                if (resFileCount) resFileCount.textContent = `${result.data.files_count || 4} evidence files safely saved`;
                if (resTimestamp) resTimestamp.textContent = new Date(result.data.created_at).toLocaleString();
=======
                // Populate success summary
                resClaimId.textContent = result.claim_id;
                resClaimantName.textContent = result.data.claimant_name || "-";
                resPolicyNumber.textContent = result.data.policy_number || "-";
                resVehicleNumber.textContent = result.data.vehicle_number || "-";
                resAccidentDate.textContent = result.data.accident_date || "-";
                if (resIncidentLocation) {
                    resIncidentLocation.textContent = result.data.incident_location || "Not specified";
                }
                resClaimDescription.textContent = result.data.claim_description || "-";
                resFileCount.textContent = `${result.data.files_count || 4} evidence files safely saved`;
                resTimestamp.textContent = new Date(result.data.created_at).toLocaleString();
>>>>>>> 772aeb2 (Phase 4)

                // Download buttons
                if (btnDownloadReceipt) {
                    btnDownloadReceipt.href = `/api/claims/${result.claim_id}/receipt`;
                }
                if (btnDownloadDocumentReport) {
                    btnDownloadDocumentReport.href = `/api/claims/${result.claim_id}/document-report`;
                }
                currentActiveClaimId = result.claim_id;

<<<<<<< HEAD
                // Switch views
=======
                // Reset replacement photo box status
                const replaceStatus = document.getElementById("replace-image-status");
                if (replaceStatus) {
                    replaceStatus.style.display = "none";
                    replaceStatus.textContent = "";
                }

                // Switch views within Section 1
>>>>>>> 772aeb2 (Phase 4)
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

<<<<<<< HEAD
    // -------------------------------------------------------------
    // 8. Reset / Submit Another Claim
    // -------------------------------------------------------------
=======
>>>>>>> 772aeb2 (Phase 4)
    if (btnNewClaim) {
        btnNewClaim.addEventListener("click", () => {
            if (claimForm) claimForm.reset();
            clearError();
<<<<<<< HEAD
=======
            refreshFileBadges();
>>>>>>> 772aeb2 (Phase 4)
            if (successCard) successCard.style.display = "none";
            if (submissionCard) {
                submissionCard.style.display = "block";
                submissionCard.scrollIntoView({ behavior: "smooth" });
            }
        });
    }

<<<<<<< HEAD
    // -------------------------------------------------------------
    // 9. Copy Claim ID to Clipboard
    // -------------------------------------------------------------
    if (btnCopyClaimId) {
        btnCopyClaimId.addEventListener("click", async () => {
            const cid = resClaimId ? resClaimId.textContent : "";
=======
    if (btnCopyClaimId) {
        btnCopyClaimId.addEventListener("click", async () => {
            const cid = resClaimId ? resClaimId.textContent : "";
            if (!cid) return;
>>>>>>> 772aeb2 (Phase 4)
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

<<<<<<< HEAD
    // -------------------------------------------------------------
    // 10. Fill Sample Demo Data
    // -------------------------------------------------------------
    if (btnFillSample) {
        btnFillSample.addEventListener("click", () => {
            const elName = document.getElementById("claimant_name");
            const elPolicy = document.getElementById("policy_number");
            const elVehicle = document.getElementById("vehicle_number");
            const elDate = document.getElementById("accident_date");
            const elDesc = document.getElementById("claim_description");

            if (elName) elName.value = "Rajesh Sharma";
            if (elPolicy) elPolicy.value = "POL-2024-88391";
            if (elVehicle) elVehicle.value = "MH-12-DE-4052";
            if (elDate) elDate.value = "2026-09-28";
            if (elDesc) {
                elDesc.value = "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.";
            }

            // Helper to create synthetic files with valid magic signatures for file inputs
            const createDummyFile = (name, type, headerBytes, contentStr) => {
                const enc = new TextEncoder();
                const textBytes = enc.encode(contentStr);
                const combined = new Uint8Array(headerBytes.length + textBytes.length);
                combined.set(headerBytes, 0);
                combined.set(textBytes, headerBytes.length);
                const blob = new Blob([combined], { type: type });
                return new File([blob], name, { type: type });
=======
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

            if (btnSubmitReplaceImage) btnSubmitReplaceImage.disabled = true;
            if (replaceImageStatus) {
                replaceImageStatus.style.display = "block";
                replaceImageStatus.className = "alert alert-info mt-2";
                replaceImageStatus.textContent = "Uploading and validating replacement photograph...";
            }

            try {
                const res = await fetch(`/api/claims/${currentActiveClaimId}/replace-image`, {
                    method: "POST",
                    body: formData,
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    throw new Error(data.message || "Failed to replace vehicle photograph.");
                }

                if (replaceImageStatus) {
                    if (data.validation && data.validation.is_valid_vehicle_photo) {
                        replaceImageStatus.className = "alert alert-success mt-2";
                        replaceImageStatus.textContent = `✓ Replacement photograph verified as authentic vehicle damage evidence (${data.new_image.original_filename}). Original file preserved in audit log.`;
                    } else {
                        replaceImageStatus.className = "alert alert-error mt-2";
                        replaceImageStatus.textContent = `⚠ Uploaded replacement image flagged: ${data.validation ? data.validation.reason : "Invalid vehicle photo"}. Original file remains preserved.`;
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
            document.getElementById("claimant_name").value = "Rajesh Sharma";
            document.getElementById("policy_number").value = "POL-2024-88391";
            document.getElementById("vehicle_number").value = "MH-12-DE-4052";
            document.getElementById("accident_date").value = "2026-09-28";
            const locInput = document.getElementById("incident_location");
            if (locInput) locInput.value = "MG Road, Pune, Maharashtra";
            document.getElementById("claim_description").value =
                "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.";

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
>>>>>>> 772aeb2 (Phase 4)
            };

            const setFileInput = (id, file) => {
                const input = document.getElementById(id);
                if (input) {
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                }
            };

<<<<<<< HEAD
            // Valid signatures: PDF (%PDF), JPEG (\xff\xd8\xff)
            const pdfSig = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x34]); // %PDF-1.4
            const jpgSig = new Uint8Array([0xFF, 0xD8, 0xFF, 0xE0]);

            setFileInput("policy_document", createDummyFile("policy_schedule_88391.pdf", "application/pdf", pdfSig, " sample policy"));
            setFileInput("claim_form_file", createDummyFile("signed_claim_form.pdf", "application/pdf", pdfSig, " claim application"));
            setFileInput("invoice_document", createDummyFile("garage_estimate_4052.pdf", "application/pdf", pdfSig, " itemized estimate"));
            setFileInput("vehicle_image", createDummyFile("rear_bumper_damage.jpg", "image/jpeg", jpgSig, " sample image bytes"));
=======
            setFileInput("policy_document", createSyntheticPdfFile("policy_schedule_88391.pdf", ["CLAIMSENSE AI", "Policy Number: POL-2024-88391", "Vehicle Registration: MH-12-DE-4052", "Accident Date: 2026-09-28"]));
            setFileInput("claim_form_file", createSyntheticPdfFile("signed_claim_form.pdf", ["Claimant: Rajesh Sharma", "Policy Number: POL-2024-88391", "Claim Description: Rear-end collision at MG Road intersection.", "Accident Date: 2026-09-28"]));
            setFileInput("invoice_document", createSyntheticPdfFile("garage_estimate_4052.pdf", ["Garage Estimate", "Claim Amount: INR 84500", "Bodywork and paint: 38500", "Tail lamp replacement: 16000", "Labor and miscellaneous: 30000"]));
            setFileInput("vehicle_image", createSyntheticImageFile("rear_bumper_damage.jpg"));
>>>>>>> 772aeb2 (Phase 4)

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

    function closeClaimDetailsModal() {
        if (modalClaimDetails) modalClaimDetails.style.display = "none";
    }

    function closeClaimEvidenceModal() {
        if (modalClaimEvidence) modalClaimEvidence.style.display = "none";
    }

    if (btnCloseDetailsModal) btnCloseDetailsModal.addEventListener("click", closeClaimDetailsModal);
    if (btnModalClose) btnModalClose.addEventListener("click", closeClaimDetailsModal);
    if (btnCloseEvidenceModal) btnCloseEvidenceModal.addEventListener("click", closeClaimEvidenceModal);
    if (btnEvidenceModalClose) btnEvidenceModalClose.addEventListener("click", closeClaimEvidenceModal);

    async function openClaimDetailsModal(claimId) {
        if (!modalClaimDetails) return;

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
});
