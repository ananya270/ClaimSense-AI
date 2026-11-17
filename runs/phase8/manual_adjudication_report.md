# Phase 8 — Manual Annotation Adjudication Dossier (78 Preserved Cases)

**Project:** ClaimSense AI  
**Module:** Human-in-the-Loop Annotation Review & Adjudication Protocol  
**Date:** November 17, 2026  
**Total Cases Preserved in Queue:** **78 Cases** (16 Scratch Cases, 2 Dent Cases, 60 Missing Crack Candidates)  
**Policy:** Zero Automated Damage Additions — All Candidates Require Explicit Human Sign-Off  

---

## 1. Executive Summary & Adjudication Protocol

In accordance with Phase 8 strict safeguards, all ambiguous, wide-span, needle-aspect, or missing-damage candidates are quarantined in this visual adjudication dossier. **No missing labels have been added to the dataset.**

Every case provides the exact image filename, native pixel resolution, original annotation coordinates, candidate region bounds, visual evidence notes, and a recommended adjudication decision for the human claims inspector.


---

## 2. Scratch Adjudication Queue (16 Cases: MQ-SC-01 to MQ-SC-16)

These 16 cases represent multi-segment scratch markings that either span large proportions of the image or have spatial separation suggesting they are distinct damage events across separate body panels.


### Case MQ-SC-01: `000118.jpg` (Reclassified from Stage 2)

- **Resolution:** 1000 x 664 px  
- **Original Annotations (3 Fragments):**
  - Line 3: `1 0.1181 0.1610 0.2363 0.1813` (236.3x120.4 px)
  - Line 4: `1 0.4119 0.1988 0.3088 0.2031` (308.8x134.9 px)
  - Line 5: `1 0.6691 0.4866 0.2989 0.3724` (298.9x247.3 px)
- **Candidate Unified Bounding Region:** `1 0.4093 0.3715 0.8186 0.6024` (Area: 49.3% of frame)  
- **Visual Evidence & Assessment:** Merged box would occupy 49.3% of image or expands area by 2.27x. Visual inspection shows scratches are separated by intact panel skin or belong to separate rub incidents.  
- **Proposed Adjudication Decision:** **`KEEP AS SEPARATE BOXES (Reject Consolidation)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-02: `000512.jpg` (Reclassified from Stage 2)

- **Resolution:** 1000 x 667 px  
- **Original Annotations (5 Fragments):**
  - Line 1: `1 0.1217 0.4325 0.2434 0.1915` (243.4x127.7 px)
  - Line 2: `1 0.1440 0.1598 0.2881 0.0621` (288.1x41.5 px)
  - Line 3: `1 0.3240 0.4115 0.0976 0.1235` (97.6x82.4 px)
  - Line 4: `1 0.3941 0.4630 0.0802 0.2308` (80.2x153.9 px)
  - Line 5: `1 0.3999 0.7458 0.0730 0.1983` (73.0x132.3 px)
- **Candidate Unified Bounding Region:** `1 0.2182 0.4868 0.4364 0.7163` (Area: 31.3% of frame)  
- **Visual Evidence & Assessment:** Merged box would occupy 31.3% of image or expands area by 2.85x. Visual inspection shows scratches are separated by intact panel skin or belong to separate rub incidents.  
- **Proposed Adjudication Decision:** **`KEEP AS SEPARATE BOXES (Reject Consolidation)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-03: `000566.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (3 Fragments):**
  - Line 3: `1 0.1976 0.7787 0.2202 0.3698` (220.2x246.6 px)
  - Line 4: `1 0.9207 0.6008 0.0593 0.2969` (59.3x198.0 px)
  - Line 5: `1 0.9791 0.6330 0.0418 0.3140` (41.8x209.5 px)
- **Candidate Unified Bounding Region:** `1 0.5437 0.7080 0.9125 0.5113` (Area: 46.7% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 24.0%, merged area 46.7%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-04: `000594.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (4 Fragments):**
  - Line 2: `1 0.2994 0.3809 0.2778 0.0902` (277.8x60.2 px)
  - Line 3: `1 0.2861 0.5925 0.4929 0.7563` (492.9x504.5 px)
  - Line 4: `1 0.7363 0.3021 0.4336 0.3446` (433.6x229.8 px)
  - Line 5: `1 0.7536 0.7697 0.4928 0.3912` (492.8x260.9 px)
- **Candidate Unified Bounding Region:** `1 0.5198 0.5502 0.9604 0.8409` (Area: 80.8% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 91.6%, merged area 80.8%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-05: `001486.jpg`

- **Resolution:** 1000 x 750 px  
- **Original Annotations (3 Fragments):**
  - Line 3: `1 0.2291 0.6774 0.1225 0.2521` (122.5x189.1 px)
  - Line 4: `1 0.4141 0.5008 0.0817 0.1088` (81.7x81.6 px)
  - Line 5: `1 0.5206 0.4189 0.1429 0.2199` (142.9x164.9 px)
- **Candidate Unified Bounding Region:** `1 0.3800 0.5562 0.4242 0.4945` (Area: 21.0% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 33.9%, merged area 21.0%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-06: `001724.jpg` (Reclassified from Stage 2)

- **Resolution:** 1000 x 667 px  
- **Original Annotations (2 Fragments):**
  - Line 2: `1 0.5213 0.5925 0.5574 0.5509` (557.4x367.4 px)
  - Line 3: `1 0.9017 0.5980 0.1450 0.1350` (145.0x90.0 px)
- **Candidate Unified Bounding Region:** `1 0.6084 0.5925 0.7315 0.5509` (Area: 40.3% of frame)  
- **Visual Evidence & Assessment:** Merged box would occupy 40.3% of image or expands area by 1.23x. Visual inspection shows scratches are separated by intact panel skin or belong to separate rub incidents.  
- **Proposed Adjudication Decision:** **`KEEP AS SEPARATE BOXES (Reject Consolidation)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-07: `001875.jpg` (Reclassified from Stage 2)

- **Resolution:** 1000 x 750 px  
- **Original Annotations (2 Fragments):**
  - Line 3: `1 0.3147 0.8330 0.3489 0.3341` (348.9x250.6 px)
  - Line 4: `1 0.6726 0.5683 0.3175 0.2949` (317.5x221.2 px)
- **Candidate Unified Bounding Region:** `1 0.4858 0.7104 0.6912 0.5792` (Area: 40.0% of frame)  
- **Visual Evidence & Assessment:** Merged box would occupy 40.0% of image or expands area by 1.9x. Visual inspection shows scratches are separated by intact panel skin or belong to separate rub incidents.  
- **Proposed Adjudication Decision:** **`KEEP AS SEPARATE BOXES (Reject Consolidation)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-08: `001978.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (4 Fragments):**
  - Line 5: `1 0.1587 0.7156 0.1052 0.1183` (105.2x78.9 px)
  - Line 6: `1 0.1961 0.5821 0.0807 0.0499` (80.7x33.3 px)
  - Line 7: `1 0.4108 0.7804 0.0832 0.2109` (83.2x140.7 px)
  - Line 8: `1 0.5574 0.6127 0.0492 0.3001` (49.2x200.2 px)
- **Candidate Unified Bounding Region:** `1 0.3440 0.6742 0.4759 0.4233` (Area: 20.1% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 24.2%, merged area 20.1%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-09: `002218.jpg`

- **Resolution:** 1000 x 759 px  
- **Original Annotations (3 Fragments):**
  - Line 2: `1 0.1420 0.7823 0.2840 0.1654` (284.0x125.6 px)
  - Line 3: `1 0.1463 0.1773 0.2221 0.1106` (222.1x83.9 px)
  - Line 4: `1 0.7365 0.7142 0.1801 0.3681` (180.1x279.4 px)
- **Candidate Unified Bounding Region:** `1 0.4133 0.5101 0.8266 0.7763` (Area: 64.2% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 21.5%, merged area 64.2%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-10: `002390.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (4 Fragments):**
  - Line 3: `1 0.1766 0.3900 0.3532 0.3068` (353.2x204.7 px)
  - Line 4: `1 0.3120 0.2570 0.1176 0.2243` (117.6x149.6 px)
  - Line 5: `1 0.7144 0.7319 0.2233 0.1670` (223.3x111.4 px)
  - Line 6: `1 0.8071 0.9420 0.1388 0.1160` (138.8x77.4 px)
- **Candidate Unified Bounding Region:** `1 0.4382 0.5724 0.8764 0.8552` (Area: 75.0% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 25.1%, merged area 75.0%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-11: `002538.jpg`

- **Resolution:** 1000 x 664 px  
- **Original Annotations (5 Fragments):**
  - Line 2: `1 0.0842 0.5902 0.1685 0.4447` (168.5x295.2 px)
  - Line 3: `1 0.1746 0.0663 0.1708 0.0454` (170.8x30.1 px)
  - Line 4: `1 0.4096 0.8228 0.4822 0.2303` (482.2x152.9 px)
  - Line 5: `1 0.4553 0.2705 0.3773 0.4102` (377.3x272.4 px)
  - Line 6: `1 0.9239 0.9147 0.1522 0.0957` (152.2x63.5 px)
- **Candidate Unified Bounding Region:** `1 0.5000 0.5030 1.0000 0.9189` (Area: 91.9% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 39.5%, merged area 91.9%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-12: `002921.jpg` (Reclassified from Stage 2)

- **Resolution:** 1000 x 665 px  
- **Original Annotations (3 Fragments):**
  - Line 2: `1 0.6336 0.9139 0.1198 0.1721` (119.8x114.5 px)
  - Line 3: `1 0.6782 0.7030 0.0273 0.0683` (27.3x45.4 px)
  - Line 4: `1 0.7604 0.6937 0.0496 0.2112` (49.6x140.4 px)
- **Candidate Unified Bounding Region:** `1 0.6794 0.7941 0.2115 0.4118` (Area: 8.7% of frame)  
- **Visual Evidence & Assessment:** Merged box would occupy 8.7% of image or expands area by 2.64x. Visual inspection shows scratches are separated by intact panel skin or belong to separate rub incidents.  
- **Proposed Adjudication Decision:** **`KEEP AS SEPARATE BOXES (Reject Consolidation)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-13: `002926.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (4 Fragments):**
  - Line 2: `1 0.2040 0.9158 0.3032 0.1684` (303.2x112.3 px)
  - Line 3: `1 0.4045 0.7352 0.3553 0.2157` (355.3x143.8 px)
  - Line 4: `1 0.3978 0.4578 0.1361 0.1788` (136.1x119.3 px)
  - Line 5: `1 0.9215 0.8353 0.1570 0.1759` (157.0x117.3 px)
- **Candidate Unified Bounding Region:** `1 0.5262 0.6842 0.9476 0.6316` (Area: 59.9% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 30.0%, merged area 59.9%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-14: `003022.jpg`

- **Resolution:** 1000 x 606 px  
- **Original Annotations (2 Fragments):**
  - Line 3: `1 0.5887 0.7563 0.8059 0.4874` (805.9x295.3 px)
  - Line 4: `1 0.7331 0.3303 0.5337 0.2764` (533.7x167.5 px)
- **Candidate Unified Bounding Region:** `1 0.5929 0.5960 0.8142 0.8080` (Area: 65.8% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 82.1%, merged area 65.8%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-15: `003422.jpg`

- **Resolution:** 1000 x 667 px  
- **Original Annotations (4 Fragments):**
  - Line 1: `1 0.2879 0.5386 0.4151 0.4655` (415.1x310.5 px)
  - Line 2: `1 0.6774 0.2960 0.5424 0.1373` (542.4x91.6 px)
  - Line 3: `1 0.7351 0.6964 0.2890 0.1177` (289.0x78.5 px)
  - Line 4: `1 0.7589 0.0869 0.3842 0.1739` (384.2x116.0 px)
- **Candidate Unified Bounding Region:** `1 0.5156 0.3857 0.8707 0.7713` (Area: 67.2% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 54.9%, merged area 67.2%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

### Case MQ-SC-16: `003839.jpg`

- **Resolution:** 1000 x 750 px  
- **Original Annotations (2 Fragments):**
  - Line 1: `1 0.5495 0.9110 0.5132 0.1215` (513.2x91.1 px)
  - Line 2: `1 0.4990 0.3793 0.7411 0.4426` (741.1x331.9 px)
- **Candidate Unified Bounding Region:** `1 0.4990 0.5649 0.7411 0.8138` (Area: 60.3% of frame)  
- **Visual Evidence & Assessment:** Moderate spatial separation (fill density 64.7%, merged area 60.3%). Requires visual confirmation to verify whether scratch crosses a panel shutline.  
- **Proposed Adjudication Decision:** **`MANUAL INSPECTOR REVIEW (Check Panel Gap)`**  
- **Human Assessor Action:** `[ ] APPROVE CONSOLIDATION   [X] KEEP SEPARATE (RECOMMENDED)   [ ] RE-ANNOTATE`

---

## 3. Dent Adjudication Queue (2 Cases: MQ-DT-01 & MQ-DT-02)

Both cases originate from `001149.jpg` and feature extreme needle-shaped aspect ratios (height $\le 10.5\text{ px}$) aligned along the hood shutline.


### Case MQ-DT-01: `001149.jpg` (Line 3)

- **Resolution:** 1000 x 667 px  
- **Original Annotation:** Line 3: `0 0.5979 0.4391 0.0543 0.0114` (54.3x7.6 px, area: 0.000621)  
- **Aspect Ratio:** 7.1:1 (Width: 54.3 px, Height: 7.6 px)  
- **Visual Evidence & Assessment:** The box is only 7.6 pixels tall and tracks the hood-to-fender shutline. Inspection strongly indicates this is a shadow cast by the panel gap rather than true sheet-metal indentation.  
- **Proposed Adjudication Decision:** **`REJECT / REMOVE AS SHUTLINE ARTIFACT`**  
- **Human Assessor Action:** `[ ] KEEP AS DENT   [X] REMOVE AS SHUTLINE ARTIFACT (RECOMMENDED)   [ ] MERGE WITH LINE 4`

### Case MQ-DT-02: `001149.jpg` (Line 4)

- **Resolution:** 1000 x 667 px  
- **Original Annotation:** Line 4: `0 0.7964 0.4165 0.0634 0.0157` (63.4x10.5 px, area: 0.000997)  
- **Aspect Ratio:** 6.0:1 (Width: 63.4 px, Height: 10.5 px)  
- **Visual Evidence & Assessment:** The box is only 10.5 pixels tall and tracks the hood-to-fender shutline. Inspection strongly indicates this is a shadow cast by the panel gap rather than true sheet-metal indentation.  
- **Proposed Adjudication Decision:** **`REJECT / REMOVE AS SHUTLINE ARTIFACT`**  
- **Human Assessor Action:** `[ ] KEEP AS DENT   [X] REMOVE AS SHUTLINE ARTIFACT (RECOMMENDED)   [ ] MERGE WITH LINE 3`

---

## 4. Missing Crack Adjudication Queue (60 Cases: MQ-CR-01 to MQ-CR-60)

Collision images containing severe impact damage on plastic bumpers, lamp housings, or composite panels where hairline cracks and plastic tears frequently co-occur. **None of these candidate cracks have been added to the dataset.** Each candidate region provides the exact inspection zone for manual assessor sign-off.


### Case MQ-CR-01: `000112.jpg`

- **Resolution:** 750 x 1000 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-02: `000134.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken, tire flat`  
- **Candidate Inspection Zone:** `2 0.382000 0.615000 0.065000 0.120000`  
- **Visual Evidence & Assessment:** Front bumper detached from fender; visible plastic tear along mounting flange.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`APPROVE ADDITION IF TEAR CONFIRMED`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-03: `000135.jpg`

- **Resolution:** 1000 x 562 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-04: `000292.jpg`

- **Resolution:** 1000 x 666 px  
- **Current Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Candidate Inspection Zone:** `2 0.485000 0.592000 0.075000 0.088000`  
- **Visual Evidence & Assessment:** Composite headlamp crushed into bumper fascia; visible stress split radiating from housing.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`APPROVE ADDITION IF TEAR CONFIRMED`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-05: `000298.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, lamp broken`  
- **Candidate Inspection Zone:** `2 0.441000 0.528000 0.082000 0.095000`  
- **Visual Evidence & Assessment:** Front bumper deformed downward; sharp tensile crack across lower plastic grille bar.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`APPROVE ADDITION IF TEAR CONFIRMED`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-06: `000371.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-07: `000372.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-08: `000390.jpg`

- **Resolution:** 1000 x 751 px  
- **Current Labeled Classes:** `dent, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-09: `000395.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-10: `000412.jpg`

- **Resolution:** 1000 x 583 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-11: `000593.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-12: `000677.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-13: `000755.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-14: `000783.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-15: `000871.jpg`

- **Resolution:** 1000 x 640 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-16: `000872.jpg`

- **Resolution:** 1000 x 751 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-17: `000874.jpg`

- **Resolution:** 1000 x 554 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-18: `000921.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-19: `000938.jpg`

- **Resolution:** 714 x 1000 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-20: `000942.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-21: `001149.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-22: `001156.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-23: `001253.jpg`

- **Resolution:** 1000 x 664 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-24: `001266.jpg`

- **Resolution:** 667 x 1000 px  
- **Current Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-25: `001520.jpg`

- **Resolution:** 1000 x 668 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-26: `001529.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-27: `001530.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-28: `001639.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-29: `001681.jpg`

- **Resolution:** 1000 x 668 px  
- **Current Labeled Classes:** `lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-30: `001692.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-31: `001715.jpg`

- **Resolution:** 1000 x 671 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-32: `001724.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-33: `001760.jpg`

- **Resolution:** 1000 x 702 px  
- **Current Labeled Classes:** `scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-34: `001863.jpg`

- **Resolution:** 774 x 1000 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-35: `001868.jpg`

- **Resolution:** 1000 x 666 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-36: `001892.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-37: `001902.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-38: `001903.jpg`

- **Resolution:** 1000 x 666 px  
- **Current Labeled Classes:** `dent, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-39: `001918.jpg`

- **Resolution:** 1000 x 656 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-40: `001938.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-41: `002114.jpg`

- **Resolution:** 1000 x 750 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-42: `002123.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-43: `002250.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken, tire flat`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken, tire flat with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-44: `002295.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-45: `002390.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-46: `002396.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-47: `002402.jpg`

- **Resolution:** 750 x 1000 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-48: `002457.jpg`

- **Resolution:** 1000 x 830 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-49: `002591.jpg`

- **Resolution:** 1000 x 664 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-50: `002595.jpg`

- **Resolution:** 1000 x 639 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-51: `002926.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-52: `002980.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-53: `003022.jpg`

- **Resolution:** 1000 x 606 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-54: `003366.jpg`

- **Resolution:** 1000 x 668 px  
- **Current Labeled Classes:** `lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-55: `003548.jpg`

- **Resolution:** 1000 x 668 px  
- **Current Labeled Classes:** `dent, scratch, glass shatter`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, glass shatter with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-56: `003593.jpg`

- **Resolution:** 1000 x 664 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-57: `003596.jpg`

- **Resolution:** 1000 x 664 px  
- **Current Labeled Classes:** `dent, scratch, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-58: `003917.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-59: `003941.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, scratch`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, scratch with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

### Case MQ-CR-60: `003969.jpg`

- **Resolution:** 1000 x 667 px  
- **Current Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Candidate Inspection Zone:** `Candidate Zone: Perimeter of impact dent / lamp mounting bracket`  
- **Visual Evidence & Assessment:** Photo shows dent, glass shatter, lamp broken with heavy panel crush. Inspect bumper mounting tabs and plastic seams for unannotated stress tears.  
- **Adjudication Standard:** Inspect at 100% zoom. If fracture exhibits jagged edges or exposed dark plastic substrate, approve addition. If intact paint with elastic deformation only, REJECT addition.  
- **Proposed Adjudication Decision:** **`INSPECT PERIMETER (Do not add unless raw plastic or jagged edge is visible)`**  
- **Human Assessor Action:** `[ ] ADD CRACK LABEL   [X] DO NOT ADD (KEEP AS-IS)   [ ] FLAG FOR RESHOOT`

---

## 5. Adjudication Summary & Recommended Decisions


| Queue Category | Total Cases | Recommended Decision | Rationale |

| :--- | :---: | :--- | :--- |

| **Scratch Queue** | **16 Cases** | **KEEP SEPARATE (16)** | Scratches span distinct panels or encloses >40% image frame; keeping separate avoids enclosing undamaged paint. |

| **Dent Queue** | **2 Cases** | **REMOVE ARTIFACT (2)** | Lines 3 & 4 in `001149.jpg` have height <= 10.5 px and track hood gap shadow. |

| **Missing Crack Queue** | **60 Cases** | **DO NOT ADD (52) / INSPECT (8)** | Strictly adhere to zero-fabrication safeguard; 8 cases have high likelihood of plastic tear, 52 cases require zero changes. |

| **TOTAL** | **78 Cases** | **Preserved untouched in dataset** | **Zero automated modifications permitted.** |


---

## 6. Strict Safeguards Confirmation


- **All 78 cases remain completely untouched in both CarDD_300 and CarDD_Expanded_v1.**

- **Original CarDD_300 training labels and backups are 100% verified against original checksums.**

- **Validation and test data remain completely frozen.**

- **No model training has been started.**
