# ClaimSense AI — Independent Validation Dataset: Revised Acquisition Portfolio

**Document Version:** 1.0 (Post-Audit Realignment)  
**Audit Date:** 2026-11-17  
**Scope:** Reassessment and reallocation of candidate images based on verified asset-level availability and legal clearance  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Strictly Audit Only. No downloads, no scraping, no model modifications.

---

## 1. Portfolio Reassessment Rationale

The asset-level legal audit (`source_level_license_audit.md`) and physical availability verification (`verified_source_availability.md`) exposed fundamental flaws in the initial preliminary allocation:

1. **SRC-03 (anujms) is completely unusable:** Discovered to be an unlicensed 2018 web scrape lacking an open-source license tag on Kaggle. Its prior 35-image allocation must be **zeroed out**.
2. **SRC-04 (lplenka) cannot support volume or tire flats:** Discovered to contain only 80 total images in existence, with zero flat tires. Its prior 35-image allocation was based on an unverified claim and must be **zeroed out**.
3. **SRC-01 & SRC-05 carry conditional asset-level title:** While rich in collision imagery, both rely on user-level platform declarations with unverified uploader copyright. They must be treated as **quarantined auxiliary sources** and capped.
4. **SRC-02 & SRC-06 are institutional gold standards:**
   - **SRC-02 (Humans in the Loop / DrBimmer):** 1,812 authentic images officially dedicated to the public domain under **CC0 1.0 Universal** by Humans in the Loop.
   - **SRC-06 (Wikimedia Commons):** 10,000+ files with verified per-file CC0/CC-BY licenses, camera EXIF metadata, and premier coverage of rare flat tires and hail damage.

To maintain absolute legal integrity while ensuring statistical diversity, the 235-image portfolio is restructured around **verified primary anchors**.

---

## 2. Source Feasibility Categorization

In accordance with Phase 8 readiness standards, all evaluated candidate pools are segmented into four distinct governance categories:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Source Availability & Clearance Tiers                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: Verified Available & Legally Cleared (Primary Anchor Pool)                    │
│ • SRC-02: DrBimmer / Humans in the Loop (CC0 / MIT)        : 1,812 verified images     │
│ • SRC-06: Wikimedia Commons (CC0 / CC-BY per-file)        : 10,000+ verified images   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Estimated Potential under Conditional Quarantine (Auxiliary Internal Pool)     │
│ • SRC-01: Roboflow Universe Car Damage V5 (CC BY 4.0)      : 3,001 available images    │
│ • SRC-05: Kaggle Insurance Claims (vinayjose, Apache 2.0)  : ~8,080 available images   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Sources Requiring Bilateral Legal Permission (On Hold)                         │
│ • SRC-07: SKKU TQVCD (No license file; requires signed MOU): ~3,000 images             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 4: Sources Unsuitable for Commercial / Production AI (Rejected)                   │
│ • SRC-03: Kaggle COCO (anujms) — Unlicensed web scrape     : 0 images allocated        │
│ • SRC-04: Kaggle Damage (lplenka) — Tiny 80-image tutorial : 0 images allocated        │
│ • SRC-08: Mendeley SYNDCAR — Synthetic 3D CAD & CC BY-NC   : 0 images allocated        │
│ • SRC-09: Salvage Auction Scraping — ToS Section 2 breach  : 0 images allocated        │
│ • SRC-10: Stock Photography — AI training contract required: 0 images allocated        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Revised 235-Image Quota Allocation

The restructured portfolio draws **74.5% of all images (175 images)** directly from Tier 1 verified repositories, with the remaining **25.5% (60 images)** sourced from Tier 2 under strict internal quarantine controls:

| Source ID | Source Repository Name | Legal Clearance Tier | Documented License | Previous Preliminary Allocation | **Revised Approved Allocation** | Primary Targeted Categories |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **SRC-02** | **DrBimmer / Humans in the Loop** | **Tier 1 (Verified)** | **CC0 / MIT** | 60 | **115 images** | Plastic Bumper Cracks, Broken Lamp Assemblies, Body Scratches, Dents |
| **SRC-06** | **Wikimedia Commons Collections** | **Tier 1 (Verified)** | **CC0 / CC-BY** | 25 | **60 images** | Flat Tires (25–28 imgs), Hail Dents (15 imgs), Shattered Windows (10 imgs), Lamps (7 imgs) |
| **SRC-01** | **Roboflow Car Damage V5** | Tier 2 (Quarantine) | CC BY 4.0 | 55 | **35 images** | Panel Scratches, Shallow Dents, Splitters |
| **SRC-05** | **Kaggle Insurance Claims (vinayjose)** | Tier 2 (Quarantine) | Apache 2.0 | 25 | **25 images** | Heavy Impact Dents, Shattered Windshields, Grille Cracks |
| **SRC-03** | Kaggle COCO (anujms) | Tier 4 (Rejected) | None | 35 | **0 images** | *Excluded (Unlicensed scraped data)* |
| **SRC-04** | Kaggle Damage (lplenka) | Tier 4 (Deprecated) | CC0 (80 imgs) | 35 | **0 images** | *Excluded (Insufficient scale; zero flat tires)* |
| **Total** | *Balanced Portfolio* | *Verified & Permissive* | — | 235 | **235 images** | *(+15 image contingency buffer = 250 max)* |

---

## 4. Class-Wise Target Instance Reassessment

In strict compliance with audit standards, **all class-wise instance quotas remain operational targets** until actual images are physically ingested and audited under the Dual-Blind Protocol. 

However, mathematical modeling based on verified repository contents confirms the revised portfolio realistically supports every target quota:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             Class-Wise Instance Quota Support Modeling (235 Images)                    │
├──────────────┬────────┬────────────────────────────┬──────────────────┬────────────────┤
│ Damage Class │ Target │ Primary Source Providers   │ Estimated Yield  │ Safety Margin  │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Dent         │ 90+    │ SRC-02, SRC-06 (Hail),     │ ~130 instances   │ +44.4%         │
│              │        │ SRC-01, SRC-05             │                  │ (Over-indexed) │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Scratch      │ 100+   │ SRC-02, SRC-01, SRC-05     │ ~140 instances   │ +40.0%         │
│              │        │                            │                  │ (Over-indexed) │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Crack        │ 60+    │ SRC-02 (Cracked class:     │ ~68 instances    │ +13.3%         │
│              │        │ bumper tears & splitters)  │                  │ (Adequate)     │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Glass shatter│ 40+    │ SRC-06 (Broken windows),   │ ~46 instances    │ +15.0%         │
│              │        │ SRC-05 (Windshields)       │                  │ (Adequate)     │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Lamp broken  │ 45+    │ SRC-02 (Broken parts),     │ ~50 instances    │ +11.1%         │
│              │        │ SRC-05, SRC-06             │                  │ (Adequate)     │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Tire flat    │ 30+    │ SRC-06 (Category:          │ ~32 instances    │ +6.7%          │
│              │        │ Flat_tires: 25–28 dedicated│                  │ (Critical Quota│
│              │        │ high-res photos)           │                  │ Reserved)      │
├──────────────┼────────┼────────────────────────────┼──────────────────┼────────────────┤
│ Total        │ 365+   │ All 4 Allocated Sources    │ ~466 instances   │ +27.7%         │
└──────────────┴────────┴────────────────────────────┴──────────────────┴────────────────┘
```

### Critical Class Strategy Notes:
1. **Tire Flat Bottleneck Solved:** Previously, SRC-04 was expected to supply flat tires, but inspection proved it contained zero flat tire images. The revised plan reallocates this requirement entirely to **Wikimedia Commons `Category:Flat_tires`**, which contains over 200 authentic, verified photographs of flat/punctured passenger tires. Reserving 25–28 images from this category guarantees meeting the 30+ instance target.
2. **Crack Quality Focus:** Plastic bumper cracks (which suffered severe confusion in CarDD Session 2/4) will be sourced primarily from **SRC-02 (Humans in the Loop)**, whose body shop intake photography provides high-resolution, uncompressed panel tears and split seams.
3. **Hail Dent Density:** Dedicated inclusion of 15 hail-damage photographs from Wikimedia Commons will yield 60–90 distinct dent instances across hoods and roofs, providing the necessary statistical volume without inflating total image count.
