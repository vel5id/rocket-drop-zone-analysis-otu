# Language Editing Guide
## For Tasks 4.2-4.3: Manual Language Editing

**Version:** 1.0  
**Date:** 2026-01-28  
**Project:** Rocket Drop Zone Analysis - OTU Pipeline  
**Based on:** IMPLEMENTATION_ROADMAP.md lines 535-551

---

## Table of Contents

1. [Introduction](#introduction)
2. [Editing Categories](#editing-categories)
3. [Tools and Scripts](#tools-and-scripts)
4. [Step-by-Step Workflow](#step-by-step-workflow)
5. [Common Error Patterns](#common-error-patterns)
6. [Quality Assurance](#quality-assurance)
7. [Integration with Task 4.1](#integration-with-task-41)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Introduction

### Purpose
This guide provides comprehensive instructions for manual language editing of scientific manuscripts, specifically designed for the Rocket Drop Zone Analysis project. The editing focuses on six key categories as specified in Tasks 4.2-4.3.

### Target Audience
- Manuscript editors
- Authors reviewing automated suggestions
- Research assistants performing language polishing
- Project managers ensuring quality control

### Scope
This guide covers:
- Article usage correction (a/an/the)
- Subject-verb agreement
- Sentence simplification (>30 words)
- Active voice conversion
- Russian translation fixes
- Terminology consistency

---

## Editing Categories

### 1. Article Usage (a/an/the)

#### Common Issues
- **Missing articles**: "Methodology was developed" → "The methodology was developed"
- **Incorrect articles**: "An new approach" → "A new approach"
- **Unnecessary articles**: "The data shows" → "Data shows" (context-dependent)

#### Rules to Apply
1. Use "a" before consonant sounds: "a methodology", "a university"
2. Use "an" before vowel sounds: "an approach", "an hour"
3. Use "the" for specific references: "the methodology described above"
4. Omit articles for general concepts: "Data were collected" (plural general)

#### Examples from Manuscript
```text
Original: "This paper presents an new methodology"
Fixed:    "This paper presents a new methodology"

Original: "Methodology was developed for analysis"
Fixed:    "The methodology was developed for analysis"
```

### 2. Subject-Verb Agreement

#### Common Issues
- **Singular subject with plural verb**: "The data shows" → "The data show"
- **Plural subject with singular verb**: "Results demonstrates" → "Results demonstrate"
- **Collective noun confusion**: "The team are" → "The team is"

#### Rules to Apply
1. Identify the true subject (not prepositional phrases)
2. Match verb to subject number
3. Treat collective nouns as singular (team, group, committee)
4. Treat data as plural (datum is singular)

#### Examples from Manuscript
```text
Original: "Results demonstrates high correlation"
Fixed:    "Results demonstrate high correlation"

Original: "The data was analyzed"
Fixed:    "The data were analyzed"
```

### 3. Sentence Simplification (>30 words)

#### Guidelines
- Target: Maximum 25-30 words per sentence
- Split at logical connectors (and, but, however, which)
- Convert complex clauses to separate sentences
- Maintain technical accuracy while improving readability

#### Simplification Strategies
1. **Split compound sentences**: Use periods instead of semicolons
2. **Reduce prepositional phrases**: "in the context of" → "for"
3. **Eliminate redundant phrases**: "it is important to note that" → ""
4. **Use bullet points for lists**

#### Examples
```text
Original (42 words): "The methodology, which was developed specifically for this study 
and incorporates multiple data sources including satellite imagery, topographic data, 
and ecological indices, provides a comprehensive framework for analysis."

Simplified: "We developed a methodology specifically for this study. It incorporates 
multiple data sources: satellite imagery, topographic data, and ecological indices. 
This provides a comprehensive framework for analysis."
```

### 4. Active Voice Conversion

#### When to Use Active Voice
- Describing actions performed by the research team
- Emphasizing agency and responsibility
- Improving clarity and directness

#### When Passive Voice is Acceptable
- Emphasizing the action over the actor
- Standard scientific reporting ("samples were collected")
- When the actor is unknown or unimportant

#### Conversion Patterns
```text
Passive: "The analysis was conducted by the research team"
Active:  "The research team conducted the analysis"

Passive: "It was found that the correlation was significant"
Active:  "We found a significant correlation"

Passive: "Data were collected from multiple sources"
Active:  "We collected data from multiple sources" (or keep passive if standard)
```

### 5. Russian Translation Fixes

#### Common Russian-English Interference
1. **Word order**: Adjective after noun → "methodology new" → "new methodology"
2. **Article omission**: Russian lacks articles → add appropriate a/an/the
3. **Preposition choice**: "according to results" → "based on the results"
4. **Verb patterns**: "was conducted analysis" → "analysis was conducted"

#### Specific Fixes
```text
Russian-influenced: "In accordance with methodology"
Natural English:    "According to the methodology"

Russian-influenced: "Analysis detailed shows"
Natural English:    "Detailed analysis shows"

Russian-influenced: "In framework of study"
Natural English:    "Within the study framework"
```

### 6. Terminology Consistency

#### Standardized Terms
| Preferred Term | Acceptable Variants | Avoid |
|----------------|---------------------|-------|
| OTU | Optimal Touchdown Unit, OTU score | touchdown unit, optimal unit |
| NDVI | Normalized Difference Vegetation Index | vegetation index, NDVI value |
| DEM | Digital Elevation Model | elevation model, topographic model |
| Baikonur Cosmodrome | Baikonur | Baikonur spaceport |
| rocket stage | launch vehicle stage, booster | rocket part, stage |

#### Consistency Rules
1. Use full term at first mention with acronym in parentheses
2. Use acronym thereafter
3. Maintain consistent capitalization
4. Use same terminology across all sections

---

## Tools and Scripts

### Available Tools

#### 1. Manual Language Editor (`scripts/manual_language_editing.py`)
```bash
# Basic usage
python scripts/manual_language_editing.py --all

# Interactive mode
python scripts/manual_language_editing.py --interactive --section Abstract.md

# Specific section
python scripts/manual_language_editing.py --section Introduction.md
```

#### 2. Interactive Editor (`scripts/interactive_language_editor.py`)
```bash
# Launch interactive interface
python scripts/interactive_language_editor.py
```

#### 3. Batch Script (`run_language_editing.bat`)
```bash
# Windows batch file
run_language_editing.bat
```

### Output Files
- `outputs/language_editing/[section]_edited.md` - Edited manuscript sections
- `outputs/language_editing/[section]_changes.csv` - Detailed change logs
- `outputs/language_editing/Editing_Change_Log.xlsx` - Excel change log
- `outputs/language_editing/Language_Quality_Report.md` - Summary report

---

## Step-by-Step Workflow

### Phase 1: Preparation
1. **Review Task 4.1 results**
   - Check `outputs/language_check/Grammar_Errors_Report.xlsx`
   - Identify most common error types
   - Prioritize sections with most issues

2. **Set up environment**
   ```bash
   # Activate virtual environment
   venv_311\Scripts\activate
   
   # Install dependencies (if needed)
   pip install pandas openpyxl
   ```

### Phase 2: Editing Process

#### Option A: Automated Batch Editing
```bash
# Apply all fixes to all sections
python scripts/manual_language_editing.py --all
```

#### Option B: Interactive Editing
```bash
# Launch interactive editor
python scripts/interactive_language_editor.py

# Follow menu prompts:
# 1. Select section
# 2. Choose editing mode
# 3. Review changes
# 4. Save and export
```

#### Option C: Section-by-Section
```bash
# Edit specific sections
python scripts/manual_language_editing.py --section Abstract.md
python scripts/manual_language_editing.py --section Introduction.md
# ... etc.
```

### Phase 3: Quality Control
1. **Review edited files**
   - Compare original vs edited versions
   - Check for over-correction
   - Ensure technical accuracy maintained

2. **Verify change logs**
   - Review `Editing_Change_Log.xlsx`
   - Ensure all changes are documented
   - Check change type distribution

3. **Generate final report**
   - Review `Language_Quality_Report.md`
   - Update metrics if needed
   - Document any manual overrides

### Phase 4: Integration
1. **Update manuscript sections**
   - Replace original files with edited versions
   - Maintain backup of originals
   - Update version control

2. **Prepare for Task 4.4**
   - Ensure bibliography formatting is next
   - Document any remaining issues
   - Update project tracking

---

## Common Error Patterns

### High-Frequency Errors in Scientific Writing

#### 1. Article Errors in Technical Context
```text
Pattern: "[A/An] [technical term starting with vowel/consonant sound]"
Example: "An UAV was used" → "A UAV was used" (U sounds like "you")
```

#### 2. Subject-Verb with Data/Results
```text
Pattern: "The data/results [singular verb]"
Fix: "The data/results [plural verb]"
Example: "The data shows" → "The data show"
```

#### 3. Russian Translation Patterns
```text
Pattern: "[Noun] [Adjective]" (Russian word order)
Fix: "[Adjective] [Noun]"
Example: "analysis statistical" → "statistical analysis"
```

#### 4. Passive Voice Clusters
```text
Pattern: "It was [verb]ed that [clause]"
Fix: "We [verb]ed [clause]"
Example: "It was determined that" → "We determined that"
```

### Error Severity Classification
- **Critical**: Changes meaning or causes confusion
- **Major**: Noticeable to native readers, affects readability
- **Minor**: Subtle issues, primarily stylistic

---

## Quality Assurance

### Pre-Editing Checklist
- [ ] All manuscript sections available in `Documents/manuscript_sections/`
- [ ] Task 4.1 reports reviewed
- [ ] Virtual environment activated
- [ ] Output directory created (`outputs/language_editing/`)

### During Editing
- [ ] Technical accuracy preserved
- [ ] Consistency maintained across sections
- [ ] Change log updated for each edit
- [ ] Regular saves and backups

### Post-Editing Verification
- [ ] All sections edited
- [ ] Change logs complete and accurate
- [ ] Quality report generated
- [ ] Files organized in output directory
- [ ] No introduced errors

### Metrics to Track
1. **Change count per section**
2. **Error type distribution**
3. **Before/after word count**
4. **Sentence length reduction**
5. **Active/passive voice ratio**

---

## Integration with Task 4.1

### Using Automated Check Results
The manual editing process should reference and address issues identified in Task 4.1:

#### 1. Load Error Reports
```python
# In manual_language_editing.py
check_results = pd.read_excel('outputs/language_check/Grammar_Errors_Report.xlsx')
```

#### 2. Prioritize Based on Frequency
- Focus on most common error types first
- Address critical errors before minor ones
- Use automated suggestions as starting point

#### 3. Compare Before/After
- Run automated check on edited versions
- Compare error counts
- Ensure reduction in identified issues

### Data Flow
```
Task 4.1 (Automated) → Error Reports → Task 4.2-4.3 (Manual) → Edited Manuscript
       ↓                    ↓                    ↓                    ↓
Grammar check        Excel reports        Interactive editing    Quality report
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Script Not Running
```text
Issue: "ModuleNotFoundError: No module named 'pandas'"
Solution: Install dependencies in virtual environment
Command: pip install pandas openpyxl numpy
```

#### 2. File Not Found
```text
Issue: "Section file not found"
Solution: Check file paths and directory structure
Verify: Documents/manuscript_sections/[section].md exists
```

#### 3. Encoding Problems
```text
Issue: UnicodeDecodeError
Solution: Specify UTF-8 encoding
Code: with open(file, 'r', encoding='utf-8') as f:
```

#### 4. Change Log Not Updating
```text
Issue: Changes not saved to Excel
Solution: Check file permissions and close Excel if open
Verify: output directory exists and is writable
```

#### 5. Over-Correction
```text
Issue: Script changes correct text
Solution: Use interactive mode to review each change
Alternative: Adjust pattern matching in script
```

### Getting Help
1. Check script documentation and comments
2. Review error messages carefully
3. Consult this guide for specific error patterns
4. Contact project technical lead for complex issues

---

## References

### Project Documents
- IMPLEMENTATION_ROADMAP.md (lines 535-551)
- Task_4_1_Automated_Language_Check_Report.md
- Project style guide (if available)

### External Resources
- APA Style Guide (for scientific writing)
- Chicago Manual of Style
- Grammarly Handbook
- Purdue OWL (Online Writing Lab)

### Tools and Software
- LanguageTool (used in Task 4.1)
- Python 3.11 with pandas, openpyxl
- Visual Studio Code (recommended editor)

### Best Practices
1. **Consistency over perfection**: Choose one style and stick to it
2. **Technical accuracy first**: Never sacrifice meaning for style
3. **Iterative approach**: Multiple passes yield better results
4. **Collaborative review**: Have another person review edits
5. **Document everything**: Maintain complete change logs

---

## Appendix

### A. Quick Reference Card

#### Command Summary
```bash
# Batch edit all sections
python scripts/manual_language_editing.py --all

# Interactive editing
python scripts/interactive_language_editor.py

# Edit specific section
python scripts/manual_language_editing.py --section Abstract.md

# With custom output directory
python scripts/manual_language_editing.py --all --output-dir my_edits
```

#### Common Fix Patterns
- `an new` → `a new`
- `data shows` → `data show`
- `was developed by` → `developed`
- `methodology new` → `new methodology`
- `OTU score` → `OTU` (after first mention)

### B. Change Log Template
```csv
section,line_number,original,fixed,change_type,timestamp
Abstract,3,"an new methodology","a new methodology","article_fix","2026-01-28T10:30:00"
Introduction,5,"Results demonstrates","Results demonstrate","subject_verb_agreement","2026-01-28T10:31:00"
```

### C. Quality Metrics Template
```markdown
## Editing Statistics
- Total sections: 6
- Total changes: 142
- Average changes per section: 23.7
- Most changes: Materials_Methods (38)
- Least changes: Conclusion (12)

## Improvement Metrics
- Article errors reduced: 85%
- Subject-verb errors: 92%
- Average sentence length: 28 → 22 words
- Active voice increased: 45% → 68%
```

---

**End of Guide**

*This guide is part of the Rocket Drop Zone Analysis - OTU Pipeline project.*  
*For updates or corrections, contact the project documentation lead.*