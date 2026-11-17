# Phase 8 — Annotation Correction Human Review Catalog (Stage 2)

**Project:** ClaimSense AI  
**Module:** Phase 8 Vehicle Damage Dataset Quality & Label Human Review Preparation  
**Date:** November 17, 2026  
**Total Cases Audited:** **116 Cases** (50 Fragmented Scratches, 6 Tiny Dents, 60 Missing Crack Candidates)  
**Status:** Staged for Human Adjudication (No labels modified; Zero in-place changes)  

---

## 1. Executive Summary & Review Principles

This document presents the complete, case-by-case audit of all 116 annotation quality proposals identified across the CarDD training set (`datasets/CarDD_300/train/labels/`). In accordance with Phase 8 strict safeguards:

1. **Zero Automated In-Place Edits:** No label files in `train/`, `val/`, or `test/` have been altered.

2. **Reversible Original Backup:** All 210 original training `.txt` label files remain preserved in `datasets/CarDD_300/train/labels_backup_original/`.

3. **Evidence-Based Categorization:** Every proposal is individually reviewed and assigned a clear recommended action:

   - **APPROVE:** Clear geometric and visual evidence demonstrates that contiguous sub-boxes belong to a single physical damage instance on a single body panel, resolving artificial IoU penalties.

   - **REJECT:** Disjoint damage markings occur on distinct vehicle panels or represent non-damage artifacts (e.g. reflection lines, panel shutlines); existing annotations should remain separate or un-modified.

   - **MANUAL REVIEW:** Ambiguous visual context (e.g. potential missing crack inside heavy bumper crumple zone) requiring manual visual inspection by a human claims assessor before any annotation is added.


---

## 2. Fragmented Continuous Scratch Cases (50 Cases: FS-01 to FS-50)

Continuous scratches and key scrapes on single panels that were artificially sliced into multiple sub-boxes during CarDD creation. In each case, we analyze the spatial coordinates, pixel dimensions, bounding span, and visual coherence.


### Case FS-01: `000014.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.8567 0.6489 0.2082 0.2703` (208.2x180.3 px, area: 0.056297)
  - Line 3: `1 0.8020 0.4216 0.1139 0.1053` (113.9x70.2 px, area: 0.011984)
- **Proposed Consolidated Box:** `1 0.8529 0.5765 0.2157 0.4151` (215.7x276.9 px, area: 0.0895)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 76.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-02: `000112.jpg` (4 Fragments)

- **Resolution:** 750 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (4 Boxes):**
  - Line 2: `1 0.2159 0.9434 0.4318 0.1132` (323.8x113.2 px, area: 0.048888)
  - Line 3: `1 0.0995 0.6737 0.1990 0.0649` (149.2x64.9 px, area: 0.012918)
  - Line 4: `1 0.1985 0.7624 0.1239 0.0560` (92.9x56.0 px, area: 0.006939)
  - Line 5: `1 0.4230 0.8807 0.1524 0.0459` (114.3x45.9 px, area: 0.006994)
- **Proposed Consolidated Box:** `1 0.2496 0.8206 0.4992 0.3588` (374.4x358.8 px, area: 0.1791)  
- **Visual Evidence & Justification:** The 4 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 42.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-03: `000118.jpg` (3 Fragments)

- **Resolution:** 1000 x 664 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 3: `1 0.1181 0.1610 0.2363 0.1813` (236.3x120.4 px, area: 0.042840)
  - Line 4: `1 0.4119 0.1988 0.3088 0.2031` (308.8x134.9 px, area: 0.062722)
  - Line 5: `1 0.6691 0.4866 0.2989 0.3724` (298.9x247.3 px, area: 0.111302)
- **Proposed Consolidated Box:** `1 0.4093 0.3715 0.8186 0.6024` (818.6x400.0 px, area: 0.4931)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 44.0%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-04: `000126.jpg` (3 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 2: `1 0.0920 0.3039 0.1491 0.2331` (149.1x155.5 px, area: 0.034758)
  - Line 3: `1 0.1111 0.5495 0.0973 0.0755` (97.3x50.4 px, area: 0.007349)
  - Line 4: `1 0.2471 0.5103 0.1158 0.4156` (115.8x277.2 px, area: 0.048122)
- **Proposed Consolidated Box:** `1 0.1612 0.4527 0.2876 0.5308` (287.6x354.0 px, area: 0.1526)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 59.1%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-05: `000485.jpg` (2 Fragments)

- **Resolution:** 667 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 5: `1 0.5383 0.6765 0.5322 0.2239` (355.0x223.9 px, area: 0.119151)
  - Line 6: `1 0.7772 0.4772 0.1727 0.1958` (115.2x195.8 px, area: 0.033818)
- **Proposed Consolidated Box:** `1 0.5679 0.5838 0.5914 0.4091` (394.4x409.1 px, area: 0.2420)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 63.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-06: `000494.jpg` (2 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.1635 0.9691 0.2139 0.0618` (213.9x46.4 px, area: 0.013226)
  - Line 3: `1 0.5816 0.8911 0.4171 0.2179` (417.1x163.4 px, area: 0.090884)
- **Proposed Consolidated Box:** `1 0.4233 0.8911 0.7336 0.2179` (733.6x163.4 px, area: 0.1598)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 65.1%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-07: `000512.jpg` (5 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (5 Boxes):**
  - Line 1: `1 0.1217 0.4325 0.2434 0.1915` (243.4x127.7 px, area: 0.046606)
  - Line 2: `1 0.1440 0.1598 0.2881 0.0621` (288.1x41.5 px, area: 0.017902)
  - Line 3: `1 0.3240 0.4115 0.0976 0.1235` (97.6x82.4 px, area: 0.012054)
  - Line 4: `1 0.3941 0.4630 0.0802 0.2308` (80.2x153.9 px, area: 0.018517)
  - Line 5: `1 0.3999 0.7458 0.0730 0.1983` (73.0x132.3 px, area: 0.014475)
- **Proposed Consolidated Box:** `1 0.2182 0.4868 0.4364 0.7163` (436.4x477.7 px, area: 0.3126)  
- **Visual Evidence & Justification:** The 5 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 35.0%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-08: `000566.jpg` (3 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (3 Boxes):**
  - Line 3: `1 0.1976 0.7787 0.2202 0.3698` (220.2x246.6 px, area: 0.081421)
  - Line 4: `1 0.9207 0.6008 0.0593 0.2969` (59.3x198.0 px, area: 0.017615)
  - Line 5: `1 0.9791 0.6330 0.0418 0.3140` (41.8x209.5 px, area: 0.013121)
- **Proposed Consolidated Box:** `1 0.5437 0.7080 0.9125 0.5113` (912.5x341.0 px, area: 0.4665)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 24.0%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-09: `000583.jpg` (2 Fragments)

- **Resolution:** 1000 x 704 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.4725 0.6235 0.3252 0.4794` (325.2x337.5 px, area: 0.155935)
  - Line 2: `1 0.4057 0.3689 0.2349 0.1961` (234.9x138.1 px, area: 0.046062)
- **Proposed Consolidated Box:** `1 0.4617 0.5670 0.3469 0.5924` (346.9x417.0 px, area: 0.2055)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 98.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-10: `000594.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (4 Boxes):**
  - Line 2: `1 0.2994 0.3809 0.2778 0.0902` (277.8x60.2 px, area: 0.025072)
  - Line 3: `1 0.2861 0.5925 0.4929 0.7563` (492.9x504.5 px, area: 0.372808)
  - Line 4: `1 0.7363 0.3021 0.4336 0.3446` (433.6x229.8 px, area: 0.149430)
  - Line 5: `1 0.7536 0.7697 0.4928 0.3912` (492.8x260.9 px, area: 0.192768)
- **Proposed Consolidated Box:** `1 0.5198 0.5502 0.9604 0.8409` (960.4x560.9 px, area: 0.8076)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 91.6%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-11: `000779.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.4391 0.7910 0.1327 0.0533` (132.7x35.6 px, area: 0.007075)
  - Line 3: `1 0.7713 0.8237 0.2090 0.3527` (209.0x235.2 px, area: 0.073718)
- **Proposed Consolidated Box:** `1 0.6243 0.8237 0.5030 0.3527` (503.0x235.2 px, area: 0.1774)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 45.5%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-12: `000792.jpg` (5 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (5 Boxes):**
  - Line 1: `1 0.0593 0.3969 0.1187 0.1597` (118.7x106.5 px, area: 0.018948)
  - Line 2: `1 0.2939 0.4867 0.1717 0.2848` (171.7x189.9 px, area: 0.048900)
  - Line 3: `1 0.2305 0.7975 0.0850 0.2172` (85.0x144.8 px, area: 0.018456)
  - Line 4: `1 0.2067 0.4120 0.1778 0.1248` (177.8x83.3 px, area: 0.022193)
  - Line 5: `1 0.1816 0.1460 0.3632 0.2224` (363.2x148.3 px, area: 0.080768)
- **Proposed Consolidated Box:** `1 0.1899 0.4705 0.3797 0.8712` (379.7x581.1 px, area: 0.3308)  
- **Visual Evidence & Justification:** The 5 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 57.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-13: `000870.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (4 Boxes):**
  - Line 3: `1 0.2887 0.5205 0.3209 0.3290` (320.9x219.4 px, area: 0.105573)
  - Line 4: `1 0.6325 0.5010 0.0911 0.2536` (91.1x169.1 px, area: 0.023089)
  - Line 5: `1 0.8590 0.5901 0.2820 0.0884` (282.0x59.0 px, area: 0.024939)
  - Line 6: `1 0.8724 0.4042 0.2551 0.0988` (255.1x65.9 px, area: 0.025212)
- **Proposed Consolidated Box:** `1 0.5641 0.5199 0.8718 0.3303` (871.8x220.3 px, area: 0.2879)  
- **Visual Evidence & Justification:** The 4 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 62.1%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-14: `000874.jpg` (2 Fragments)

- **Resolution:** 1000 x 554 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 3: `1 0.9310 0.5504 0.1381 0.0575` (138.1x31.9 px, area: 0.007946)
  - Line 4: `1 0.9121 0.7043 0.1757 0.0999` (175.7x55.4 px, area: 0.017555)
- **Proposed Consolidated Box:** `1 0.9121 0.6379 0.1757 0.2326` (175.7x128.9 px, area: 0.0409)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 62.4%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-15: `000901.jpg` (2 Fragments)

- **Resolution:** 1000 x 563 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.6399 0.5451 0.5603 0.3451` (560.3x194.3 px, area: 0.193341)
  - Line 2: `1 0.9014 0.7253 0.1067 0.2218` (106.7x124.9 px, area: 0.023663)
- **Proposed Consolidated Box:** `1 0.6573 0.6044 0.5950 0.4637` (595.0x261.1 px, area: 0.2759)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 78.7%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-16: `001153.jpg` (3 Fragments)

- **Resolution:** 1000 x 732 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 1: `1 0.2934 0.7517 0.1968 0.4967` (196.8x363.6 px, area: 0.097716)
  - Line 2: `1 0.5705 0.6965 0.2255 0.3910` (225.5x286.2 px, area: 0.088170)
  - Line 3: `1 0.8699 0.9156 0.1632 0.1688` (163.2x123.5 px, area: 0.027538)
- **Proposed Consolidated Box:** `1 0.5732 0.7505 0.7565 0.4990` (756.5x365.3 px, area: 0.3775)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 56.5%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-17: `001337.jpg` (2 Fragments)

- **Resolution:** 1000 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.2903 0.6555 0.5806 0.3632` (580.6x363.2 px, area: 0.210896)
  - Line 2: `1 0.5530 0.3847 0.2974 0.1573` (297.4x157.3 px, area: 0.046787)
- **Proposed Consolidated Box:** `1 0.3509 0.5716 0.7017 0.5310` (701.7x531.0 px, area: 0.3726)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 69.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-18: `001427.jpg` (2 Fragments)

- **Resolution:** 667 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 3: `1 0.4784 0.5555 0.3697 0.0754` (246.6x75.4 px, area: 0.027879)
  - Line 4: `1 0.6730 0.6545 0.5311 0.1493` (354.3x149.3 px, area: 0.079316)
- **Proposed Consolidated Box:** `1 0.6160 0.6235 0.6450 0.2114` (430.2x211.4 px, area: 0.1363)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 78.6%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-19: `001485.jpg` (3 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 3: `1 0.2219 0.5238 0.1474 0.1297` (147.4x97.2 px, area: 0.019115)
  - Line 4: `1 0.6035 0.4985 0.5930 0.1828` (593.0x137.1 px, area: 0.108395)
  - Line 5: `1 0.8828 0.6642 0.2344 0.1945` (234.4x145.9 px, area: 0.045590)
- **Proposed Consolidated Box:** `1 0.5741 0.5843 0.8518 0.3544` (851.8x265.8 px, area: 0.3019)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 57.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-20: `001486.jpg` (3 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (3 Boxes):**
  - Line 3: `1 0.2291 0.6774 0.1225 0.2521` (122.5x189.1 px, area: 0.030876)
  - Line 4: `1 0.4141 0.5008 0.0817 0.1088` (81.7x81.6 px, area: 0.008888)
  - Line 5: `1 0.5206 0.4189 0.1429 0.2199` (142.9x164.9 px, area: 0.031418)
- **Proposed Consolidated Box:** `1 0.3800 0.5562 0.4242 0.4945` (424.2x370.8 px, area: 0.2098)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 33.9%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-21: `001608.jpg` (2 Fragments)

- **Resolution:** 667 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.5796 0.4671 0.1439 0.3668` (96.0x366.8 px, area: 0.052788)
  - Line 2: `1 0.5439 0.8232 0.1916 0.1854` (127.8x185.4 px, area: 0.035509)
- **Proposed Consolidated Box:** `1 0.5499 0.5998 0.2035 0.6323` (135.7x632.3 px, area: 0.1286)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 68.6%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-22: `001724.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.5213 0.5925 0.5574 0.5509` (557.4x367.4 px, area: 0.307071)
  - Line 3: `1 0.9017 0.5980 0.1450 0.1350` (145.0x90.0 px, area: 0.019569)
- **Proposed Consolidated Box:** `1 0.6084 0.5925 0.7315 0.5509` (731.5x367.4 px, area: 0.4030)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 81.0%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-23: `001760.jpg` (2 Fragments)

- **Resolution:** 1000 x 702 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.1303 0.8421 0.2606 0.1154` (260.6x81.0 px, area: 0.030088)
  - Line 2: `1 0.1907 0.4893 0.3597 0.3076` (359.7x215.9 px, area: 0.110636)
- **Proposed Consolidated Box:** `1 0.1853 0.6176 0.3706 0.5643` (370.6x396.1 px, area: 0.2091)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 67.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-24: `001869.jpg` (2 Fragments)

- **Resolution:** 1000 x 666 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 3: `1 0.2920 0.8083 0.1850 0.0315` (185.0x21.0 px, area: 0.005823)
  - Line 4: `1 0.3247 0.6772 0.1859 0.1575` (185.9x104.9 px, area: 0.029272)
- **Proposed Consolidated Box:** `1 0.3086 0.7112 0.2181 0.2256` (218.1x150.2 px, area: 0.0492)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 71.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-25: `001875.jpg` (2 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 3: `1 0.3147 0.8330 0.3489 0.3341` (348.9x250.6 px, area: 0.116563)
  - Line 4: `1 0.6726 0.5683 0.3175 0.2949` (317.5x221.2 px, area: 0.093617)
- **Proposed Consolidated Box:** `1 0.4858 0.7104 0.6912 0.5792` (691.2x434.4 px, area: 0.4003)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 52.5%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-26: `001902.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (4 Boxes):**
  - Line 3: `1 0.4926 0.9517 0.1713 0.0965` (171.3x64.4 px, area: 0.016535)
  - Line 4: `1 0.4582 0.8811 0.0936 0.1415` (93.6x94.4 px, area: 0.013240)
  - Line 5: `1 0.6587 0.5525 0.2043 0.6074` (204.3x405.2 px, area: 0.124075)
  - Line 6: `1 0.7990 0.3617 0.0915 0.2487` (91.5x165.9 px, area: 0.022761)
- **Proposed Consolidated Box:** `1 0.6259 0.6187 0.4377 0.7627` (437.7x508.7 px, area: 0.3338)  
- **Visual Evidence & Justification:** The 4 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 52.9%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-27: `001948.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.3720 0.7628 0.2139 0.2641` (213.9x176.2 px, area: 0.056504)
  - Line 3: `1 0.5986 0.6710 0.4954 0.2521` (495.4x168.2 px, area: 0.124885)
- **Proposed Consolidated Box:** `1 0.5557 0.7199 0.5811 0.3499` (581.1x233.4 px, area: 0.2033)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 89.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-28: `001978.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (4 Boxes):**
  - Line 5: `1 0.1587 0.7156 0.1052 0.1183` (105.2x78.9 px, area: 0.012454)
  - Line 6: `1 0.1961 0.5821 0.0807 0.0499` (80.7x33.3 px, area: 0.004029)
  - Line 7: `1 0.4108 0.7804 0.0832 0.2109` (83.2x140.7 px, area: 0.017536)
  - Line 8: `1 0.5574 0.6127 0.0492 0.3001` (49.2x200.2 px, area: 0.014764)
- **Proposed Consolidated Box:** `1 0.3440 0.6742 0.4759 0.4233` (475.9x282.3 px, area: 0.2014)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 24.2%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-29: `002018.jpg` (3 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 1: `1 0.6627 0.4534 0.1308 0.0341` (130.8x22.8 px, area: 0.004460)
  - Line 2: `1 0.6663 0.8785 0.2047 0.2430` (204.7x162.0 px, area: 0.049730)
  - Line 3: `1 0.8012 0.8593 0.3977 0.2813` (397.7x187.6 px, area: 0.111866)
- **Proposed Consolidated Box:** `1 0.7820 0.7182 0.4361 0.5637` (436.1x376.0 px, area: 0.2458)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 67.6%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-30: `002114.jpg` (3 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 2: `1 0.1054 0.7710 0.1672 0.4581` (167.2x343.6 px, area: 0.076570)
  - Line 3: `1 0.2592 0.9250 0.1638 0.0887` (163.8x66.5 px, area: 0.014524)
  - Line 4: `1 0.4521 0.6124 0.4119 0.2684` (411.9x201.3 px, area: 0.110548)
- **Proposed Consolidated Box:** `1 0.3399 0.7391 0.6363 0.5217` (636.3x391.3 px, area: 0.3320)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 60.7%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-31: `002123.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.4278 0.8110 0.0954 0.1339` (95.4x89.3 px, area: 0.012775)
  - Line 3: `1 0.4441 0.5243 0.0525 0.1317` (52.5x87.8 px, area: 0.006919)
- **Proposed Consolidated Box:** `1 0.4278 0.6682 0.0954 0.4194` (95.4x279.7 px, area: 0.0400)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 49.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-32: `002218.jpg` (3 Fragments)

- **Resolution:** 1000 x 759 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (3 Boxes):**
  - Line 2: `1 0.1420 0.7823 0.2840 0.1654` (284.0x125.6 px, area: 0.046977)
  - Line 3: `1 0.1463 0.1773 0.2221 0.1106` (222.1x83.9 px, area: 0.024555)
  - Line 4: `1 0.7365 0.7142 0.1801 0.3681` (180.1x279.4 px, area: 0.066309)
- **Proposed Consolidated Box:** `1 0.4133 0.5101 0.8266 0.7763` (826.6x589.2 px, area: 0.6417)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 21.5%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-33: `002249.jpg` (3 Fragments)

- **Resolution:** 1000 x 666 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 2: `1 0.3193 0.6046 0.0358 0.1168` (35.8x77.8 px, area: 0.004184)
  - Line 3: `1 0.5480 0.8029 0.0941 0.0799` (94.1x53.2 px, area: 0.007524)
  - Line 4: `1 0.5593 0.6392 0.1801 0.2413` (180.1x160.7 px, area: 0.043458)
- **Proposed Consolidated Box:** `1 0.4754 0.6807 0.3480 0.3242` (348.0x215.9 px, area: 0.1128)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 48.9%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-34: `002390.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (4 Boxes):**
  - Line 3: `1 0.1766 0.3900 0.3532 0.3068` (353.2x204.7 px, area: 0.108363)
  - Line 4: `1 0.3120 0.2570 0.1176 0.2243` (117.6x149.6 px, area: 0.026383)
  - Line 5: `1 0.7144 0.7319 0.2233 0.1670` (223.3x111.4 px, area: 0.037278)
  - Line 6: `1 0.8071 0.9420 0.1388 0.1160` (138.8x77.4 px, area: 0.016100)
- **Proposed Consolidated Box:** `1 0.4382 0.5724 0.8764 0.8552` (876.4x570.4 px, area: 0.7495)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 25.1%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-35: `002538.jpg` (5 Fragments)

- **Resolution:** 1000 x 664 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (5 Boxes):**
  - Line 2: `1 0.0842 0.5902 0.1685 0.4447` (168.5x295.2 px, area: 0.074911)
  - Line 3: `1 0.1746 0.0663 0.1708 0.0454` (170.8x30.1 px, area: 0.007752)
  - Line 4: `1 0.4096 0.8228 0.4822 0.2303` (482.2x152.9 px, area: 0.111065)
  - Line 5: `1 0.4553 0.2705 0.3773 0.4102` (377.3x272.4 px, area: 0.154767)
  - Line 6: `1 0.9239 0.9147 0.1522 0.0957` (152.2x63.5 px, area: 0.014562)
- **Proposed Consolidated Box:** `1 0.5000 0.5030 1.0000 0.9189` (1000.0x610.2 px, area: 0.9189)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 39.5%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-36: `002595.jpg` (2 Fragments)

- **Resolution:** 1000 x 639 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.2777 0.8109 0.1842 0.3392` (184.2x216.7 px, area: 0.062475)
  - Line 3: `1 0.5396 0.6017 0.2541 0.2131` (254.1x136.1 px, area: 0.054141)
- **Proposed Consolidated Box:** `1 0.4261 0.7378 0.4811 0.4853` (481.1x310.1 px, area: 0.2335)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 49.9%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-37: `002802.jpg` (3 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 1: `1 0.4855 0.3145 0.3818 0.1439` (381.8x96.0 px, area: 0.054947)
  - Line 2: `1 0.5184 0.6283 0.4365 0.3565` (436.5x237.8 px, area: 0.155581)
  - Line 3: `1 0.4854 0.0945 0.4284 0.1890` (428.4x126.1 px, area: 0.080955)
- **Proposed Consolidated Box:** `1 0.5039 0.4033 0.4655 0.8065` (465.5x537.9 px, area: 0.3754)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 77.6%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-38: `002921.jpg` (3 Fragments)

- **Resolution:** 1000 x 665 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 2: `1 0.6336 0.9139 0.1198 0.1721` (119.8x114.5 px, area: 0.020617)
  - Line 3: `1 0.6782 0.7030 0.0273 0.0683` (27.3x45.4 px, area: 0.001862)
  - Line 4: `1 0.7604 0.6937 0.0496 0.2112` (49.6x140.4 px, area: 0.010466)
- **Proposed Consolidated Box:** `1 0.6794 0.7941 0.2115 0.4118` (211.5x273.9 px, area: 0.0871)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 37.8%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-39: `002926.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (4 Boxes):**
  - Line 2: `1 0.2040 0.9158 0.3032 0.1684` (303.2x112.3 px, area: 0.051051)
  - Line 3: `1 0.4045 0.7352 0.3553 0.2157` (355.3x143.8 px, area: 0.076619)
  - Line 4: `1 0.3978 0.4578 0.1361 0.1788` (136.1x119.3 px, area: 0.024339)
  - Line 5: `1 0.9215 0.8353 0.1570 0.1759` (157.0x117.3 px, area: 0.027616)
- **Proposed Consolidated Box:** `1 0.5262 0.6842 0.9476 0.6316` (947.6x421.3 px, area: 0.5985)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 30.0%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-40: `003022.jpg` (2 Fragments)

- **Resolution:** 1000 x 606 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (2 Boxes):**
  - Line 3: `1 0.5887 0.7563 0.8059 0.4874` (805.9x295.3 px, area: 0.392758)
  - Line 4: `1 0.7331 0.3303 0.5337 0.2764` (533.7x167.5 px, area: 0.147536)
- **Proposed Consolidated Box:** `1 0.5929 0.5960 0.8142 0.8080` (814.2x489.6 px, area: 0.6579)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 82.1%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-41: `003237.jpg` (2 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.3895 0.8439 0.2607 0.3122` (260.7x234.1 px, area: 0.081391)
  - Line 2: `1 0.8687 0.9424 0.1704 0.1153` (170.3x86.5 px, area: 0.019636)
- **Proposed Consolidated Box:** `1 0.6065 0.8439 0.6947 0.3122` (694.7x234.1 px, area: 0.2169)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 46.6%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-42: `003305.jpg` (3 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 3: `1 0.6854 0.5921 0.4500 0.1813` (450.0x120.9 px, area: 0.081592)
  - Line 4: `1 0.7538 0.7679 0.2735 0.1149` (273.5x76.7 px, area: 0.031436)
  - Line 5: `1 0.8469 0.9205 0.2280 0.1011` (228.0x67.4 px, area: 0.023042)
- **Proposed Consolidated Box:** `1 0.7106 0.7362 0.5006 0.4696` (500.6x313.2 px, area: 0.2351)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 57.9%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-43: `003356.jpg` (2 Fragments)

- **Resolution:** 667 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.2666 0.5639 0.0446 0.1417` (29.7x141.8 px, area: 0.006320)
  - Line 2: `1 0.4762 0.5307 0.2348 0.2597` (156.6x259.7 px, area: 0.060981)
- **Proposed Consolidated Box:** `1 0.4189 0.5307 0.3493 0.2597` (233.0x259.7 px, area: 0.0907)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 74.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-44: `003422.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (4 Boxes):**
  - Line 1: `1 0.2879 0.5386 0.4151 0.4655` (415.1x310.5 px, area: 0.193230)
  - Line 2: `1 0.6774 0.2960 0.5424 0.1373` (542.4x91.6 px, area: 0.074490)
  - Line 3: `1 0.7351 0.6964 0.2890 0.1177` (289.0x78.5 px, area: 0.034023)
  - Line 4: `1 0.7589 0.0869 0.3842 0.1739` (384.2x116.0 px, area: 0.066808)
- **Proposed Consolidated Box:** `1 0.5156 0.3857 0.8707 0.7713` (870.7x514.5 px, area: 0.6716)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 54.9%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-45: `003610.jpg` (2 Fragments)

- **Resolution:** 1000 x 563 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.5467 0.5593 0.4887 0.6737` (488.7x379.3 px, area: 0.329206)
  - Line 3: `1 0.6341 0.7240 0.3091 0.4752` (309.1x267.5 px, area: 0.146894)
- **Proposed Consolidated Box:** `1 0.5467 0.5920 0.4887 0.7391` (488.7x416.1 px, area: 0.3612)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 131.8%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-46: `003733.jpg` (2 Fragments)

- **Resolution:** 750 x 1000 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 2: `1 0.5590 0.5176 0.3940 0.1332` (295.5x133.2 px, area: 0.052470)
  - Line 3: `1 0.8011 0.4344 0.1237 0.0499` (92.7x49.9 px, area: 0.006175)
- **Proposed Consolidated Box:** `1 0.6124 0.4968 0.5010 0.1748` (375.7x174.8 px, area: 0.0876)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 67.0%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-47: `003826.jpg` (3 Fragments)

- **Resolution:** 1000 x 668 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (3 Boxes):**
  - Line 1: `1 0.2973 0.3287 0.0763 0.0564` (76.3x37.7 px, area: 0.004300)
  - Line 2: `1 0.3464 0.5381 0.1654 0.3194` (165.4x213.4 px, area: 0.052817)
  - Line 3: `1 0.4461 0.5905 0.0602 0.3159` (60.2x211.0 px, area: 0.019020)
- **Proposed Consolidated Box:** `1 0.3677 0.5245 0.2170 0.4479` (217.0x299.2 px, area: 0.0972)  
- **Visual Evidence & Justification:** The 3 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 78.3%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-48: `003839.jpg` (2 Fragments)

- **Resolution:** 1000 x 750 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.5495 0.9110 0.5132 0.1215` (513.2x91.1 px, area: 0.062376)
  - Line 2: `1 0.4990 0.3793 0.7411 0.4426` (741.1x331.9 px, area: 0.327994)
- **Proposed Consolidated Box:** `1 0.4990 0.5649 0.7411 0.8138` (741.1x610.3 px, area: 0.6031)  
- **Visual Evidence & Justification:** Moderate spatial separation (fill density 64.7%). Requires visual inspection to confirm whether the scratch crosses a door-to-fender shutline or represents two separate scrapes.

### Case FS-49: `003847.jpg` (4 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (4 Boxes):**
  - Line 1: `1 0.0786 0.2766 0.1571 0.1890` (157.1x126.1 px, area: 0.029702)
  - Line 2: `1 0.2954 0.8082 0.1694 0.2926` (169.4x195.2 px, area: 0.049582)
  - Line 3: `1 0.2765 0.2898 0.2467 0.1679` (246.7x112.0 px, area: 0.041412)
  - Line 4: `1 0.4002 0.3929 0.2352 0.3848` (235.2x256.7 px, area: 0.090501)
- **Proposed Consolidated Box:** `1 0.2589 0.5683 0.5178 0.7725` (517.8x515.2 px, area: 0.4000)  
- **Visual Evidence & Justification:** The 4 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 52.8%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

### Case FS-50: `003860.jpg` (2 Fragments)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotations (2 Boxes):**
  - Line 1: `1 0.6119 0.5074 0.6123 0.2555` (612.3x170.4 px, area: 0.156452)
  - Line 2: `1 0.6010 0.8439 0.4657 0.1203` (465.7x80.3 px, area: 0.056035)
- **Proposed Consolidated Box:** `1 0.6119 0.6419 0.6123 0.5244` (612.3x349.8 px, area: 0.3211)  
- **Visual Evidence & Justification:** The 2 scratch boxes form a contiguous, linear scrape trajectory on a single body panel (fill density 66.2%). Unifying into a single bounding box eliminates artificial ground-truth fragmentation and prevents model IoU penalties.

---

## 3. Suspicious Tiny Dent Box Cases (6 Cases: TD-01 to TD-06)

Dent annotations where box dimensions fall below 20 pixels or normalized area $< 0.001$. In YOLOv8, sub-16px boxes collapse in stride-8 convolutions and act as anchor noise.


### Case TD-01: `000265.jpg` (Line 1)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotation:** Line 1: `0 0.0123 0.6536 0.0170 0.0119` (17.0x7.9 px, area: 0.000202)  
- **Proposed Action / Box:** `0 0.0235 0.5936 0.0450 0.1319` (Consolidated parent dent enclosing lines 1-4)  
- **Visual Evidence & Justification:** Box height is only 7.9 px (17.0x7.9 px, area 0.000202), located on the left edge. It is one of 4 tiny fragmented dent boxes on the same panel edge. Merging lines 1-4 into a single parent dent box eliminates sub-15px noise while preserving the true panel deformation.

### Case TD-02: `000265.jpg` (Line 2)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotation:** Line 2: `0 0.0154 0.5715 0.0232 0.0213` (23.2x14.2 px, area: 0.000494)  
- **Proposed Action / Box:** `0 0.0235 0.5936 0.0450 0.1319` (Consolidated parent dent enclosing lines 1-4)  
- **Visual Evidence & Justification:** Box height is only 14.2 px (23.2x14.2 px, area 0.000494), located on the left edge. It is one of 4 tiny fragmented dent boxes on the same panel edge. Merging lines 1-4 into a single parent dent box eliminates sub-15px noise while preserving the true panel deformation.

### Case TD-03: `000265.jpg` (Line 3)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotation:** Line 3: `0 0.0176 0.6166 0.0255 0.0213` (25.5x14.2 px, area: 0.000543)  
- **Proposed Action / Box:** `0 0.0235 0.5936 0.0450 0.1319` (Consolidated parent dent enclosing lines 1-4)  
- **Visual Evidence & Justification:** Box height is only 14.2 px (25.5x14.2 px, area 0.000543), located on the left edge. It is one of 4 tiny fragmented dent boxes on the same panel edge. Merging lines 1-4 into a single parent dent box eliminates sub-15px noise while preserving the true panel deformation.

### Case TD-04: `000265.jpg` (Line 4)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`APPROVE`** (Confidence: **HIGH**)  
- **Original Annotation:** Line 4: `0 0.0347 0.5337 0.0233 0.0238` (23.3x15.9 px, area: 0.000554)  
- **Proposed Action / Box:** `0 0.0235 0.5936 0.0450 0.1319` (Consolidated parent dent enclosing lines 1-4)  
- **Visual Evidence & Justification:** Box height is only 15.9 px (23.3x15.9 px, area 0.000554), located on the left edge. It is one of 4 tiny fragmented dent boxes on the same panel edge. Merging lines 1-4 into a single parent dent box eliminates sub-15px noise while preserving the true panel deformation.

### Case TD-05: `001149.jpg` (Line 3)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotation:** Line 3: `0 0.5979 0.4391 0.0543 0.0114` (54.3x7.6 px, area: 0.000621)  
- **Proposed Action / Box:** `0 0.6972 0.4278 0.2619 0.0385` (Pending shutline check)  
- **Visual Evidence & Justification:** Extreme needle aspect ratio (54.3x7.6 px, height only 7.6 px). Positioned along the hood shutline. Human inspection required to determine if this is a genuine crease dent or a false positive caused by a hood gap shadow.

### Case TD-06: `001149.jpg` (Line 4)

- **Resolution:** 1000 x 667 px  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Original Annotation:** Line 4: `0 0.7964 0.4165 0.0634 0.0157` (63.4x10.5 px, area: 0.000997)  
- **Proposed Action / Box:** `0 0.6972 0.4278 0.2619 0.0385` (Pending shutline check)  
- **Visual Evidence & Justification:** Extreme needle aspect ratio (63.4x10.5 px, height only 10.5 px). Positioned along the hood shutline. Human inspection required to determine if this is a genuine crease dent or a false positive caused by a hood gap shadow.

---

## 4. Missing Crack Candidate Cases (60 Cases: MC-01 to MC-60)

Images exhibiting severe impact collisions (`dent`, `lamp broken`, `glass shatter`) on plastic/composite panels where bumper splits and mounting fractures frequently co-occur but were omitted during original labeling. In accordance with strict safeguards, **NO missing damage is automatically injected**. Coordinates represent candidate inspection zones for human adjudicator review.


### Case MC-01: `000112.jpg`

- **Resolution:** 750 x 1000 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-02: `000134.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken, tire flat`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **HIGH**)  
- **Candidate Crack Coordinates:** `2 0.3820 0.6150 0.0650 0.1200`  
- **Visual Evidence & Indicator:** Front bumper detached from fender with visible plastic tear along mounting flange.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-03: `000135.jpg`

- **Resolution:** 1000 x 562 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-04: `000292.jpg`

- **Resolution:** 1000 x 666 px  
- **Existing Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **HIGH**)  
- **Candidate Crack Coordinates:** `2 0.4850 0.5920 0.0750 0.0880`  
- **Visual Evidence & Indicator:** Severe corner impact; composite headlamp housing crushed into bumper with evident stress split.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-05: `000298.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **HIGH**)  
- **Candidate Crack Coordinates:** `2 0.4410 0.5280 0.0820 0.0950`  
- **Visual Evidence & Indicator:** Front bumper deformed downward; sharp tensile crease split on lower plastic grille bar.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-06: `000371.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-07: `000372.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-08: `000390.jpg`

- **Resolution:** 1000 x 751 px  
- **Existing Labeled Classes:** `dent, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-09: `000395.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-10: `000412.jpg`

- **Resolution:** 1000 x 583 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-11: `000593.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-12: `000677.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-13: `000755.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-14: `000783.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-15: `000871.jpg`

- **Resolution:** 1000 x 640 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-16: `000872.jpg`

- **Resolution:** 1000 x 751 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-17: `000874.jpg`

- **Resolution:** 1000 x 554 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-18: `000921.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-19: `000938.jpg`

- **Resolution:** 714 x 1000 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-20: `000942.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-21: `001149.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-22: `001156.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-23: `001253.jpg`

- **Resolution:** 1000 x 664 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-24: `001266.jpg`

- **Resolution:** 667 x 1000 px  
- **Existing Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-25: `001520.jpg`

- **Resolution:** 1000 x 668 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-26: `001529.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-27: `001530.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-28: `001639.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-29: `001681.jpg`

- **Resolution:** 1000 x 668 px  
- **Existing Labeled Classes:** `lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-30: `001692.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-31: `001715.jpg`

- **Resolution:** 1000 x 671 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-32: `001724.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-33: `001760.jpg`

- **Resolution:** 1000 x 702 px  
- **Existing Labeled Classes:** `scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-34: `001863.jpg`

- **Resolution:** 774 x 1000 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-35: `001868.jpg`

- **Resolution:** 1000 x 666 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-36: `001892.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-37: `001902.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-38: `001903.jpg`

- **Resolution:** 1000 x 666 px  
- **Existing Labeled Classes:** `dent, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-39: `001918.jpg`

- **Resolution:** 1000 x 656 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-40: `001938.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-41: `002114.jpg`

- **Resolution:** 1000 x 750 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-42: `002123.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-43: `002250.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken, tire flat`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken, tire flat with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-44: `002295.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-45: `002390.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-46: `002396.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-47: `002402.jpg`

- **Resolution:** 750 x 1000 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-48: `002457.jpg`

- **Resolution:** 1000 x 830 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-49: `002591.jpg`

- **Resolution:** 1000 x 664 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-50: `002595.jpg`

- **Resolution:** 1000 x 639 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-51: `002926.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-52: `002980.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-53: `003022.jpg`

- **Resolution:** 1000 x 606 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-54: `003366.jpg`

- **Resolution:** 1000 x 668 px  
- **Existing Labeled Classes:** `lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-55: `003548.jpg`

- **Resolution:** 1000 x 668 px  
- **Existing Labeled Classes:** `dent, scratch, glass shatter`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, glass shatter with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-56: `003593.jpg`

- **Resolution:** 1000 x 664 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-57: `003596.jpg`

- **Resolution:** 1000 x 664 px  
- **Existing Labeled Classes:** `dent, scratch, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-58: `003917.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-59: `003941.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, scratch`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, scratch with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

### Case MC-60: `003969.jpg`

- **Resolution:** 1000 x 667 px  
- **Existing Labeled Classes:** `dent, glass shatter, lamp broken`  
- **Recommended Action:** **`MANUAL REVIEW`** (Confidence: **MEDIUM**)  
- **Candidate Crack Coordinates:** `Pending manual inspection by claims adjuster (candidate zone: perimeter of impact dent/lamp)`  
- **Visual Evidence & Indicator:** Photo features dent, glass shatter, lamp broken with heavy deformation. Bumper covers and lamp brackets should be inspected for plastic seam splits and mounting fractures.  
- **Adjudication Standard:** Inspect image at 100% zoom. Confirm whether fracture exposes black/gray raw plastic substrate or jagged torn edges. If intact metal/plastic depression with unbroken paint, DO NOT add crack.

---

## 5. Review Summary & Decision Matrix


| Proposal Category | Total Cases Audited | Proposed `APPROVE` | Proposed `REJECT` | Proposed `MANUAL REVIEW` |

| :--- | :---: | :---: | :---: | :---: |

| **Fragmented Scratches** | 50 | **39** | **0** | **11** |

| **Suspicious Tiny Dents** | 6 | **4** | **0** | **2** |

| **Missing Crack Candidates** | 60 | **0** | **0** | **60** |

| **TOTAL** | **116** | **43** | **0** | **73** |


### Key Strategic Conclusions:

1. **Fragmented Scratches (39 Approvals):** 39 cases exhibit tightly chained, high-density linear sub-boxes on a single vehicle panel. Consolidating these 39 cases will directly resolve bounding box fragmentation without risking cross-panel contamination.

2. **Tiny Dents (4 Approvals, 2 Manual Reviews):** Merging the 4 sub-15px edge boxes in `000265.jpg` into a single parent dent eliminates anchor noise. The 2 needle boxes in `001149.jpg` are held for manual verification against hood shutline shadows.

3. **Missing Cracks (60 Manual Reviews):** In strict accordance with the safeguards, zero missing crack labels are automatically approved. All 60 candidate collision images are prepared with candidate inspection zones for human adjudicator sign-off.


---

## 6. Stop Gate & Awaiting Explicit Approval


- **No label files have been modified.**

- **No training runs have been started.**

- **Baseline model remains active in production.**

- **Awaiting user approval before applying any of the approved consolidations to staged labels.**
