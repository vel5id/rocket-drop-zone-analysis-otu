# 👥 AGENT ASSIGNMENTS
## Task Distribution for Manuscript Revision

**Project:** Rocket Drop Zone Optimization Paper Revision  
**Target:** MDPI Aerospace  
**Timeline:** 30 days  

---

## 🎯 AGENT ROLES & RESPONSIBILITIES

### 1. 🔬 Data Processing Agent
**Primary Skills:** Remote sensing, geospatial data processing, Sentinel-2 analysis  
**Tools:** Python, rasterio, GDAL, pandas  
**Output Formats:** GeoTIFF, CSV, Excel  

**Assigned Tasks:**
- ✅ **Task 1.1:** Sentinel-2 Scene Metadata Table (Days 1-3)
  - Extract scene IDs, dates, cloud cover from archive
  - Create Table S1 (Excel + CSV)
  - Update Materials & Methods section
  
**Deliverables:**
- `/outputs/supplementary_tables/Table_S1_Sentinel2_Scenes.xlsx`
- `/outputs/supplementary_tables/Table_S1_Sentinel2_Scenes.csv`
- Updated text for manuscript section 3.1

**Dependencies:** Access to Sentinel-2 data archive

---

### 2. 📐 Methodology Agent
**Primary Skills:** Soil science, GIS analysis, classification methods  
**Tools:** Python, GeoPandas, soil databases  
**Output Formats:** Excel, LaTeX tables  

**Assigned Tasks:**
- ✅ **Task 1.2:** Soil Coefficients Tables (Days 2-5)
  - Create Tables S2 (QBi coefficients) and S3 (QSi coefficients)
  - Implement `SoilQualityCalculator` class
  - Implement `SoilStrengthCalculator` class
  - Add worked examples

**Deliverables:**
- `/outputs/supplementary_tables/Table_S2_Soil_Quality_Coefficients.xlsx`
- `/outputs/supplementary_tables/Table_S3_Protodyakonov_Strength.xlsx`
- `/src/analysis/soil_coefficients.py` (updated)
- Updated manuscript section 3.2

**Dependencies:** Access to national soil databases, bonitet methodology docs

---

### 3. 🌿 Vegetation Analysis Agent
**Primary Skills:** Ecology, NDVI analysis, fire hazard assessment  
**Tools:** Python, scikit-learn, matplotlib  
**Output Formats:** Excel, PNG maps  

**Assigned Tasks:**
- ✅ **Task 1.3:** Fire Hazard Classification (Days 3-5)
  - Create plant community classification table
  - Define NDVI ranges and flammability weights
  - Implement `FireHazardClassifier` class
  - Generate fire hazard maps

**Deliverables:**
- Fire hazard classification table (LaTeX + Excel)
- `/src/analysis/fire_hazard_assessment.py` (new)
- Fire hazard maps for manuscript
- Updated manuscript section 3.2

**Dependencies:** NDVI raster data, plant community inventories

---

### 4. 🛰️ Remote Sensing Agent
**Primary Skills:** Atmospheric correction, spectral analysis  
**Tools:** Sen2Cor, Python, ESA SNAP  
**Output Formats:** Documentation, processed imagery  

**Assigned Tasks:**
- ✅ **Task 1.4:** Atmospheric Correction Details (Days 1-2)
  - Document Sen2Cor v2.9 processing parameters
  - Update methodology description
  - Add references

**Deliverables:**
- Updated manuscript section 3.1
- Processing parameter documentation

**Dependencies:** None (documentation task)

---

### 5. 📊 Statistical Analysis Agent
**Primary Skills:** Sensitivity analysis, Monte Carlo, Sobol methods  
**Tools:** Python, SALib, scipy, numpy  
**Output Formats:** Excel, PNG plots, LaTeX  

**Assigned Tasks:**
- ✅ **Task 2.1:** OAT Sensitivity Analysis (Days 5-8)
- ✅ **Task 2.2:** Monte Carlo Sensitivity (Days 6-9)
- ✅ **Task 2.3:** Sobol Indices Calculation (Days 7-10)
- ✅ **Task 2.4:** Sensitivity Results Integration (Days 8-11)
- ✅ **Task 2.8:** Uncertainty Analysis (Days 12-14)

**Deliverables:**
- `/src/validation/sensitivity_analysis.py` (new)
- Supplementary Figure S1 (sensitivity plots)
- Supplementary Table S4 (sensitivity results)
- New manuscript section "Sensitivity Analysis"
- Updated Discussion section

**Dependencies:** Finalized OTU dataset with all indices

---

### 6. ✅ Field Data Integration Agent
**Primary Skills:** Validation design, field methodology, statistics  
**Tools:** Python, pandas, scikit-learn  
**Output Formats:** PDF reports, Excel, LaTeX  

**Assigned Tasks:**
- ✅ **Task 2.5:** Validation Framework Design (Days 9-12)
- ✅ **Task 2.6:** Validation Framework Implementation (Days 10-13)
- ✅ **Task 2.7:** Validation Section Writing (Days 12-14)

**Deliverables:**
- `/src/validation/validation_framework.py` (new)
- Validation protocol document (PDF)
- Supplementary Figure S2 (validation workflow)
- New manuscript section "Validation Framework"

**Dependencies:** Statistical Analysis Agent (for metrics)

---

### 7. 🎨 Visualization Agent
**Primary Skills:** Scientific figure design, cartography, ColorBrewer  
**Tools:** Python, matplotlib, CartoPy, Adobe Illustrator  
**Output Formats:** PNG (300 DPI), PDF  

**Assigned Tasks:**
- ✅ **Task 3.1:** Figure Quality Standards Setup (Days 12-15)
- ✅ **Task 3.2:** Map Enhancement Core Functions (Days 13-16)
- ✅ **Task 3.3:** Enhance Figures Group 1 (Days 14-17)
- ✅ **Task 3.4:** Enhance Figures Group 2 (Days 15-18)
- ✅ **Task 3.5:** Simplify Flowcharts (Days 16-18)
- ✅ **Task 3.6:** Final Map Figure 18 (Days 17-19)

**Deliverables:**
- `/src/visualization/figure_enhancement.py` (new)
- 18 enhanced figures (all Figures 1-18, PNG 300 DPI)
- Simplified IAS architecture diagrams
- All figures in `/outputs/enhanced_figures/`

**Dependencies:** All data processing completed

---

### 8. 📝 Documentation Agent
**Primary Skills:** Technical writing, LaTeX, Excel  
**Tools:** Python, pandas, openpyxl, LaTeX  
**Output Formats:** Excel, LaTeX, TXT  

**Assigned Tasks:**
- ✅ **Task 3.7:** Supplementary Table S5 (Days 14-17)
- ✅ **Task 3.8:** Supplementary Table S6 (Days 14-17)
- ✅ **Task 3.9:** Supplementary Materials Package (Days 18-20)

**Deliverables:**
- Table S5: OTU Distribution (Excel + LaTeX)
- Table S6: Weighting Rationale (Excel + LaTeX)
- README_Supplementary_Materials.txt
- Complete supplementary materials ZIP

**Dependencies:** All other agents' tables completed

---

### 9. ✍️ Language Editor
**Primary Skills:** Scientific English, grammar, style editing  
**Tools:** LanguageTool, Grammarly, Microsoft Word  
**Output Formats:** LaTeX (edited), DOCX (tracked changes)  

**Assigned Tasks:**
- ✅ **Task 4.1:** Automated Language Check (Days 17-21)
- ✅ **Task 4.2:** Manual Editing Part 1 (Days 18-22)
- ✅ **Task 4.3:** Manual Editing Part 2 (Days 19-23)
- ✅ **Task 4.4:** Manual Editing Part 3 (Days 20-24)

**Deliverables:**
- Language check report (Excel)
- Fully edited manuscript (LaTeX)
- Change log (what was corrected)

**Dependencies:** All content finalized before editing

**Note:** Consider professional MDPI language service for final polish (Task 4.5)

---

### 10. 📚 Bibliography Agent
**Primary Skills:** Reference management, API usage, formatting  
**Tools:** Python, Crossref API, Zotero  
**Output Formats:** BibTeX, formatted text  

**Assigned Tasks:**
- ✅ **Task 4.5:** Bibliography Formatting (Days 18-22)
  - Extract DOIs via Crossref API
  - Add missing metadata
  - Format per MDPI Aerospace standards

**Deliverables:**
- `/outputs/formatted_references.bib`
- Formatted reference list for manuscript
- Missing DOI report

**Dependencies:** None (can start anytime)

---

### 11. 💰 Economics Agent
**Primary Skills:** Environmental economics, cost-benefit analysis  
**Tools:** Python, pandas, Excel  
**Output Formats:** Excel, LaTeX, PDF  

**Assigned Tasks:**
- ✅ **Task 5.1:** Economic Calculator Implementation (Days 16-20)
- ✅ **Task 5.2:** Worked Example for OTU (Days 17-21)
- ✅ **Task 5.3:** Comparative Cost Analysis (Days 18-22)
- ✅ **Task 5.4:** Supplementary Table S7 (Days 19-22)
- ✅ **Task 5.5:** Economics Section Update (Days 20-23)

**Deliverables:**
- `/src/analysis/economic_calculator.py` (new)
- Worked example in manuscript text
- Table S7: Cost Breakdown (Excel + LaTeX)
- Updated Economics subsection

**Dependencies:** Soil and vegetation parameters finalized

---

### 12. 👔 Project Manager
**Primary Skills:** Coordination, documentation, submission  
**Tools:** Git, Markdown, MDPI submission system  
**Output Formats:** PDF, DOCX, ZIP  

**Assigned Tasks:**
- ✅ **Task FD.1:** Response to Reviewers (Days 22-27)
- ✅ **Task FD.2:** Cover Letter (Days 22-27)
- ✅ **Task FD.3:** Final Manuscript Assembly (Days 25-28)
- ✅ **Task FD.5:** Submission to MDPI (Days 28-29)
- ⚫ Coordination of all agents (Days 1-30)
- ⚫ Daily progress tracking (Days 1-30)
- ⚫ Blocker resolution (as needed)

**Deliverables:**
- Response to Reviewers document (PDF)
- Cover letter (PDF)
- Final assembled manuscript (LaTeX + PDF)
- Submission package (ZIP)
- MDPI submission confirmation

**Dependencies:** All other agents' work completed

---

### 13. 💻 Code Manager
**Primary Skills:** Software engineering, Git, documentation  
**Tools:** Git, Python, Sphinx  
**Output Formats:** Python code, Markdown, HTML docs  

**Assigned Tasks:**
- ✅ **Task FD.4:** GitHub Repository Update (Days 20-28)
  - Commit all new scripts
  - Update README
  - Create API documentation
  - Release v2.0

**Deliverables:**
- Updated GitHub repository
- API documentation (HTML)
- README with reproducibility guide
- Tagged release v2.0

**Dependencies:** All code from other agents completed

---

## 📅 GANTT CHART (Simplified)

```
Agent                  | Week 1  | Week 2  | Week 3  | Week 4  |
-----------------------|---------|---------|---------|---------|
Data Processing        | ████    |         |         |         |
Methodology            | ████    |         |         |         |
Vegetation Analysis    | ████    |         |         |         |
Remote Sensing         | ██      |         |         |         |
Statistical Analysis   |  ████   | ████    |         |         |
Field Data Integration |         | ████    | ██      |         |
Visualization          |         | ████    | ████    |         |
Documentation          |         |  ███    | ████    |         |
Language Editor        |         |         | ████    | ███     |
Bibliography           |         |  ████   |         |         |
Economics              |         |  ████   | ███     |         |
Project Manager        | ░░░░░░░░░░░░░░░░░░░░░░░░░░░░| ████    |
Code Manager           |         |         | ████    | ████    |
```

Legend:
- `█` Active work
- `░` Background coordination

---

## 🔄 HANDOFF PROTOCOL

### Data Processing → Methodology
**Handoff:** Day 3  
**Items:** Processed Sentinel-2 scenes, NDVI rasters  
**Format:** GeoTIFF + metadata CSV  
**Verification:** Methodology Agent confirms data integrity

### Methodology → Statistical Analysis
**Handoff:** Day 5  
**Items:** Complete OTU characteristics database  
**Format:** CSV with columns (OTU_ID, QVi, QSi, QBi, Qrelief, stability_class)  
**Verification:** Statistical Agent runs basic stats check

### Statistical Analysis → Documentation
**Handoff:** Day 11  
**Items:** Sensitivity analysis results  
**Format:** Excel tables + PNG plots  
**Verification:** Documentation Agent checks table formatting

### All Data Agents → Visualization
**Handoff:** Days 12-15  
**Items:** All raster datasets  
**Format:** GeoTIFF (UTM Zone 43N)  
**Verification:** Visualization Agent tests import

### All Content → Language Editor
**Handoff:** Day 21  
**Items:** Complete manuscript (unedited version)  
**Format:** LaTeX + PDF  
**Verification:** Language Editor confirms receipt

### All Agents → Project Manager
**Handoff:** Day 27  
**Items:** All final deliverables  
**Format:** As specified per task  
**Verification:** Project Manager creates checklist

---

## 💬 COMMUNICATION PROTOCOL

### Daily Standups (Async)
**Time:** 09:00 UTC (posted by 10:00 UTC)  
**Format:** Update in shared document  
**Template:**
```
Agent: [Name]
Date: [YYYY-MM-DD]
Yesterday: [Tasks completed]
Today: [Tasks planned]
Blockers: [Any issues]
ETA on deliverables: [On track / Delayed by X days]
```

### Weekly Sync (Live Meeting)
**Time:** Fridays 14:00 UTC  
**Duration:** 30 minutes  
**Agenda:**
1. Progress review (5 min)
2. Blocker discussion (10 min)
3. Next week planning (10 min)
4. Q&A (5 min)

### Emergency Contact
**For critical blockers only:**
- Project Manager: [contact info]
- Slack channel: #paper-revision-urgent

---

## 🚨 ESCALATION PROCEDURE

### Level 1: Agent self-resolution
- Agent attempts to resolve blocker (max 2 hours)

### Level 2: Peer consultation
- Ask relevant peer agent for help
- Document in shared log

### Level 3: Project Manager intervention
- If blocker persists > 4 hours
- PM assigns resources or adjusts timeline

### Level 4: External help
- If technical expertise needed (e.g., MDPI support)
- PM coordinates external contact

---

## 📊 PROGRESS REPORTING

### Metrics to Track:
1. **Tasks completed** vs. planned (daily)
2. **Deliverables submitted** vs. expected (daily)
3. **Code quality** (test coverage, linting) (weekly)
4. **Documentation completeness** (% of required docs done) (weekly)

### Reports:
- **Daily:** Brief status update (async)
- **Weekly:** Full progress report (live meeting)
- **Final:** Comprehensive completion report (Day 30)

---

## 🎯 SUCCESS CRITERIA

### For Each Agent:
- ✅ All assigned tasks completed on time
- ✅ All deliverables meet quality standards
- ✅ Code passes tests and review
- ✅ Documentation is complete

### For Project:
- ✅ Manuscript accepted for publication
- ✅ All reviewer comments addressed
- ✅ Code repository updated and tested
- ✅ Team satisfied with process

---

## 🏆 AGENT PRIORITIES

### Critical Path Agents (Must Complete First):
1. Data Processing Agent
2. Methodology Agent
3. Statistical Analysis Agent

### Parallel Track Agents (Can Work Simultaneously):
4. Vegetation Analysis Agent
5. Remote Sensing Agent
6. Field Data Integration Agent

### Dependent Agents (Wait for Others):
7. Visualization Agent (waits for data)
8. Documentation Agent (waits for content)
9. Language Editor (waits for finalized content)

### Support Agents (Ongoing):
10. Bibliography Agent (can start anytime)
11. Economics Agent (moderate dependency)
12. Project Manager (coordinates all)
13. Code Manager (integrates all code)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-27  
**Next Review:** 2026-02-03 (Day 7)
