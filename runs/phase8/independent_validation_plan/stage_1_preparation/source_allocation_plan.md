# ClaimSense AI — Phase 8: Approved Source Feasibility & Allocation Plan

**Document Version:** 1.0 (Strictly Approved Sources Only)  
**Audit Date:** 2026-11-17  
**Scope:** Feasibility evaluation and source-wise image allocation plan for the 235-image target using exclusively legally cleared sources  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Governing Mandate:** Roboflow Universe V5 and Kaggle Insurance Claims are **strictly excluded**. No reliance on Fair Use assumptions.

---

## 1. Approved Source Eligibility & Governance Boundary

In strict compliance with executive directives, candidate sources without verifiable asset-level copyright title are disqualified from the acquisition plan:
- **Roboflow Car Damage V5 (`SRC-01`):** **EXCLUDED.** Uploader chain of title is unverified; cannot be used without bilateral written copyright assignment.
- **Kaggle Insurance Claims (`SRC-05`):** **EXCLUDED.** Uploader lacks copyright title over third-party insurer claim walkarounds.
- **Kaggle COCO (`SRC-03`) & Kaggle Damage (`SRC-04`):** **EXCLUDED.** Unlicensed scrape and trivial scale, respectively.

The acquisition pool is restricted exclusively to **two legally verified sources**:
1. **Humans in the Loop / DrBimmer (`SRC-02`):** Institutional dedication to the public domain under **Creative Commons CC0 1.0 Universal**.
2. **Wikimedia Commons (`SRC-06`):** Photographic media files individually verified via official MediaWiki API as **CC0, Public Domain, or CC BY** (with full photographer attribution). All CC BY-SA (Share-Alike) and GFDL files are excluded.

---

## 2. Source-by-Source Physical Availability Funnel

The table below distinguishes documented platform totals from physically accessible, legally cleared, and estimated usable counts:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   Approved Source Availability & Usability Funnel                      │
├────────┬─────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Source │ Source Name     │ Doc Count│ License- │ Actually │ Est. Post│ Target Stage 1  │
│ ID     │                 │ (Card)   │ Verified │ Accessible│ Screening│ Allocation Plan │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SRC-02 │ Humans in Loop  │ 1,812    │ 1,812    │ 1,812    │ ~580     │ **190 images**  │
│        │ (Institutional) │          │ (CC0)    │ (HF/API) │ (Clean)  │ (80.9%)         │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SRC-06 │ Wikimedia Comm. │ 10,000+  │ 71*      │ 71       │ ~45      │ **45 images**   │
│        │ (General + Hail)│          │ (CC0/BY) │ (API)    │ (Vehicle)│ (19.1%)         │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Total  │ Approved Pool   │ 11,812   │ 1,883    │ 1,883    │ ~625     │ **235 images**  │
└────────┴─────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```
*\*Derived from live API queries: 36 verified general damage candidates (`wikimedia_candidate_manifest.csv`) + 35 verified hail damage candidates (`wikimedia_hail_candidates.csv`).*

### Usability Screening Adjustments:
1. **Humans in the Loop (`SRC-02`):**  
   Contains 814 dedicated vehicle damage images and 998 vehicle part images. Applying an estimated 25%–30% intake fallout (rejecting low-resolution thumbnails, severe motion blur, and license plates where solid masking would occlude $>20\%$ of adjacent damage) leaves **~580 high-integrity usable damage photographs**. Allocating **190 images** is realistic and utilizes only 32.7% of available usable stock.
2. **Wikimedia Commons (`SRC-06`):**  
   Out of 71 license-verified CC0/CC-BY candidates identified across the MediaWiki queries, manual review of titles and descriptions shows ~26 files are non-vehicular (apples, satellite agricultural scans, space shuttle foam repairs) or low resolution ($<800 \times 600$). This leaves **~45 genuine, high-resolution automobile damage photographs** available for allocation.

---

## 3. Class-Wise Instance Feasibility & Critical Bottleneck Flags

Treating class quotas strictly as **operational targets** rather than guarantees, mathematical yield modeling based on verified source contents reveals critical category imbalances:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             Approved Source Class Feasibility & Bottleneck Matrix                      │
├──────────────┬────────┬──────────────────────────┬──────────────────┬──────────────────┤
│ Damage Class │ Target │ Primary Source Provider  │ Estimated Yield  │ Feasibility Flag │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Dent         │ 90+    │ SRC-02 (Body Panels) +   │ ~125 instances   │ **SUFFICIENT**   │
│              │        │ SRC-06 (12 Hail Photos)  │                  │ (Robust Margin)  │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Scratch      │ 100+   │ SRC-02 (Clearcoat/Primer)│ ~135 instances   │ **SUFFICIENT**   │
│              │        │                          │                  │ (Robust Margin)  │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Crack        │ 60+    │ SRC-02 (`Cracked` Class: │ ~65 instances    │ **FEASIBLE**     │
│              │        │ Bumper splits/tears)     │                  │ (Adequate)       │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Lamp broken  │ 45+    │ SRC-02 (`Broken part` +  │ ~50 instances    │ **FEASIBLE**     │
│              │        │ Headlight/Taillight)     │                  │ (Adequate)       │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Glass shatter│ 40+    │ SRC-06 (Broken Windows) +│ ~26 instances    │ **CONSTRAINED**  │
│              │        │ SRC-02 (Windshield tears)│                  │ (Deficit: ~14)   │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Tire flat    │ 30+    │ SRC-06 (Flat Tires:      │ ~18 instances    │ **INSUFFICIENT** │
│              │        │ 16 verified CC0/CC-BY)   │                  │ (Deficit: ~12)   │
├──────────────┼────────┼──────────────────────────┼──────────────────┼────────────────┤
│ Total        │ 365+   │ 235 Curated Images       │ ~419 instances   │ Over-Indexed in  │
│              │        │                          │                  │ Dents/Scratches  │
└────────┴────────┴──────────────────────────┴──────────────────┴──────────────────┘
```

---

## 4. In-Depth Bottleneck Analysis

### A. Critical Bottleneck 1: Tire Flat (Target: 30+, Estimated: ~18) — **INSUFFICIENT**
- **Root Cause:**  
  1. Humans in the Loop (`SRC-02`) contains **zero flat tire images** (its scope is restricted to body panels, lights, and intact alloy wheels).
  2. Wikimedia Commons `Category:Flat_tires` contains 38 total files, but **22 files carry CC BY-SA 3.0 / 4.0** and were strictly excluded to eliminate copyleft risks. Only **16 files** carry verified CC0, Public Domain, or CC BY deeds.
  3. Assuming an average of 1.15 flat tire instances per photograph, 16 approved images can produce at most **18–20 ground-truth tire flat instances**, falling **10–12 instances short of the 30-instance target quota**.
- **Actionable Remediation Options:**
  - *Option A:* Execute expanded MediaWiki search queries across non-English categories (e.g. `Category:Punctured tires`, `Category:Deflated tires`, French `Pneu crevé`, German `Reifenpanne`).
  - *Option B:* Accept an operational benchmark target of 18–20 tire flat instances, adjusting the statistical confidence interval accordingly.

### B. Bottleneck 2: Glass Shatter (Target: 40+, Estimated: ~26) — **CONSTRAINED**
- **Root Cause:**  
  1. Wikimedia `Category:Broken_car_windows` yielded only 4 CC0/CC-BY files (26 were CC BY-SA).
  2. The hail search added ~6 authentic shattered rear windshield photos.
  3. Total approved glass shatter images equal ~12–14 files, yielding approximately **24–28 verified glass instances**.
- **Actionable Remediation Options:**
  - Traverse specific disaster subcategories on Wikimedia Commons (e.g. `Category:Vandalized vehicles`, `Category:Civil unrest vehicle damage`).

---

## 5. Final Stage 1 Allocation Decision

```
                 Approved Stage 1 Portfolio Allocation (235 Images)
                 
   ┌────────────────────────────────────────────────────────────────────────┐
   │ SRC-02: Humans in the Loop (CC0 1.0 Universal)     : 190 images (80.9%)│
   │ SRC-06: Wikimedia Commons (CC0 / CC BY verified)   :  45 images (19.1%)│
   ├────────────────────────────────────────────────────────────────────────┤
   │ Total Planned Curated Intake                       : 235 images        │
   │ Raw Candidate Pipeline Buffer Required             : 320 images        │
   └────────────────────────────────────────────────────────────────────────┘
```

**Conclusion:**  
While reaching **235 authentic, legally approved images** is fully viable, **approved sources alone are currently INSUFFICIENT to meet the 30+ Tire Flat quota (capped at ~18) and CONSTRAINED for Glass Shatter (~26)** without expanding Wikimedia search queries into non-English punctured tire categories.
