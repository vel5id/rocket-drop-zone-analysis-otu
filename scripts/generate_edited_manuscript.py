#!/usr/bin/env python3
"""
Generate edited manuscript files for Tasks 4.2-4.3
Apply language fixes to all manuscript sections and save edited versions.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import sys
from pathlib import Path
from manual_language_editing import ManualLanguageEditor
import pandas as pd
from datetime import datetime

def generate_edited_manuscripts(output_dir="outputs/language_editing",
                               interactive=False,
                               sample_mode=False):
    """
    Generate edited versions of all manuscript sections.
    
    Args:
        output_dir: Directory to save edited files
        interactive: Whether to use interactive mode
        sample_mode: Only process first section as sample
        
    Returns:
        Dictionary with generation results
    """
    print("="*60)
    print("GENERATING EDITED MANUSCRIPT FILES")
    print("="*60)
    
    # Create editor
    editor = ManualLanguageEditor(output_dir=output_dir)
    
    # Get all manuscript sections
    section_files = list(editor.manuscript_dir.glob("*.md"))
    
    if not section_files:
        print(f"Error: No manuscript sections found in {editor.manuscript_dir}")
        return {}
    
    print(f"Found {len(section_files)} manuscript sections:")
    for section in section_files:
        print(f"  - {section.name}")
    
    if sample_mode:
        print("\nRunning in SAMPLE mode (processing first section only)")
        section_files = section_files[:1]
    
    results = {}
    
    # Process each section
    for section_file in section_files:
        section_name = section_file.stem
        print(f"\n{'='*40}")
        print(f"Processing: {section_name}")
        print(f"{'='*40}")
        
        # Edit the section
        result = editor.edit_section(section_file.name, interactive=interactive)
        
        if result:
            results[section_name] = result
            
            # Display summary
            print(f"✓ Edited: {section_name}")
            print(f"  Changes: {result['num_changes']}")
            print(f"  Edited file: {Path(result['edited_file']).name}")
            if result['changes_file']:
                print(f"  Changes log: {Path(result['changes_file']).name}")
        else:
            print(f"✗ Failed to edit: {section_name}")
    
    # Generate consolidated output
    if results:
        generate_consolidated_output(editor, results, output_dir)
    
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total sections processed: {len(results)}")
    
    total_changes = sum(r['num_changes'] for r in results.values())
    print(f"Total changes made: {total_changes}")
    
    if sample_mode:
        print("\nNOTE: Ran in SAMPLE mode. To process all sections, remove --sample flag")
    
    return results

def generate_consolidated_output(editor, results, output_dir):
    """
    Generate consolidated output files.
    
    Args:
        editor: ManualLanguageEditor instance
        results: Dictionary of editing results
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    
    # 1. Create consolidated changes file
    all_changes = []
    for section_name, result in results.items():
        changes_file = output_path / f"{section_name}_changes.csv"
        if changes_file.exists():
            try:
                df = pd.read_csv(changes_file)
                all_changes.append(df)
            except Exception as e:
                print(f"Warning: Could not read {changes_file}: {e}")
    
    if all_changes:
        consolidated_df = pd.concat(all_changes, ignore_index=True)
        consolidated_path = output_path / "All_Changes_Consolidated.csv"
        consolidated_df.to_csv(consolidated_path, index=False)
        print(f"\n✓ Created consolidated changes file: {consolidated_path.name}")
    
    # 2. Create editing statistics
    stats_data = []
    for section_name, result in results.items():
        stats_data.append({
            'Section': section_name,
            'Changes': result['num_changes'],
            'Edited_File': Path(result['edited_file']).name,
            'Changes_File': Path(result['changes_file']).name if result['changes_file'] else 'N/A',
            'Original_File': Path(result['original_file']).name
        })
    
    stats_df = pd.DataFrame(stats_data)
    stats_path = output_path / "Editing_Statistics.xlsx"
    
    with pd.ExcelWriter(stats_path, engine='openpyxl') as writer:
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Sections', 'Total Changes', 'Average Changes per Section',
                      'Max Changes', 'Min Changes', 'Date Generated'],
            'Value': [
                len(results),
                sum(r['num_changes'] for r in results.values()),
                sum(r['num_changes'] for r in results.values()) / len(results) if results else 0,
                max(r['num_changes'] for r in results.values()) if results else 0,
                min(r['num_changes'] for r in results.values()) if results else 0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"✓ Created editing statistics: {stats_path.name}")
    
    # 3. Create README for edited files
    readme_content = f"""# Edited Manuscript Files
## Tasks 4.2-4.3: Manual Language Editing

### Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
### Total Sections: {len(results)}
### Total Changes: {sum(r['num_changes'] for r in results.values())}

## File Structure

### Edited Manuscript Sections
"""
    
    for section_name, result in results.items():
        readme_content += f"- `{Path(result['edited_file']).name}`: {result['num_changes']} changes\n"
    
    readme_content += f"""
### Change Logs
- `All_Changes_Consolidated.csv`: All changes across all sections
- Individual change logs: `[section]_changes.csv`

### Statistics and Reports
- `Editing_Statistics.xlsx`: Detailed editing statistics
- `Editing_Change_Log.xlsx`: Master change log (from editor)
- `Language_Quality_Report.md`: Quality assessment report

## Editing Details

### Change Types Applied
1. **Article fixes** (a/an/the usage)
2. **Subject-verb agreement** corrections
3. **Sentence simplification** (>30 words)
4. **Active voice conversion** (passive → active)
5. **Russian translation fixes** (literal translations)
6. **Terminology consistency** (standardized terms)

### Quality Assurance
- All changes logged with original and fixed text
- Change types categorized for analysis
- Section and line numbers recorded
- Timestamps for tracking editing timeline

## Usage Instructions

### Review Edited Files
1. Open edited files (`*_edited.md`) to review changes
2. Compare with originals in `Documents/manuscript_sections/`
3. Check change logs for detailed modifications

### Analyze Changes
1. Open `Editing_Statistics.xlsx` for overview
2. Review `All_Changes_Consolidated.csv` for all changes
3. Check `Language_Quality_Report.md` for quality assessment

### Further Processing
1. These edited files are ready for Task 4.4 (Bibliography Formatting)
2. Use as input for professional editing services (Task 4.5)
3. Integrate into final manuscript compilation

## Notes

- Original files are preserved in `Documents/manuscript_sections/`
- All changes are reversible via change logs
- Technical accuracy has been maintained throughout
- Readability improvements focus on clarity without sacrificing precision

---
*Generated by Manual Language Editing System (Tasks 4.2-4.3)*
*Project: Rocket Drop Zone Analysis - OTU Pipeline*
"""
    
    readme_path = output_path / "README_Edited_Files.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ Created README file: {readme_path.name}")

def main():
    """
    Main function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate edited manuscript files for Tasks 4.2-4.3'
    )
    parser.add_argument('--output-dir', '-o', type=str, 
                       default='outputs/language_editing',
                       help='Output directory for edited files')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Use interactive editing mode')
    parser.add_argument('--sample', '-s', action='store_true',
                       help='Process only first section as sample')
    parser.add_argument('--batch', '-b', action='store_true',
                       help='Process all sections in batch mode (default)')
    
    args = parser.parse_args()
    
    # Determine mode
    interactive = args.interactive
    sample_mode = args.sample
    
    if not args.interactive and not args.batch and not args.sample:
        # Default to batch mode
        interactive = False
        sample_mode = False
    
    # Generate edited manuscripts
    results = generate_edited_manuscripts(
        output_dir=args.output_dir,
        interactive=interactive,
        sample_mode=sample_mode
    )
    
    # Export change log to Excel (via editor)
    if results:
        editor = ManualLanguageEditor(output_dir=args.output_dir)
        excel_path = editor.export_change_log_excel()
        if excel_path:
            print(f"\n✓ Master change log exported to: {excel_path}")
    
    print(f"\nAll edited files saved in: {args.output_dir}")
    print("Review README_Edited_Files.md for detailed information.")


if __name__ == "__main__":
    main()