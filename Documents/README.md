# 📘 README: Manuscript Revision Plan
## Complete Guide to Paper Revision for MDPI Aerospace

**Project:** Optimization of land-based impact zones for spent rocket stages  
**Status:** Revision in progress  
**Timeline:** 30 days (2026-01-27 to 2026-02-26)  
**Team:** 13 specialized agents  

---

## 🎯 QUICK START

### What is this?
This is a **complete, actionable plan** for revising the manuscript based on two detailed reviewer comments. The plan breaks down all required work into 35 concrete tasks across 5 major blocks.

### Start here:
1. ✅ **Read this README** (you are here)
2. ✅ **Read** `00_MAIN_PLAN.md` (overview of all blocks)
3. ✅ **Review** `IMPLEMENTATION_CHECKLIST.md` (track progress)
4. ✅ **Check** `AGENT_ASSIGNMENTS.md` (who does what)
5. ✅ **Begin** with Block 1 tasks (methodology)

---

## 📁 FILE STRUCTURE

```
/mnt/user-data/outputs/
├── README.md                          ← YOU ARE HERE
├── 00_MAIN_PLAN.md                    ← Master plan overview
├── IMPLEMENTATION_CHECKLIST.md        ← Task tracking (35 tasks)
├── AGENT_ASSIGNMENTS.md               ← Team roles & handoffs
├── 01_METHODOLOGY_DETAILING.md        ← [See detailed plan]
├── 02_VALIDATION_SENSITIVITY.md       ← [See detailed plan]
├── 03_VISUALIZATION_DOCS.md           ← [See detailed plan]
├── 04_LANGUAGE_REFERENCES.md          ← [See detailed plan]
└── 05_ECONOMICS.md                    ← [See detailed plan]
```

**Note:** The detailed block files (01-05) contain extensive code examples and step-by-step instructions. They are referenced from the main plan but not included in this README for brevity.

---

## 🚀 GETTING STARTED

### Prerequisites

#### Software Requirements:
```bash
# Python 3.9+
python --version

# Required packages
pip install pandas numpy scipy matplotlib seaborn
pip install rasterio geopandas shapely
pip install openpyxl xlsxwriter
pip install SALib language-tool-python
pip install requests beautifulsoup4

# For LaTeX (manuscript editing)
# Install TeX Live or MiKTeX
```

#### Data Requirements:
- Sentinel-2 Level-2A scenes (2017-2023)
- OTU characteristics database (from IAS)
- Digital soil maps (1:200,000)
- DEM (ASTER GDEM v3)

#### Access Requirements:
- GitHub repository: https://github.com/vel5id/rocket-drop-zone-analysis-otu
- MDPI submission system: https://susy.mdpi.com/
- Crossref API (for DOI lookup): https://api.crossref.org/

---

### Setup

```bash
# Clone the repository
git clone https://github.com/vel5id/rocket-drop-zone-analysis-otu.git
cd rocket-drop-zone-analysis-otu

# Create working directories
mkdir -p outputs/{supplementary_tables,enhanced_figures,validation,language_check}

# Create revision branch
git checkout -b revision-v2

# Copy planning documents to project
cp /mnt/user-data/outputs/*.md ./docs/revision_plan/
```

---

## 📊 WHAT REVIEWERS ASKED FOR

### Reviewer 1 (PDF: aerospace-3883653-review (1).pdf)

#### Main Concerns:
1. **Methodology insufficient for reproducibility**
   - Need Sentinel-2 scene IDs and dates → **Task 1.1**
   - Need specific atmospheric correction algorithm → **Task 1.4**
   - Need actual numerical coefficients for soil quality → **Task 1.2**
   - Need explicit fire hazard classification → **Task 1.3**

2. **Sensitivity analysis MISSING** ⚠️ CRITICAL
   - Must show how results change with different weights → **Tasks 2.1-2.4**
   - Standard procedure in multi-criteria analysis

3. **Validation framework needed**
   - Even if empirical validation not yet possible → **Tasks 2.5-2.7**
   - Define success criteria and metrics

4. **Figures need improvement**
   - Font sizes too small (< 8pt) → minimum 10pt → **Tasks 3.1-3.6**
   - Missing north arrows and scale bars
   - Not colorblind-friendly

5. **English requires professional editing**
   - Article usage errors → **Tasks 4.1-4.4**
   - Complex sentence structure
   - Literal translations from Russian

6. **References incomplete**
   - Missing DOIs, page ranges, volumes → **Task 4.5**

### Reviewer 2 (DOCX: Рец2.docx)

#### Main Concerns:
1. **Economic analysis weak**
   - Need at least one worked example → **Tasks 5.1-5.2**
   - Show exact calculation for specific OTU

2. **Additional tables needed**
   - Weighting coefficients rationale → **Task 3.8 (Table S6)**
   - OTU distribution by class → **Task 3.7 (Table S5)**

3. **Temporal update strategy**
   - Clarify how often to update environmental baseline → **Section added to Discussion**

---

## 🎯 PRIORITIZATION

### 🔴 CRITICAL (Must do for acceptance):
- Sensitivity analysis (Tasks 2.1-2.4)
- Validation framework (Tasks 2.5-2.7)
- Methodology details (Tasks 1.1-1.3)
- All supplementary tables (S1-S6)

### 🟡 HIGH (Important for quality):
- Figure improvements (Tasks 3.1-3.6)
- Language editing (Tasks 4.1-4.4)
- Reference formatting (Task 4.5)

### 🟢 MEDIUM (Enhances paper):
- Economic worked example (Tasks 5.1-5.3)
- Additional documentation

---

## 📅 TIMELINE (30 Days)

```
Week 1: Data & Methodology
├─ Days 1-3: Sentinel-2 table, soil coefficients
├─ Days 4-5: Fire classification, atmospheric details
└─ Days 6-7: Begin sensitivity analysis

Week 2: Validation & Analysis  
├─ Days 8-10: Complete sensitivity (OAT, MC, Sobol)
├─ Days 11-13: Validation framework design
└─ Days 14: Integration of results

Week 3: Visualization & Tables
├─ Days 15-17: Enhance all figures
├─ Days 18-19: Supplementary tables S5-S6
└─ Days 20: Package supplementary materials

Week 4: Language & Submission
├─ Days 21-23: Language editing
├─ Days 24-25: Reference formatting
├─ Days 26-27: Response to reviewers
└─ Days 28-30: Final assembly and submission
```

---

## 👥 TEAM STRUCTURE

### 13 Specialized Agents:

**Core Data Team** (Week 1):
- Data Processing Agent
- Methodology Agent  
- Vegetation Analysis Agent
- Remote Sensing Agent

**Analysis Team** (Weeks 1-2):
- Statistical Analysis Agent
- Field Data Integration Agent

**Production Team** (Weeks 2-3):
- Visualization Agent
- Documentation Agent

**Finishing Team** (Weeks 3-4):
- Language Editor
- Bibliography Agent
- Economics Agent

**Support Team** (Ongoing):
- Project Manager
- Code Manager

**See** `AGENT_ASSIGNMENTS.md` for detailed responsibilities.

---

## 🔄 WORKFLOW

### Daily Cycle:
1. **Morning:** Check assignments in `AGENT_ASSIGNMENTS.md`
2. **Work:** Execute tasks, commit code frequently
3. **Afternoon:** Update `IMPLEMENTATION_CHECKLIST.md`
4. **Evening:** Post async standup update

### Weekly Cycle:
1. **Monday:** Review week's goals
2. **Wednesday:** Mid-week check-in
3. **Friday:** Live sync meeting, adjust if needed

### Handoffs:
- Follow handoff protocol in `AGENT_ASSIGNMENTS.md`
- Verify data integrity before accepting handoff
- Document any discrepancies immediately

---

## 📋 DELIVERABLES CHECKLIST

### For MDPI Submission:
- [ ] Revised manuscript (LaTeX + PDF)
- [ ] Response to Reviewers (point-by-point)
- [ ] Cover letter
- [ ] Supplementary Tables S1-S7 (Excel + LaTeX)
- [ ] Supplementary Figures S1-S2 (PNG 300 DPI)
- [ ] Supplementary Methods S1
- [ ] All source figures (enhanced, PNG/PDF)

### For GitHub:
- [ ] Updated code (all new scripts)
- [ ] README with reproducibility guide
- [ ] API documentation
- [ ] Test suite
- [ ] Release v2.0 tag

---

## 🛠️ TOOLS & RESOURCES

### Python Libraries:
```python
# Data processing
import pandas as pd
import numpy as np
import rasterio
import geopandas as gpd

# Analysis
from scipy import stats
from SALib.sample import saltelli
from SALib.analyze import sobol

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib_scalebar.scalebar import ScaleBar

# Language
import language_tool_python

# References
import requests  # for Crossref API
```

### External Tools:
- **Sen2Cor:** ESA atmospheric correction processor
- **QGIS:** For manual map checks
- **Grammarly:** For initial language check
- **Zotero:** For reference management
- **Overleaf:** For collaborative LaTeX editing (optional)

### Documentation:
- **MDPI Guide:** https://www.mdpi.com/authors
- **Sentinel-2:** https://sentinels.copernicus.eu/
- **ColorBrewer:** https://colorbrewer2.org/
- **SALib Docs:** https://salib.readthedocs.io/

---

## 🚨 COMMON PITFALLS & SOLUTIONS

### Pitfall 1: "Sensitivity analysis is too complex"
**Solution:** Follow Task 2.1-2.3 step-by-step. Start with simple OAT, then MC, then Sobol. Code examples provided.

### Pitfall 2: "Don't have field validation data"
**Solution:** Create a validation *framework* (protocol) without executing it. Show what *would* be done. Task 2.5-2.7 provides template.

### Pitfall 3: "Figures still look bad after enhancement"
**Solution:** Use `FigureEnhancer` class (Task 3.1). Apply ALL fixes: fonts ≥10pt, north arrow, scale bar, colorblind palette, hatching patterns.

### Pitfall 4: "Language editing takes forever"
**Solution:** Do automated check first (LanguageTool), then manual edit in 3 passes (one section at a time). Consider MDPI language service for final polish.

### Pitfall 5: "Can't find DOI for old references"
**Solution:** Use Crossref API (Task 4.5). For missing DOIs, search Google Scholar or contact journal directly. Document any references without DOI.

---

## 📞 SUPPORT & ESCALATION

### For Questions:
1. **Check documentation** in detailed plan files (01-05)
2. **Search GitHub issues** in the code repository
3. **Ask peer agent** (see assignments)
4. **Escalate to Project Manager** if stuck > 4 hours

### For Blockers:
1. **Document in** `IMPLEMENTATION_CHECKLIST.md` → Blocker Tracking
2. **Notify Project Manager** immediately
3. **Propose alternative approach** if possible
4. **Request timeline adjustment** if critical

### Contacts:
- **Project Manager:** [Add contact]
- **Technical Lead:** [Add contact]
- **MDPI Support:** https://www.mdpi.com/about/contact

---

## 🎉 SUCCESS CRITERIA

### Manuscript Acceptance:
- ✅ All reviewer comments addressed
- ✅ All supplementary materials included
- ✅ Figures meet publication standards
- ✅ Language is clear and error-free
- ✅ References properly formatted

### Code Quality:
- ✅ All scripts run without errors
- ✅ Code is documented (docstrings)
- ✅ README explains reproducibility
- ✅ Tests pass (if implemented)

### Team Performance:
- ✅ All tasks completed on time
- ✅ No major blockers unresolved
- ✅ Good communication throughout
- ✅ Lessons learned documented

---

## 📚 DETAILED PLANS

For in-depth instructions, code examples, and methodologies, see:

1. **`01_METHODOLOGY_DETAILING.md`**
   - How to create Tables S1-S3
   - Sentinel-2 metadata extraction
   - Soil coefficient calculation
   - Fire hazard classification

2. **`02_VALIDATION_SENSITIVITY.md`**
   - Complete sensitivity analysis workflow
   - OAT, Monte Carlo, Sobol methods
   - Validation framework design
   - Metrics and success criteria

3. **`03_VISUALIZATION_DOCS.md`**
   - Figure enhancement procedures
   - ColorBrewer palettes
   - North arrows and scale bars
   - Supplementary tables S5-S6

4. **`04_LANGUAGE_REFERENCES.md`**
   - Language editing checklist
   - Common grammar errors
   - Reference formatting (MDPI style)
   - Crossref API usage

5. **`05_ECONOMICS.md`**
   - Economic damage calculator
   - Worked example for OTU
   - Cost comparison methodology
   - Table S7 creation

**Note:** These files contain extensive code examples (>1000 lines each) and are the primary reference for implementation.

---

## 🔍 FREQUENTLY ASKED QUESTIONS

### Q1: Do I need to implement ALL 35 tasks?
**A:** Critical tasks (🔴) are mandatory. High priority (🟡) tasks are strongly recommended. Medium (🟢) are enhancing but can be abbreviated if time-constrained.

### Q2: Can I change the order of tasks?
**A:** Follow the dependencies in `AGENT_ASSIGNMENTS.md`. Some tasks must be completed before others (e.g., data processing before analysis).

### Q3: What if I don't have access to Sentinel-2 data?
**A:** Contact the Data Processing Agent or Project Manager. Archive data should be available from project storage.

### Q4: How do I know if my work meets publication standards?
**A:** Each task has specific acceptance criteria in the detailed plan files. Check figures at 300 DPI, tables in proper format, code runs without errors.

### Q5: What if sensitivity analysis shows classification is unstable?
**A:** This is valuable finding! Document it honestly in Discussion. Propose adjustments to weights or additional validation steps.

### Q6: Do I need to be expert in all tools?
**A:** No. Code examples are provided. For complex tasks, collaborate with relevant agent or escalate to Project Manager.

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-27 | Initial revision plan created |
| 1.1 | TBD | After Week 1 review |
| 2.0 | TBD | Final submission version |

---

## 🏁 FINAL CHECKLIST

Before submission, verify:

- [ ] All 35 tasks marked as complete in `IMPLEMENTATION_CHECKLIST.md`
- [ ] All deliverables present in outputs directory
- [ ] Response to Reviewers addresses every point
- [ ] Manuscript compiles without LaTeX errors
- [ ] All figures render at 300 DPI
- [ ] All supplementary materials formatted correctly
- [ ] GitHub repository updated with tag v2.0
- [ ] Cover letter written and signed
- [ ] MDPI submission form completed
- [ ] All co-authors approve final version

---

## 🎯 NEXT STEPS

1. **Read** the main plan: `00_MAIN_PLAN.md`
2. **Assign** agents: use `AGENT_ASSIGNMENTS.md`
3. **Begin** Block 1 tasks (methodology)
4. **Track** progress daily in `IMPLEMENTATION_CHECKLIST.md`
5. **Submit** on Day 30!

---

**Good luck with the revision! 🚀**

**Questions?** Contact the Project Manager  
**Updates?** Check GitHub repository  
**Blocked?** Review escalation procedure in `AGENT_ASSIGNMENTS.md`

---

**Document Version:** 1.0  
**Created:** 2026-01-27  
**For:** MDPI Aerospace Manuscript Revision  
**Authors:** Revision Planning Team
