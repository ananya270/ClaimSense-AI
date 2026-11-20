/**
 * ClaimSense AI - English Translations (en)
 * Enterprise-grade professional insurance technology terminology
 */

window.CLAIM_TRANSLATIONS = window.CLAIM_TRANSLATIONS || {};
window.CLAIM_TRANSLATIONS.en = {
  // Brand & Header
  brand_name: "ClaimSense AI",
  brand_subtitle: "Enterprise Insurance Claim Verification & Multi-Source Decision Support",
  status_checking: "Checking backend...",
  status_online: "API Online (Port 5001)",
  status_offline: "Backend Offline",
  theme_toggle: "Theme",
  sign_in: "Sign In",
  register: "Register",
  sign_out: "Sign Out",
  user_claimant: "Claimant",
  user_assessor: "Claims Assessor",
  disclaimer_badge: "Academic Decision-Support Prototype",
  disclaimer_text: "This system identifies inconsistencies and cross-source evidentiary patterns across documents, vehicle photographs, and narratives to assist human claim adjusters. It does not render autonomous legal or insurance decisions.",

  // Sidebar & Navigation
  nav_dashboard: "Dashboard",
  nav_submit: "Submit Claim Evidence",
  nav_myclaims: "My Submissions",
  nav_lookup: "Policy Claim Lookup",
  nav_documents: "Documents & Evidence",
  nav_reports: "Reports & Receipts",
  nav_help: "Help Centre & Guides",
  nav_settings: "Portal Settings",
  badge_new: "New",
  badge_coming_soon: "Coming Soon",

  // Dashboard
  dash_welcome: "Welcome back",
  dash_subtitle: "Review claim corroboration metrics, submit multi-source documentation, and inspect forensic findings.",
  dash_btn_submit: "Submit New Claim",
  dash_btn_help: "Explore Help Centre",
  dash_stat_total: "Total Submissions",
  dash_stat_review: "Review Required",
  dash_stat_consistent: "Fully Corroborated",
  dash_stat_active_policy: "Active Policies",
  dash_recent_claims: "Recent Claim Activity",
  dash_no_claims: "No claims submitted yet.",
  dash_no_claims_sub: "Get started by submitting your first insurance claim evidence package.",
  dash_quick_policy_title: "Quick Policy Verification",
  dash_quick_policy_desc: "Enter a policy number to index associated claim records.",
  dash_quick_policy_btn: "Verify Policy",
  dash_checklist_title: "Evidence Checklist",
  dash_chk_policy: "Official Insurance Policy Schedule (PDF)",
  dash_chk_form: "Signed Claim Application Form (PDF)",
  dash_chk_invoice: "Itemized Repair Estimate or Invoice (PDF)",
  dash_chk_photo: "Authentic Vehicle Accident Photograph (JPG/PNG)",

  // Submission Wizard
  wiz_title: "Guided Insurance Claim Submission",
  wiz_subtitle: "Complete the 4-step guided wizard to submit claimant metadata, incident chronology, and forensic files for automated verification.",
  wiz_step1_title: "Claimant Info",
  wiz_step2_title: "Incident Details",
  wiz_step3_title: "Upload Evidence",
  wiz_step4_title: "Review & Confirm",
  wiz_btn_demo: "✨ Fill Demo Sample",
  wiz_btn_next: "Continue",
  wiz_btn_prev: "Back",
  wiz_btn_submit: "Submit Claim for Verification 🚀",
  wiz_submitting: "Processing & Verifying Documents...",

  // Wizard Step 1
  step1_heading: "1. Claimant & Policy Metadata",
  step1_desc: "Enter verified legal claimant identifiers matching your insurance policy schedule.",
  lbl_claimant_name: "Claimant Full Name",
  ph_claimant_name: "e.g. Rajesh Sharma",
  lbl_policy_number: "Policy Number",
  ph_policy_number: "e.g. POL-2026-9901",
  lbl_vehicle_number: "Vehicle Registration #",
  ph_vehicle_number: "e.g. DL-01-AB-1234",
  lbl_accident_date: "Accident / Incident Date",
  lbl_incident_location: "Incident Location / City (Optional)",
  ph_incident_location: "e.g. MG Road, Sector 62, Noida",

  // Wizard Step 2
  step2_heading: "2. Incident Narrative & Damage Description",
  step2_desc: "Provide an accurate factual statement detailing how the collision or damage occurred.",
  lbl_narrative: "Accident Narrative / Claim Statement",
  ph_narrative: "Describe how the accident occurred, stated damage locations (e.g. rear bumper, right tail lamp), impact direction, and driving conditions...",
  guide_title: "Writing Guide for Adjuster Review:",
  guide_tip1: "State the chronological sequence of events clearly.",
  guide_tip2: "Specify exact vehicle components damaged (e.g., bumper dent, broken lamp, side scratches).",
  guide_tip3: "Mention speed, weather, and roadway circumstances.",
  sample_narrative_title: "Example Good Narrative:",
  sample_narrative_text: "Rear collision during evening commute. Bumper was dented and right tail lamp broken when stationary at a traffic signal.",
  btn_use_sample: "Use Sample Narrative",

  // Wizard Step 3
  step3_heading: "3. Multi-Source Evidence Uploads",
  step3_desc: "All four distinct evidence categories are strictly mandatory for cross-source algorithmic triangulation.",
  upload_policy_title: "Insurance Policy Schedule",
  upload_policy_desc: "Official policy document confirming validity dates and covered vehicle.",
  upload_form_title: "Claim Application Form",
  upload_form_desc: "Signed claim registration document with stated damage itemization.",
  upload_invoice_title: "Repair Invoice / Estimate",
  upload_invoice_desc: "Itemized repair estimate or garage parts invoice for cost corroboration.",
  upload_photo_title: "Vehicle Accident Photograph",
  upload_photo_desc: "Clear daylight photograph showing exterior vehicle damage components.",
  upload_drag_drop: "Drag & drop file here or click to browse",
  upload_max_size: "Max size: 16 MB",
  upload_accepted: "Accepted formats:",
  upload_btn_remove: "Remove File",

  // Wizard Step 4
  step4_heading: "4. Review & Confirm Submission",
  step4_desc: "Review your submitted information and evidence files before initiating AI verification.",
  rev_claimant_summary: "Claimant & Policy Summary",
  rev_narrative_summary: "Accident Statement Summary",
  rev_files_summary: "Evidence Package Checklist",
  rev_confirm_label: "I confirm that the submitted incident narrative and evidence files are authentic to the best of my knowledge for algorithmic verification and assessor review.",
  rev_warning: "Please ensure all 4 evidence documents are selected and the confirmation checkbox is checked.",

  // Wizard Step 5 / Success Card
  success_heading: "Claim Successfully Registered",
  success_desc: "Your claim has been assigned a unique tracking identifier and evidence files are secured.",
  claim_id_label: "Generated Claim Identifier:",
  btn_copy_id: "📋 Copy ID",
  btn_view_modal: "🔍 View Claim & AI Analysis",
  btn_download_receipt: "📄 Download PDF Receipt",
  btn_download_report: "📊 Download Document Report",
  btn_new_claim: "➕ Submit Another Claim",

  // Replace Photo
  rep_title: "Replace Vehicle Accident Photograph",
  rep_desc: "If the initial upload was flagged as an invalid graphic or document scan, upload an authentic vehicle photograph. The original file remains preserved in the audit log.",
  rep_btn_upload: "Upload Replacement Photo",

  // Policy Lookup Section
  lookup_title: "Policy Claim Verification & Index",
  lookup_desc: "Search database for claims registered under a specific insurance policy identifier.",
  lbl_search_policy: "Insurance Policy Number",
  ph_search_policy: "e.g. POL-2026-9901",
  btn_search_policy: "Search Policy Claims",
  lookup_empty_title: "Policy Index Explorer",
  lookup_empty_desc: "Enter an active policy identifier above to inspect registered claims, vehicle numbers, and cross-source verification status.",
  lookup_results_found: "Policy Record Identified",

  // My Submissions Section
  myclaims_title: "Claim Submissions & Tracking",
  myclaims_desc: "Monitor your submitted claims, inspect automated damage detections, and download audit reports.",
  btn_refresh: "Refresh Submissions",
  ph_filter_search: "Search by Claim ID, Name, or Vehicle...",
  opt_all_status: "All Statuses",
  opt_review: "Review Required",
  opt_consistent: "Consistent",
  opt_inconclusive: "Inconclusive",
  lbl_sort: "Sort by:",
  opt_sort_newest: "Newest First",
  opt_sort_oldest: "Oldest First",
  myclaims_empty_title: "No Claim Submissions Found",
  myclaims_empty_desc: "You have not submitted any insurance claims under this account yet.",

  // Help Centre Section
  help_title: "Interactive User Manual & Knowledge Base",
  help_subtitle: "Comprehensive operational guides explaining claim submission, document requirements, verification rules, and audit report interpretation.",
  help_search_ph: "Search articles, guides, rules, FAQs...",
  help_tab_intro: "1. Getting Started",
  help_tab_guide: "2. How to Submit",
  help_tab_upload: "3. Upload Guidelines",
  help_tab_rules: "4. Verification Rules",
  help_tab_reports: "5. Understanding Reports",
  help_tab_faq: "6. Frequently Asked Questions",
  btn_start_tour: "Launch Guided Onboarding Walkthrough 🚀",

  // Modals & Details
  modal_close: "Close",
  modal_claim_details_title: "Claim Record & Algorithmic Verification Details",
  modal_tab_vision: "Vehicle Damage Detection (YOLOv8)",
  modal_tab_nlp: "Narrative & Chronology (NLP)",
  modal_tab_verif: "Cross-Source Verification (Phase 7)",
  btn_reverify: "🔄 Re-run Cross-Source Verification",

  // Notifications
  toast_copied: "Claim ID copied to clipboard!",
  toast_login_success: "Signed in successfully. Welcome back!",
  toast_logout_success: "Signed out successfully.",
  toast_sample_filled: "Demo sample claim fields populated.",
  toast_lang_changed: "Language preference updated.",
  toast_theme_changed: "Display theme updated."
};
