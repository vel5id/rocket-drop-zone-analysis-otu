# Editing Checklist
## For Tasks 4.2-4.3: Manual Language Editing

**Version:** 1.0  
**Date:** 2026-01-28  
**Project:** Rocket Drop Zone Analysis - OTU Pipeline  
**Based on:** IMPLEMENTATION_ROADMAP.md lines 535-551

---

## Overview

This checklist provides a systematic approach to manual language editing of scientific manuscripts. Use this checklist to ensure comprehensive coverage of all editing categories and maintain consistency across all manuscript sections.

### How to Use This Checklist
1. **Complete all items** in each section before moving to the next
2. **Check off items** as you complete them
3. **Document exceptions** in the notes section
4. **Review completed checklist** before finalizing edits
5. **Save completed checklist** with edited files

---

## Pre-Editing Preparation

### Environment Setup
- [ ] Virtual environment `venv_311` activated
- [ ] Required packages installed: `pandas`, `openpyxl`, `numpy`
- [ ] Output directory created: `outputs/language_editing/`
- [ ] Backup of original manuscript sections created

### Document Review
- [ ] All manuscript sections available in `Documents/manuscript_sections/`
- [ ] Task 4.1 reports reviewed: `outputs/language_check/`
- [ ] Common Errors Catalog available: `Common_Errors_Catalog.xlsx`
- [ ] Language Editing Guide reviewed

### Tool Configuration
- [ ] `manual_language_editing.py` script tested
- [ ] `interactive_language_editor.py` script tested
- [ ] Batch file `run_language_editing.bat` ready
- [ ] Text editor/IDE configured for markdown viewing

---

## Section-by-Section Editing

### For EACH Manuscript Section (Abstract, Introduction, etc.)

#### 1. Article Usage Check (a/an/the)
- [ ] Scan for "an new" → correct to "a new"
- [ ] Check "a university" (correct) vs "an university" (incorrect)
- [ ] Verify "an hour" (correct) vs "a hour" (incorrect)
- [ ] Add missing articles before singular nouns: "methodology" → "the methodology"
- [ ] Remove unnecessary articles where appropriate
- [ ] Check consistency of article usage throughout section
- [ ] Document all article corrections in change log

#### 2. Subject-Verb Agreement Check
- [ ] Verify "data show" (plural) not "data shows" (singular)
- [ ] Check "results demonstrate" not "results demonstrates"
- [ ] Confirm collective nouns: "team is" not "team are"
- [ ] Verify subject-verb agreement in complex sentences
- [ ] Check for intervening phrases that might confuse agreement
- [ ] Ensure consistency in tense throughout section
- [ ] Document all subject-verb corrections

#### 3. Sentence Complexity Review
- [ ] Identify sentences longer than 30 words
- [ ] Split overly complex sentences at logical break points
- [ ] Convert nested clauses to separate sentences
- [ ] Reduce prepositional phrase chains
- [ ] Eliminate redundant phrases and wordiness
- [ ] Maintain technical accuracy while simplifying
- [ ] Check readability after simplification
- [ ] Document sentence simplifications

#### 4. Active Voice Conversion
- [ ] Identify passive constructions: "was developed", "were collected"
- [ ] Convert to active voice where appropriate: "we developed", "we collected"
- [ ] Retain passive voice for standard scientific reporting
- [ ] Check for "It was found that" → convert to "We found that"
- [ ] Ensure consistent use of "we" or "the research team"
- [ ] Balance active and passive voice appropriately
- [ ] Document voice conversions

#### 5. Russian Translation Fixes
- [ ] Check for adjective-noun order: "methodology new" → "new methodology"
- [ ] Fix preposition usage: "according to results" → "based on results"
- [ ] Correct literal translations: "in framework of" → "within the framework of"
- [ ] Fix verb patterns: "was conducted analysis" → "analysis was conducted"
- [ ] Add missing articles (common in Russian translations)
- [ ] Check for other Russian-influenced constructions
- [ ] Document translation fixes

#### 6. Terminology Consistency
- [ ] Verify first use of acronyms with full term: "Optimal Touchdown Unit (OTU)"
- [ ] Ensure consistent use of acronyms thereafter
- [ ] Check for variant terminology: "rocket stage" vs "booster" vs "launch vehicle stage"
- [ ] Verify consistent capitalization of technical terms
- [ ] Ensure consistent spelling: "re-entry" vs "reentry"
- [ ] Check geographical names: "Baikonur Cosmodrome" (full name)
- [ ] Document terminology standardization

#### 7. General Language Quality
- [ ] Check spelling of technical terms
- [ ] Verify punctuation, especially with citations
- [ ] Ensure consistent use of British vs American English
- [ ] Check for typographical errors
- [ ] Verify numerical formatting consistency
- [ ] Ensure proper use of abbreviations
- [ ] Check paragraph structure and flow

#### 8. Section-Specific Checks
- **Abstract**: Concise, complete summary, keywords appropriate
- **Introduction**: Clear research gap, objectives stated
- **Methods**: Reproducible, logically ordered, technically accurate
- **Results**: Objective presentation, appropriate statistics
- **Discussion**: Interpretation of results, limitations acknowledged
- **Conclusion**: Summary of findings, implications stated

---

## Cross-Section Consistency Checks

### After Editing ALL Sections

#### Terminology Consistency Across Sections
- [ ] OTU/Optimal Touchdown Unit usage consistent
- [ ] NDVI/Normalized Difference Vegetation Index consistent
- [ ] DEM/Digital Elevation Model consistent
- [ ] Acronym definitions consistent in first usage
- [ ] Technical term capitalization consistent
- [ ] Measurement units consistent (km vs kilometers)
- [ ] Date formats consistent

#### Style Consistency
- [ ] Heading levels consistent
- [ ] Citation format consistent
- [ ] Figure/table reference format consistent
- [ ] Number formatting consistent (1,000 vs 1000)
- [ ] List formatting consistent
- [ ] Emphasis (bold/italic) usage consistent

#### Narrative Flow
- [ ] Transitions between sections smooth
- [ ] Key concepts introduced before used
- [ ] Logical progression from introduction to conclusion
- [ ] Consistent perspective (first person vs third person)
- [ ] Tone consistent throughout

---

## Quality Assurance

### Technical Accuracy Verification
- [ ] Technical terms used correctly
- [ ] Mathematical formulas accurate
- [ ] Statistical methods described correctly
- [ ] References to figures/tables accurate
- [ ] Data values consistent with source material
- [ ] Methodological descriptions accurate
- [ ] No introduced factual errors

### Readability Assessment
- [ ] Average sentence length appropriate (20-25 words)
- [ ] Paragraph length appropriate (3-5 sentences)
- [ ] Technical jargon explained or defined
- [ ] Complex concepts broken down
- [ ] Transition words used appropriately
- [ ] Overall readability score improved

### Change Documentation
- [ ] All changes documented in change log
- [ ] Change type categorized correctly
- [ ] Original and fixed text recorded
- [ ] Section and line number recorded
- [ ] Timestamp recorded for each change
- [ ] Change log saved in multiple formats (CSV, Excel, JSON)

### Output File Verification
- [ ] Edited files saved with `_edited.md` suffix
- [ ] Original files preserved unchanged
- [ ] Change logs saved with corresponding section names
- [ ] Master change log (`Editing_Change_Log.xlsx`) created
- [ ] Quality report (`Language_Quality_Report.md`) generated
- [ ] All files organized in `outputs/language_editing/`

---

## Final Review

### Before Finalizing
- [ ] All checklist items completed
- [ ] All manuscript sections edited
- [ ] Change logs complete and accurate
- [ ] Quality report generated and reviewed
- [ ] Backup of all edited files created
- [ ] Version control updated (if applicable)

### Peer Review (If Available)
- [ ] Edited sections shared with colleague
- [ ] Feedback incorporated
- [ ] Final review of incorporated changes
- [ ] Approval documented

### Integration with Next Tasks
- [ ] Files prepared for Task 4.4 (Bibliography Formatting)
- [ ] Documentation updated for project tracking
- [ ] Progress reported in project management system
- [ ] Next steps identified and scheduled

---

## Post-Editing Tasks

### File Organization
- [ ] Original files: `Documents/manuscript_sections/` (preserved)
- [ ] Edited files: `outputs/language_editing/[section]_edited.md`
- [ ] Change logs: `outputs/language_editing/[section]_changes.csv`
- [ ] Master logs: `outputs/language_editing/Editing_Change_Log.*`
- [ ] Reports: `outputs/language_editing/Language_Quality_Report.md`
- [ ] Catalog: `outputs/language_editing/Common_Errors_Catalog.xlsx`

### Documentation
- [ ] Editing process documented
- [ ] Challenges and solutions noted
- [ ] Time spent recorded
- [ ] Quality metrics calculated
- [ ] Recommendations for future editing noted

### Cleanup
- [ ] Temporary files deleted
- [ ] Workspace organized
- [ ] Scripts and tools returned to ready state
- [ ] Virtual environment deactivated

---

## Quick Reference

### Common Error Patterns to Watch For
1. **ART-001**: `an new` → `a new`
2. **SVA-001**: `data shows` → `data show`
3. **SC-001**: Sentences > 30 words → split
4. **PV-001**: `It was found that` → `We found that`
5. **RT-001**: `methodology new` → `new methodology`
6. **TC-001**: Inconsistent acronym usage

### Editing Priorities
1. **Critical**: Errors that change meaning
2. **Major**: Errors affecting readability
3. **Minor**: Stylistic improvements

### Time Allocation Guide
- Abstract: 30-45 minutes
- Introduction: 60-90 minutes
- Methods: 90-120 minutes
- Results: 60-90 minutes
- Discussion: 90-120 minutes
- Conclusion: 30-45 minutes
- **Total**: 6-8 hours for complete manuscript

---

## Notes and Exceptions

### Section-Specific Notes
```
Abstract: 
- Focus on conciseness and clarity
- Ensure all key findings included
- Check word count limits

Methods:
- Technical accuracy paramount
- Ensure reproducibility
- Detailed but not verbose

Results: 
- Objective presentation only
- Statistical significance clear
- Figures/tables referenced correctly
```

### Exceptions Documented
| Section | Exception | Reason | Action Taken |
|---------|-----------|--------|--------------|
| | | | |
| | | | |
| | | | |

### Special Considerations
- [ ] Journal-specific style requirements
- [ ] Co-author preferences
- [ ] Cultural considerations in international collaboration
- [ ] Accessibility requirements
- [ ] Translation requirements

---

## Completion Sign-off

### Editor Information
- **Editor Name**: _________________________
- **Date Started**: _________________________
- **Date Completed**: _________________________
- **Total Time Spent**: _________________________
- **Sections Edited**: _________________________

### Quality Metrics
- **Total Changes Made**: _________________________
- **Critical Errors Fixed**: _________________________
- **Major Errors Fixed**: _________________________
- **Minor Improvements**: _________________________
- **Readability Improvement**: _________________________

### Approval
- [ ] All editing completed according to checklist
- [ ] Quality verified through review
- [ ] Files organized and documented
- [ ] Ready for next phase (Task 4.4)

**Editor Signature**: _________________________
**Date**: _________________________

**Reviewer Signature** (if applicable): _________________________
**Date**: _________________________

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-28 | Initial version for Tasks 4.2-4.3 | Rocket Drop Zone Analysis Team |
| | | | |

---

**End of Checklist**

*This checklist is part of the Rocket Drop Zone Analysis - OTU Pipeline project.*  
*Save completed checklist with edited files for documentation and quality assurance.*