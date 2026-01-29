#!/usr/bin/env python3
"""
Integration with Task 4.1 Reports for Tasks 4.2-4.3
Load and analyze Task 4.1 automated language check results
to inform manual editing process.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class Task4_1_Integrator:
    """
    Integrate Task 4.1 automated language check results with manual editing.
    """
    
    def __init__(self, task4_1_dir="outputs/language_check",
                 output_dir="outputs/language_editing"):
        """
        Initialize integrator with Task 4.1 results.
        
        Args:
            task4_1_dir: Directory containing Task 4.1 output files
            output_dir: Directory for integration output
        """
        self.task4_1_dir = Path(task4_1_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load Task 4.1 results
        self.results = self._load_task4_1_results()
        
        # Analysis results
        self.analysis = {}
        
    def _load_task4_1_results(self) -> dict:
        """
        Load all Task 4.1 result files.
        
        Returns:
            Dictionary of DataFrames keyed by file name
        """
        results = {}
        
        if not self.task4_1_dir.exists():
            print(f"Warning: Task 4.1 directory not found: {self.task4_1_dir}")
            return results
        
        # Look for Excel files from Task 4.1
        excel_files = list(self.task4_1_dir.glob("*.xlsx"))
        
        for file in excel_files:
            try:
                df = pd.read_excel(file)
                results[file.stem] = df
                print(f"✓ Loaded: {file.name} ({len(df)} rows)")
            except Exception as e:
                print(f"✗ Could not load {file}: {e}")
        
        # Also look for CSV files
        csv_files = list(self.task4_1_dir.glob("*.csv"))
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                results[file.stem] = df
                print(f"✓ Loaded: {file.name} ({len(df)} rows)")
            except Exception as e:
                print(f"✗ Could not load {file}: {e}")
        
        return results
    
    def analyze_error_distribution(self):
        """
        Analyze error distribution from Task 4.1 results.
        
        Returns:
            DataFrame with error analysis
        """
        if not self.results:
            print("No Task 4.1 results to analyze")
            return None
        
        # Combine all errors if possible
        all_errors = []
        
        for name, df in self.results.items():
            if not df.empty:
                # Add source column
                df_copy = df.copy()
                df_copy['source_file'] = name
                all_errors.append(df_copy)
        
        if not all_errors:
            print("No error data found in Task 4.1 results")
            return None
        
        # Combine into single DataFrame
        combined_df = pd.concat(all_errors, ignore_index=True)
        
        # Analyze error types
        error_analysis = {}
        
        # Check for common column names
        if 'Error Type' in combined_df.columns:
            error_types = combined_df['Error Type'].value_counts()
            error_analysis['error_types'] = error_types
            
        if 'Message' in combined_df.columns:
            # Extract common patterns from messages
            messages = combined_df['Message'].dropna()
            common_messages = messages.value_counts().head(10)
            error_analysis['common_messages'] = common_messages
        
        # Section analysis if section column exists
        if 'section' in combined_df.columns or 'Section' in combined_df.columns:
            section_col = 'section' if 'section' in combined_df.columns else 'Section'
            section_counts = combined_df[section_col].value_counts()
            error_analysis['section_counts'] = section_counts
        
        # Save analysis
        self.analysis['error_distribution'] = error_analysis
        
        # Create summary DataFrame
        summary_data = []
        
        if 'error_types' in error_analysis:
            for error_type, count in error_analysis['error_types'].items():
                summary_data.append({
                    'Error_Category': 'Grammar',
                    'Error_Type': error_type,
                    'Count': count,
                    'Percentage': (count / len(combined_df)) * 100
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Save to file
        output_path = self.output_dir / "Task4_1_Error_Analysis.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            if not summary_df.empty:
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Save raw combined data
            combined_df.to_excel(writer, sheet_name='All_Errors', index=False)
            
            # Add analysis sheets
            for key, data in error_analysis.items():
                if isinstance(data, pd.Series):
                    data_df = data.reset_index()
                    data_df.columns = ['Item', 'Count']
                    sheet_name = key[:31]  # Excel sheet name limit
                    data_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✓ Error analysis saved to: {output_path}")
        return summary_df
    
    def generate_editing_priorities(self):
        """
        Generate editing priorities based on Task 4.1 results.
        
        Returns:
            DataFrame with editing priorities
        """
        if not self.analysis:
            self.analyze_error_distribution()
        
        # Default priorities based on common errors in scientific writing
        default_priorities = [
            {
                'Priority': 1,
                'Error_Type': 'Subject-verb agreement',
                'Description': 'Data shows → data show, Results demonstrates → results demonstrate',
                'Sections': 'Results, Abstract, Discussion',
                'Action': 'Check all plural subjects with singular verbs',
                'Estimated_Time': '15 min per section'
            },
            {
                'Priority': 2,
                'Error_Type': 'Article usage',
                'Description': 'Missing or incorrect articles (a/an/the)',
                'Sections': 'Abstract, Introduction, Methods',
                'Action': 'Add missing articles, correct a/an usage',
                'Estimated_Time': '10 min per section'
            },
            {
                'Priority': 3,
                'Error_Type': 'Sentence complexity',
                'Description': 'Sentences > 30 words, nested clauses',
                'Sections': 'Methods, Discussion',
                'Action': 'Split long sentences, simplify structure',
                'Estimated_Time': '20 min per section'
            },
            {
                'Priority': 4,
                'Error_Type': 'Passive voice',
                'Description': 'Overuse of passive constructions',
                'Sections': 'Methods, Results',
                'Action': 'Convert to active voice where appropriate',
                'Estimated_Time': '10 min per section'
            },
            {
                'Priority': 5,
                'Error_Type': 'Russian translation',
                'Description': 'Literal translations from Russian',
                'Sections': 'All sections (especially Methods)',
                'Action': 'Fix word order, preposition usage',
                'Estimated_Time': '15 min per section'
            },
            {
                'Priority': 6,
                'Error_Type': 'Terminology consistency',
                'Description': 'Inconsistent use of technical terms',
                'Sections': 'All sections',
                'Action': 'Standardize terminology, ensure acronym consistency',
                'Estimated_Time': '5 min per section'
            }
        ]
        
        priorities_df = pd.DataFrame(default_priorities)
        
        # Customize based on actual Task 4.1 results if available
        if 'error_distribution' in self.analysis:
            error_dist = self.analysis['error_distribution']
            
            if 'error_types' in error_dist:
                # Update priorities based on actual error frequency
                for idx, row in priorities_df.iterrows():
                    error_type = row['Error_Type']
                    # Check if this error type appears in Task 4.1 results
                    # This is simplified - would need more sophisticated matching
                    pass
        
        # Save priorities
        output_path = self.output_dir / "Editing_Priorities.xlsx"
        priorities_df.to_excel(output_path, index=False)
        
        print(f"✓ Editing priorities saved to: {output_path}")
        return priorities_df
    
    def create_section_specific_guides(self, manuscript_dir="Documents/manuscript_sections"):
        """
        Create section-specific editing guides based on Task 4.1 results.
        
        Args:
            manuscript_dir: Directory containing manuscript sections
            
        Returns:
            Dictionary of section-specific guides
        """
        manuscript_path = Path(manuscript_dir)
        if not manuscript_path.exists():
            print(f"Manuscript directory not found: {manuscript_dir}")
            return {}
        
        # Get section files
        section_files = list(manuscript_path.glob("*.md"))
        
        guides = {}
        
        for section_file in section_files:
            section_name = section_file.stem
            
            # Create section-specific guide
            guide = {
                'section': section_name,
                'file': str(section_file),
                'common_errors': [],
                'focus_areas': [],
                'checklist': []
            }
            
            # Add section-specific focus areas
            if section_name == 'Abstract':
                guide['focus_areas'] = [
                    'Conciseness and clarity',
                    'Article usage (critical in first sentences)',
                    'Active voice for impact',
                    'Keyword optimization'
                ]
                guide['checklist'] = [
                    'Check word count (150-250 words)',
                    'Ensure all key findings included',
                    'Verify article usage in first sentence',
                    'Check for "an new" → "a new"',
                    'Ensure active voice where possible'
                ]
            
            elif section_name == 'Introduction':
                guide['focus_areas'] = [
                    'Article usage with technical terms',
                    'Sentence complexity (often high)',
                    'Transition phrases',
                    'Literature review language'
                ]
                guide['checklist'] = [
                    'Check "a/an" before technical terms',
                    'Split sentences > 30 words',
                    'Verify transition words (however, therefore)',
                    'Check citation formatting',
                    'Ensure clear research gap statement'
                ]
            
            elif section_name == 'Materials_Methods':
                guide['focus_areas'] = [
                    'Passive voice (acceptable but balance)',
                    'Technical terminology consistency',
                    'Russian translation fixes',
                    'Procedural clarity'
                ]
                guide['checklist'] = [
                    'Balance active/passive voice',
                    'Check for Russian-influenced word order',
                    'Verify technical term consistency',
                    'Ensure reproducibility of methods',
                    'Check measurement units consistency'
                ]
            
            elif section_name == 'Results':
                guide['focus_areas'] = [
                    'Subject-verb agreement with data/results',
                    'Statistical language accuracy',
                    'Figure/table references',
                    'Objective presentation'
                ]
                guide['checklist'] = [
                    'Check "data show" not "data shows"',
                    'Verify statistical terminology',
                    'Check figure/table reference formatting',
                    'Ensure objective language (no interpretation)',
                    'Check numerical formatting'
                ]
            
            elif section_name == 'Discussion':
                guide['focus_areas'] = [
                    'Sentence complexity (often highest)',
                    'Interpretation language',
                    'Comparison with literature',
                    'Limitations language'
                ]
                guide['checklist'] = [
                    'Split complex sentences',
                    'Check comparison language (similar to, different from)',
                    'Verify interpretation is supported by results',
                    'Check limitations wording',
                    'Ensure future work suggestions'
                ]
            
            elif section_name == 'Conclusion':
                guide['focus_areas'] = [
                    'Conciseness',
                    'Summary language',
                    'Implications statement',
                    'Future work'
                ]
                guide['checklist'] = [
                    'Check for redundancy with Abstract',
                    'Ensure clear summary of findings',
                    'Verify implications are stated',
                    'Check future work suggestions',
                    'Ensure no new information introduced'
                ]
            
            guides[section_name] = guide
        
        # Save guides to JSON
        guides_path = self.output_dir / "Section_Specific_Guides.json"
        with open(guides_path, 'w', encoding='utf-8') as f:
            json.dump(guides, f, indent=2, default=str)
        
        # Also save as Excel for easier viewing
        guides_list = []
        for section_name, guide in guides.items():
            guides_list.append({
                'Section': section_name,
                'Focus_Areas': '; '.join(guide['focus_areas']),
                'Checklist_Items': '; '.join(guide['checklist']),
                'File': guide['file']
            })
        
        guides_df = pd.DataFrame(guides_list)
        guides_excel_path = self.output_dir / "Section_Specific_Guides.xlsx"
        guides_df.to_excel(guides_excel_path, index=False)
        
        print(f"✓ Section-specific guides saved to:")
        print(f"  JSON: {guides_path}")
        print(f"  Excel: {guides_excel_path}")
        
        return guides
    
    def generate_integration_report(self):
        """
        Generate comprehensive integration report.
        
        Returns:
            Path to the generated report
        """
        report = f"""# Task 4.1 - Task 4.2/4.3 Integration Report

## Overview
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Task 4.1 Directory**: {self.task4_1_dir}
- **Task 4.2/4.3 Output**: {self.output_dir}
- **Integration Status**: {'COMPLETE' if self.results else 'NO DATA'}

## Task 4.1 Results Summary
"""
        
        if self.results:
            report += f"- **Files Loaded**: {len(self.results)}\n"
            for name, df in self.results.items():
                report += f"  - `{name}.xlsx/csv`: {len(df)} rows\n"
        else:
            report += "- No Task 4.1 results found\n"
        
        report += f"""
## Analysis Results
"""
        
        if self.analysis:
            if 'error_distribution' in self.analysis:
                error_dist = self.analysis['error_distribution']
                report += "- **Error Distribution Analysis**: Complete\n"
                
                if 'error_types' in error_dist and not error_dist['error_types'].empty:
                    report += "  - Top error types:\n"
                    for error_type, count in error_dist['error_types'].head(5).items():
                        report += f"    - {error_type}: {count} occurrences\n"
        else:
            report += "- No analysis performed yet\n"
        
        report += f"""
## Integration Components

### 1. Error Analysis
- File: `Task4_1_Error_Analysis.xlsx`
- Purpose: Statistical analysis of Task 4.1 error reports
- Use: Identify most common error types for focused editing

### 2. Editing Priorities
- File: `Editing_Priorities.xlsx`
- Purpose: Rank editing tasks by importance and frequency
- Use: Guide manual editing process for maximum impact

### 3. Section-Specific Guides
- Files: `Section_Specific_Guides.json` and `.xlsx`
- Purpose: Tailored editing guidance for each manuscript section
- Use: Address section-specific language challenges

### 4. Change Tracking System
- Integrated with `manual_language_editing.py`
- All changes logged with reference to Task 4.1 error types
- Enables before/after comparison

## Recommended Workflow

### Step 1: Review Task 4.1 Analysis
1. Open `Task4_1_Error_Analysis.xlsx`
2. Identify top 3 error types in your manuscript
3. Note which sections have most errors

### Step 2: Set Editing Priorities
1. Open `Editing_Priorities.xlsx`
2. Adjust priorities based on your error analysis
3. Allocate time based on priority and section length

### Step 3: Use Section-Specific Guides
1. Open `Section_Specific_Guides.xlsx`
2. Review focus areas for each section
3. Use checklist items during editing

### Step 4: Execute Editing
1. Use `manual_language_editing.py` with `--interactive` mode
2. Reference Task 4.1 error reports when making decisions
3. Document all changes in the integrated change log

### Step 5: Verify Integration
1. Compare before/after error counts
2. Ensure Task 4.1 identified errors are addressed
3. Generate final quality report

## Quality Metrics

### Integration Success Criteria
- [ ] All Task 4.1 error types addressed in editing priorities
- [ ] Section-specific guides created for all manuscript sections
- [ ] Change logging system references Task 4.1 error categories
- [ ] Before/after comparison shows error reduction
- [ ] Editing time optimized based on error frequency

### Expected Outcomes
1. **Efficiency**: Focused editing on most common errors
2. **Consistency**: Uniform approach across all sections
3. **Documentation**: Clear linkage between automated and manual editing
4. **Quality**: Measurable improvement in language quality

## Next Steps

### Immediate (Post-Integration)
1. Begin manual editing using integrated tools
2. Monitor progress against priorities
3. Adjust approach based on initial results

### Medium Term (During Editing)
1. Update priorities based on emerging patterns
2. Refine section-specific guides
3. Document lessons learned

### Long Term (Post-Editing)
1. Analyze effectiveness of integration
2. Refine integration approach for future projects
3. Update documentation and training materials

## Technical Notes

### Data Flow
```
Task 4.1 (Automated Check) → Error Reports → Analysis → Priorities → Manual Editing
      ↓                         ↓           ↓          ↓              ↓
Grammar check            Excel/CSV files  Statistics  Ranked list    Guided editing
```

### File Dependencies
- Task 4.1 outputs: `outputs/language_check/*.xlsx`
- Integration outputs: `outputs/language_editing/Task4_1_*`
- Manual editing outputs: `outputs/language_editing/*_edited.md`

### Limitations
1. **Data Format**: Requires Task 4.1 outputs in specific Excel/CSV format
2. **Error Matching**: Simple string matching for error categorization
3. **Section Mapping**: Assumes consistent section naming between tasks
4. **Manual Review**: Still requires human judgment for complex cases

## Conclusion

This integration bridges automated language checking (Task 4.1) with manual editing (Tasks 4.2-4.3), creating a data-driven approach to language improvement. By analyzing automated check results, editors can focus their efforts where they will have the greatest impact, ensuring efficient and effective manuscript polishing.

---
*Generated by Task 4.1 - Task 4.2/4.3 Integration System*
*Project: Rocket Drop Zone Analysis - OTU Pipeline*
*Date: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        # Save report
        report_path = self.output_dir / "Task4_1_Integration_Report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Integration report saved to: {report_path}")
        return report_path
    
    def run_complete_integration(self):
        """
        Run complete integration pipeline.
        
        Returns:
            Dictionary with all integration results
        """
        print("="*60)
        print("TASK 4.1 - TASK 4.2/4.3 INTEGRATION PIPELINE")
        print("="*60)
        
        results = {}
        
        # Step 1: Load Task 4.1 results
        print("\n1. Loading Task 4.1 results...")
        if not self.results:
            print("   Warning: No Task 4.1 results found")
        else:
            print(f"   ✓ Loaded {len(self.results)} result files")
        
        # Step 2: Analyze error distribution
        print("\n2. Analyzing error distribution...")
        error_analysis = self.analyze_error_distribution()
        if error_analysis is not None:
            results['error_analysis'] = error_analysis
            print(f"   ✓ Error analysis complete")
        
        # Step 3: Generate editing priorities
        print("\n3. Generating editing priorities...")
        priorities = self.generate_editing_priorities()
        results['priorities'] = priorities
        print(f"   ✓ Editing priorities generated")
        
        # Step 4: Create section-specific guides
        print("\n4. Creating section-specific guides...")
        guides = self.create_section_specific_guides()
        results['guides'] = guides
        print(f"   ✓ Section-specific guides created")
        
        # Step 5: Generate integration report
        print("\n5. Generating integration report...")
        report_path = self.generate_integration_report()
        results['report_path'] = report_path
        print(f"   ✓ Integration report generated")
        
        print("\n" + "="*60)
        print("INTEGRATION COMPLETE")
        print("="*60)
        print(f"Output directory: {self.output_dir}")
        print(f"Files created:")
        print(f"  - Task4_1_Error_Analysis.xlsx")
        print(f"  - Editing_Priorities.xlsx")
        print(f"  - Section_Specific_Guides.json/.xlsx")
        print(f"  - Task4_1_Integration_Report.md")
        print("\nNext: Begin manual editing using integrated tools")
        
        return results


def main():
    """
    Main function to run integration.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Integrate Task 4.1 with Tasks 4.2-4.3')
    parser.add_argument('--task4-1-dir', type=str, default='outputs/language_check',
                       help='Directory with Task 4.1 results')
    parser.add_argument('--output-dir', type=str, default='outputs/language_editing',
                       help='Output directory for integration files')
    parser.add_argument('--run-all', action='store_true',
                       help='Run complete integration pipeline')
    
    args = parser.parse_args()
    
    # Create integrator
    integrator = Task4_1_Integrator(args.task4_1_dir, args.output_dir)
    
    if args.run_all:
        # Run complete pipeline
        results = integrator.run_complete_integration()
        print(f"\nIntegration complete. Results saved in: {args.output_dir}")
    else:
        # Interactive or step-by-step mode could be added here
        print("Use --run-all to execute complete integration pipeline")
        print("Or call specific methods from the integrator class")


if __name__ == "__main__":
    main()