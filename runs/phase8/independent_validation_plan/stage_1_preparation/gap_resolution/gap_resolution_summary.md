# ClaimSense AI — Phase 8: Targeted Dataset Gap Resolution Summary

**Document Version:** 1.0 (Executive Resolution Report)  
**Audit Date:** 2026-11-17  
**Scope:** Resolution of Tire Flat and Glass Shatter candidate shortages via targeted MediaWiki API discovery  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Acquisition Gate Status:** **LOCKED — READ-ONLY DISCOVERY COMPLETE.** No image binaries downloaded.

---

## 1. Executive Summary & Resolution Verdict

```
========================================================================================
            DATASET GAP RESOLUTION VERDICT: ALL CANDIDATE DEFICITS RESOLVED
                      (86 Tire Candidates | 38 Glass Candidates Verified)
========================================================================================
```

Following the Stage 1 Readiness Audit, which flagged a projected deficit of ~12 tire flat instances and ~14 glass shatter instances under approved sources, we executed an expanded, multilingual MediaWiki Action API discovery across 7 Wikimedia Commons categories and 15 targeted search terms.

The discovery successfully identified:
1. **86 License-Cleared Tire Flat Candidates:** Verified under CC0, Public Domain, or CC BY (excluding 95 CC BY-SA files). Provides an estimated **~53 usable passenger vehicle images** and **~60 projected tire flat instances** (exceeding the 30-instance target by +100%).
2. **38 License-Cleared Glass Shatter Candidates:** Verified under CC0, Public Domain, or CC BY (excluding 66 CC BY-SA files). Combined with previously verified files and institutional intake, provides **~48 usable glass damage images** and **~62 projected glass instances** (exceeding the 40-instance target by +55%).
3. **Zero Copyleft Contamination:** All 161 identified CC BY-SA and GFDL candidate files were categorically excluded, eliminating any legal ambiguity regarding model weight derivation under Share-Alike terms.

---

## 2. Final Candidate Counts & Feasibility Reconciliation

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Final 6-Class Feasibility Reconciliation                        │
├──────────────┬────────┬──────────────────────────┬───────────┬──────────────┬──────────┤
│ Damage Class │ Target │ Primary Source Provider  │ Verified  │ Projected    │ Gap      │
│              │ Quota  │                          │ Candidates│ Instances*   │ Status   │
├──────────────┼────────┼──────────────────────────┼───────────┼──────────────┼──────────┤
│ Dent         │ 90+    │ SRC-02 (HITL) + Hail (35)│ 1,847     │ ~130 inst    │ ADEQUATE │
│ Scratch      │ 100+   │ SRC-02 (HITL Panels)     │ 1,812     │ ~140 inst    │ ADEQUATE │
│ Crack        │ 60+    │ SRC-02 (HITL Bumper Tear)│ 1,812     │ ~68 inst     │ ADEQUATE │
│ Lamp broken  │ 45+    │ SRC-02 (HITL Lights)     │ 1,812     │ ~50 inst     │ ADEQUATE │
│ Glass shatter│ 40+    │ SRC-06 (Glass: 38 + 10)  │ 48        │ ~62 inst     │ RESOLVED │
│ Tire flat    │ 30+    │ SRC-06 (Tires: 86)       │ 86        │ ~60 inst     │ RESOLVED │
├──────────────┼────────┼──────────────────────────┼───────────┼──────────────┼──────────┤
│ Total Dataset│ 365+   │ 235 Curated Images       │ 1,981     │ ~510 inst    │ ALL MET  │
└──────────────┴────────┴──────────────────────────┴───────────┴──────────────┴──────────┤
```
*\*Projected instances represent mathematical modeling based on verified candidate media files. They do NOT count as verified ground-truth annotations until physical image intake and Dual-Blind labeling occur.*

---

## 3. Unresolved Shortages & Remaining Operational Actions

- **Candidate Availability Shortages:** **NONE.** All candidate volume deficits against the contract quotas are fully resolved using exclusively approved sources (Humans in the Loop CC0 + Wikimedia Commons CC0/CC-BY). Roboflow Universe V5 and Kaggle Insurance Claims remain 100% excluded.
- **Remaining Operational Gates Prior to Acquisition:**
  1. *Acquisition Gate Remains Locked:* No image binaries have been downloaded; live download requires explicit user authorization.
  2. *Intake Usability Filter:* When acquisition is authorized, the automated pipeline must filter out the ~33 non-passenger vehicle items identified in the raw candidate manifests.
  3. *Solid PII Masking & Human Review:* Execution of the validated zero-entropy solid masking protocol ($[0,0,0]$ black box with $\ge 15\%$ dilation) and manual inspection of chrome reflection channels during the Dual-Blind annotation protocol.

---

## 4. Deliverables Inventory & Cryptographic Checksums

All deliverables for the Targeted Dataset Gap Resolution are saved in `runs/phase8/independent_validation_plan/stage_1_preparation/gap_resolution/` with verified cryptographic SHA-256 hashes:

| Deliverable Artifact | File Type | Size | Cryptographic SHA-256 Checksum |
| :--- | :---: | :---: | :--- |
| **`tire_candidates.csv`** | CSV Manifest | 29,329 B | `3aeff7ff0385c3645110ea7fc633404ff80670196634a4c5eb8824e632f950cc` |
| **`glass_candidates.csv`** | CSV Manifest | 13,747 B | `08dc2a395f93ba5f9709f9425effe009477bad77777cccedad93743c7a72e33e` |
| **`license_verification_report.md`** | Markdown Report | 7,446 B | `07a76af54b1a357279a0eb7173e5fe95c8047eb7fe8c59439b32b5f9f1e4eec7` |
| **`revised_class_feasibility.md`** | Markdown Report | 10,192 B | `9ba7948122a237052585d057a856182184e5971cf74979d032cdb805539b7f3b` |
| **`gap_resolution_summary.md`** | Markdown Report | ~7,000 B | *(Self-referential summary report)* |
| **`gap_discovery_raw.json`** | JSON Metadata | 2,002 B | `aea0ca792bc0f0e36acd34d53697d0ff29ac801eea12d20c851343a9d7311798` |
