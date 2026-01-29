# MDPI Language Service Guide
## Professional Editing Service for Rocket Drop Zone Analysis Manuscript

**Task 4.5 Reference:** IMPLEMENTATION_ROADMAP.md lines 605-616  
**Created:** 2026-01-28  
**Version:** 1.0

---

## 📋 Overview

This guide provides instructions for using the MDPI Language Editing Service for the "Rocket Drop Zone Analysis - OTU Pipeline" manuscript. The service ensures the manuscript meets MDPI's high standards for academic English, clarity, and style.

### Key Features:
- **Automated preparation** of manuscript files for submission
- **Submission package creation** with all required components
- **Status tracking** throughout the editing process
- **Feedback processing** and analysis tools
- **Change integration** workflow for editor's suggestions
- **Version control** to track all modifications

---

## 🚀 Quick Start

### 1. Prepare Your Manuscript
```bash
# Activate virtual environment
venv_311\Scripts\activate

# Run preparation script
python scripts/professional_editing_service.py --prepare --files outputs/manuscript_sections/*.md
```

### 2. Create Submission Package
```bash
# Create ZIP package for MDPI
python scripts/professional_editing_service.py --create-package --files outputs/manuscript_sections/*.md
```

### 3. Submit to MDPI
1. Go to [MDPI Language Editing Service](https://www.mdpi.com/authors/english)
2. Upload the generated `Submission_Package.zip`
3. Select "Aerospace" as target journal
4. Provide manuscript details and submit

---

## 📁 File Requirements

### Mandatory Files:
| File Type | Description | Format |
|-----------|-------------|--------|
| Main Manuscript | Complete manuscript text | `.docx`, `.tex`, or `.md` |
| Figures | All figures referenced | `.png`, `.jpg`, `.svg` (300 DPI) |
| Tables | Supplementary tables | `.xlsx`, `.csv` |
| Bibliography | Reference list | `.bib`, `.txt` (MDPI format) |

### Recommended Structure:
```
Submission_Package/
├── manuscript/
│   ├── main_manuscript.docx
│   ├── abstract.md
│   ├── introduction.md
│   └── methods_results_discussion.md
├── figures/
│   ├── Figure_1.png
│   ├── Figure_2.png
│   └── ...
├── tables/
│   ├── Table_1.xlsx
│   └── ...
└── metadata.json
```

---

## 🔧 Using the Professional Editing Service Script

### Class: `ProfessionalEditingService`
The main class providing all editing service functionality.

#### Initialization:
```python
from scripts.professional_editing_service import ProfessionalEditingService

service = ProfessionalEditingService(project_root=".")
```

#### Key Methods:

##### 1. `prepare_for_mdpi_service()`
Prepares files for MDPI submission with validation checks.

```python
result = service.prepare_for_mdpi_service([
    "outputs/manuscript_sections/abstract.md",
    "outputs/manuscript_sections/introduction.md",
    "outputs/manuscript_sections/methods.md"
])
```

**Output:** `preparation_report.json` with validation results.

##### 2. `create_submission_package()`
Creates a ZIP package ready for MDPI submission.

```python
package_path = service.create_submission_package(
    files_to_include=manuscript_files,
    package_name="Rocket_Drop_Zone_Submission"
)
```

**Output:** `Submission_Package.zip` with README and metadata.

##### 3. `track_submission_status()`
Tracks the status of your MDPI submission.

```python
status = service.track_submission_status(submission_id="SUB001_20260128")
```

**Output:** JSON status report with estimated completion time.

##### 4. `process_editor_feedback()`
Processes feedback received from MDPI editor.

```python
analysis = service.process_editor_feedback(
    feedback_file="Editor_Feedback_Report.xlsx",
    submission_id="SUB001_20260128"
)
```

**Output:** `processed_feedback.json` and `Editor_Feedback_Report.xlsx`

##### 5. `integrate_editor_changes()`
Integrates editor's changes into your manuscript.

```python
result = service.integrate_editor_changes(
    original_files=["manuscript_v1.docx"],
    edited_files=["manuscript_edited.docx"],
    feedback_analysis=analysis
)
```

**Output:** `integration_report.json` with change summary.

##### 6. `create_change_summary()`
Creates a summary of changes between versions.

```python
summary = service.create_change_summary(changes_list)
```

---

## 📊 Version Tracking System

### Class: `VersionTracker`
Tracks all versions of manuscript files with hash-based comparison.

#### Creating Snapshots:
```python
version_id = service.version_tracker.create_snapshot(
    files=manuscript_files,
    description="Pre-MDPI submission version",
    metadata={"author": "Research Team", "status": "ready"}
)
```

#### Comparing Versions:
```python
comparison = service.version_tracker.compare_versions(
    version_id1="v001_20260128_120000",
    version_id2="v002_20260130_150000"
)
```

#### Version Directory Structure:
```
outputs/professional_editing/versions/
├── v001_20260128_120000/
│   ├── abstract.md
│   ├── introduction.md
│   └── metadata.json
├── v002_20260130_150000/
│   └── ...
└── version_history.json
```

---

## 📨 Submission Tracking

### Class: `SubmissionTracker`
Manages submissions to editing services with status history.

#### Recording a Submission:
```python
submission_id = service.submission_tracker.record_submission(
    package_path="outputs/professional_editing/Submission_Package.zip",
    files_included=manuscript_files,
    service="MDPI"
)
```

#### Status Updates:
- `submitted` → `under_review` → `being_edited` → `editing_complete` → `ready_for_download` → `completed`

#### Viewing Submission History:
```python
# Get latest submission
latest = service.submission_tracker.get_latest_status()

# Get specific submission
submission = service.submission_tracker.get_submission_status("SUB001_20260128")
```

---

## 🎯 Integration with Previous Tasks

### Task 4.1: Automated Language Check
The professional editing service builds upon the language check results:

```python
# Load language check results
language_errors = pd.read_excel("outputs/language_check/Grammar_Errors_Report.xlsx")

# Include in submission metadata
metadata = {
    "language_check_completed": True,
    "error_count": len(language_errors),
    "major_issues_resolved": True
}
```

### Tasks 4.2-4.3: Manual Language Editing
Ensure manual edits are incorporated before professional editing:

1. Run manual editing scripts
2. Verify all changes are saved
3. Create version snapshot
4. Proceed with MDPI submission

### Task 4.4: Bibliography Formatting
MDPI requires specific bibliography formatting:

```python
# Verify bibliography is MDPI-compliant
bibliography_check = service._check_mdpi_requirements([
    "outputs/bibliography/formatted_references.bib"
])
```

---

## 📈 Expected Timeline

| Day | Activity | Duration | Status |
|-----|----------|----------|--------|
| Day 1 | Prepare and submit | 1 day | ✅ |
| Day 2-4 | MDPI editing process | 2-3 days | ⏳ |
| Day 5 | Receive feedback | 1 day | ⏳ |
| Day 6-7 | Integrate changes | 2 days | ⏳ |
| Day 8 | Final verification | 1 day | ⏳ |

**Total Estimated Time:** 7-8 days

---

## ✅ Quality Checklist

### Before Submission:
- [ ] All figures are 300 DPI minimum
- [ ] Tables are in Excel format with clear headers
- [ ] Bibliography follows MDPI Aerospace style
- [ ] Abstract is 200-250 words
- [ ] Keywords (5-10) are provided
- [ ] All acronyms are defined at first use
- [ ] Word count is within journal limits
- [ ] Language check (Task 4.1) completed
- [ ] Manual edits (Tasks 4.2-4.3) incorporated
- [ ] Bibliography formatting (Task 4.4) verified

### After Receiving Feedback:
- [ ] Review all editor comments
- [ ] Prioritize changes by importance
- [ ] Integrate technical corrections
- [ ] Verify terminology consistency
- [ ] Check reference formatting
- [ ] Create change summary report
- [ ] Update version history

---

## 🛠️ Troubleshooting

### Common Issues:

#### 1. File Format Issues
**Problem:** MDPI rejects file format  
**Solution:** Convert to `.docx` using:
```bash
pandoc manuscript.md -o manuscript.docx --reference-doc=template.docx
```

#### 2. Large File Size
**Problem:** Submission package too large  
**Solution:** Compress images:
```python
from PIL import Image
img = Image.open("figure.png")
img.save("figure_compressed.png", optimize=True, quality=85)
```

#### 3. Missing Metadata
**Problem:** Submission lacks required information  
**Solution:** Ensure `metadata.json` includes:
```json
{
  "title": "Rocket Drop Zone Analysis Using OTU Methodology",
  "authors": ["Author1", "Author2"],
  "corresponding_author": "author@email.com",
  "target_journal": "Aerospace",
  "word_count": 8500,
  "figure_count": 18,
  "table_count": 7
}
```

#### 4. Status Not Updating
**Problem:** MDPI status not reflected in tracker  
**Solution:** Manual update:
```python
service.submission_tracker.update_submission_status(
    submission_id="SUB001_20260128",
    status="being_edited",
    notes="Confirmed via MDPI portal"
)
```

---

## 📋 Output Files Generated

The professional editing service creates the following output structure:

```
outputs/professional_editing/
├── preparation_report.json          # Initial preparation results
├── Submission_Package.zip           # Package for MDPI submission
├── submission_status.json           # Current submission status
├── processed_feedback.json          # Analyzed editor feedback
├── Editor_Feedback_Report.xlsx      # Excel report of feedback
├── integration_report.json          # Results of change integration
├── change_summary.json              # Summary of all changes
├── backups/                         # Backup of original files
│   └── manuscript_pre_integration.md
├── versions/                        # Version history
│   ├── v001_20260128_120000/
│   ├── v002_20260130_150000/
│   └── version_history.json
└── submissions/                     # Submission tracking
    └── submission_history.json
```

---

## 🔗 Related Resources

1. **MDPI Language Editing Service:** https://www.mdpi.com/authors/english
2. **Aerospace Journal Guidelines:** https://www.mdpi.com/journal/aerospace/instructions
3. **Reference Style Guide:** https://www.mdpi.com/authors/references
4. **Figure Requirements:** https://www.mdpi.com/authors/layout
5. **Ethical Guidelines:** https://www.mdpi.com/ethics

---

## 📞 Support

For issues with the professional editing service:

1. **Script Issues:** Check `scripts/professional_editing_service.py` documentation
2. **MDPI Process:** Contact MDPI support at english@mdpi.com
3. **Technical Questions:** Refer to project documentation in `docs/`
4. **Integration Problems:** Verify Tasks 4.1-4.4 are completed

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-28 | Initial guide for Task 4.5 | System |
| 1.1 | 2026-01-28 | Added troubleshooting section | System |

---

**Last Updated:** 2026-01-28  
**Next Review:** 2026-02-28  
**Status:** Active ✅