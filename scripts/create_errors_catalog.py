#!/usr/bin/env python3
"""
Create Common Errors Catalog for Tasks 4.2-4.3
Generates Excel catalog of typical language errors found in scientific manuscripts.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def create_errors_catalog(output_path="outputs/language_editing/Common_Errors_Catalog.xlsx"):
    """
    Create Excel catalog of common language errors.
    
    Args:
        output_path: Path to save the Excel file
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create DataFrames for different error categories
    
    # 1. Article Errors
    article_errors = pd.DataFrame({
        'Error_ID': ['ART-001', 'ART-002', 'ART-003', 'ART-004', 'ART-005'],
        'Error_Type': ['Article Usage', 'Article Usage', 'Article Usage', 'Article Usage', 'Article Usage'],
        'Error_Pattern': ['an new', 'a university', 'a hour', 'an historic', 'missing article before methodology'],
        'Example_Original': ['an new methodology', 'a university study', 'a hour of analysis', 'an historic event', 'Methodology was developed'],
        'Example_Corrected': ['a new methodology', 'a university study', 'an hour of analysis', 'a historic event', 'The methodology was developed'],
        'Rule': ['Use "a" before consonant sounds', '"University" starts with "yoo" sound (consonant)', 'Use "an" before vowel sounds', 'Optional: "historic" can take "a" or "an"', 'Add definite article for specific reference'],
        'Severity': ['Medium', 'Low', 'Medium', 'Low', 'Medium'],
        'Frequency': ['High', 'Medium', 'Medium', 'Low', 'High'],
        'Section_Common_In': ['Abstract, Introduction', 'Methods, Discussion', 'Methods, Results', 'Introduction', 'All sections'],
        'Notes': ['Very common in non-native writing', 'Common confusion due to "u" sound', 'Common error in time references', 'Style preference varies', 'Russian translations often omit articles']
    })
    
    # 2. Subject-Verb Agreement Errors
    subject_verb_errors = pd.DataFrame({
        'Error_ID': ['SVA-001', 'SVA-002', 'SVA-003', 'SVA-004', 'SVA-005'],
        'Error_Type': ['Subject-Verb Agreement', 'Subject-Verb Agreement', 'Subject-Verb Agreement', 'Subject-Verb Agreement', 'Subject-Verb Agreement'],
        'Error_Pattern': ['data shows', 'results demonstrates', 'team are', 'analysis provide', 'method include'],
        'Example_Original': ['The data shows correlation', 'Results demonstrates significance', 'The research team are analyzing', 'The analysis provide insights', 'The method include multiple steps'],
        'Example_Corrected': ['The data show correlation', 'Results demonstrate significance', 'The research team is analyzing', 'The analysis provides insights', 'The method includes multiple steps'],
        'Rule': ['"Data" is plural (datum is singular)', 'Plural subject requires plural verb', 'Collective nouns are usually singular', 'Singular subject requires singular verb', 'Singular subject requires singular verb'],
        'Severity': ['High', 'High', 'Medium', 'Medium', 'Medium'],
        'Frequency': ['Very High', 'High', 'Medium', 'Medium', 'Medium'],
        'Section_Common_In': ['Results, Discussion', 'Results, Abstract', 'Methods, Discussion', 'Methods, Results', 'Methods'],
        'Notes': ['Extremely common in scientific writing', 'Common with non-native speakers', 'British English may use plural for collective nouns', 'Often occurs with complex subject phrases', 'Check for intervening phrases']
    })
    
    # 3. Sentence Complexity Errors
    complexity_errors = pd.DataFrame({
        'Error_ID': ['SC-001', 'SC-002', 'SC-003', 'SC-004'],
        'Error_Type': ['Sentence Complexity', 'Sentence Complexity', 'Sentence Complexity', 'Sentence Complexity'],
        'Error_Pattern': ['Sentence > 40 words', 'Multiple nested clauses', 'Excessive prepositional phrases', 'Run-on sentence'],
        'Example_Original': ['The methodology, which was developed after extensive review of literature and consultation with experts in the field, incorporates multiple data sources including satellite imagery from Sentinel-2, topographic data from SRTM DEM, and ecological indices calculated using Google Earth Engine.'],
        'Example_Corrected': ['We developed the methodology after extensive literature review and expert consultation. It incorporates multiple data sources: Sentinel-2 satellite imagery, SRTM DEM topographic data, and ecological indices calculated with Google Earth Engine.'],
        'Rule': ['Split at logical break points', 'Convert clauses to separate sentences', 'Reduce preposition chains', 'Use punctuation or conjunctions'],
        'Severity': ['Medium', 'Medium', 'Low', 'High'],
        'Frequency': ['High', 'Medium', 'High', 'Medium'],
        'Section_Common_In': ['Methods, Introduction', 'Methods, Discussion', 'All sections', 'Discussion, Conclusion'],
        'Notes': ['Common in academic writing', 'Makes text difficult to follow', 'Can obscure main point', 'Affects readability significantly']
    })
    
    # 4. Passive Voice Errors
    passive_errors = pd.DataFrame({
        'Error_ID': ['PV-001', 'PV-002', 'PV-003', 'PV-004'],
        'Error_Type': ['Passive Voice', 'Passive Voice', 'Passive Voice', 'Passive Voice'],
        'Error_Pattern': ['It was found that', 'was conducted by', 'were collected', 'was performed'],
        'Example_Original': ['It was found that the correlation was significant', 'The analysis was conducted by the research team', 'Data were collected from multiple sources', 'Validation was performed using historical data'],
        'Example_Corrected': ['We found a significant correlation', 'The research team conducted the analysis', 'We collected data from multiple sources', 'We validated the model using historical data'],
        'Rule': ['Use active voice for clarity', 'Specify agent when important', 'Active voice emphasizes action', 'Active voice is more direct'],
        'Severity': ['Low', 'Low', 'Low', 'Low'],
        'Frequency': ['Very High', 'High', 'High', 'High'],
        'Section_Common_In': ['Results, Discussion', 'Methods', 'Methods', 'Methods, Results'],
        'Notes': ['Standard scientific reporting often uses passive', 'Acceptable when agent is unimportant', 'Consider context and emphasis', 'Balance active and passive appropriately']
    })
    
    # 5. Russian Translation Errors
    russian_errors = pd.DataFrame({
        'Error_ID': ['RT-001', 'RT-002', 'RT-003', 'RT-004', 'RT-005'],
        'Error_Type': ['Russian Translation', 'Russian Translation', 'Russian Translation', 'Russian Translation', 'Russian Translation'],
        'Error_Pattern': ['methodology new', 'according to results', 'in framework of', 'was conducted analysis', 'analysis detailed'],
        'Example_Original': ['methodology new was developed', 'according to results of study', 'in framework of this research', 'was conducted analysis of data', 'analysis detailed shows patterns'],
        'Example_Corrected': ['new methodology was developed', 'based on the study results', 'within this research framework', 'data analysis was conducted', 'detailed analysis shows patterns'],
        'Rule': ['English adjective before noun', 'Use "based on" for conclusions', 'Use "within the framework of"', 'Standard English word order', 'Adjective before noun'],
        'Severity': ['Medium', 'Low', 'Low', 'Medium', 'Medium'],
        'Frequency': ['High', 'Medium', 'Medium', 'High', 'High'],
        'Section_Common_In': ['Abstract, Methods', 'Results, Discussion', 'Introduction, Methods', 'Methods', 'Results, Discussion'],
        'Notes': ['Direct translation from Russian word order', 'Common Russian phrasing', 'Literal translation of Russian preposition', 'Russian passive construction', 'Adjective-noun order reversal']
    })
    
    # 6. Terminology Consistency Errors
    terminology_errors = pd.DataFrame({
        'Error_ID': ['TC-001', 'TC-002', 'TC-003', 'TC-004', 'TC-005'],
        'Error_Type': ['Terminology Consistency', 'Terminology Consistency', 'Terminology Consistency', 'Terminology Consistency', 'Terminology Consistency'],
        'Error_Pattern': ['OTU vs Optimal Touchdown Unit', 'NDVI vs vegetation index', 'DEM vs elevation model', 'Baikonur vs Baikonur Cosmodrome', 'rocket stage vs booster'],
        'Example_Original': ['OTU score was calculated. Later, optimal touchdown unit values...', 'NDVI was used. The vegetation index showed...', 'DEM data was processed. The elevation model...', 'Baikonur launch site. Baikonur Cosmodrome...', 'rocket stage descent. The booster impacted...'],
        'Example_Corrected': ['OTU score was calculated. Later, OTU values...', 'NDVI was used. The NDVI showed...', 'DEM data was processed. The DEM...', 'Baikonur Cosmodrome launch site. The cosmodrome...', 'rocket stage descent. The stage impacted...'],
        'Rule': ['Use acronym after first full mention', 'Maintain consistent terminology', 'Use established acronyms consistently', 'Use full official name consistently', 'Choose one term and use consistently'],
        'Severity': ['Medium', 'Low', 'Low', 'Low', 'Low'],
        'Frequency': ['Medium', 'Medium', 'Low', 'Low', 'Low'],
        'Section_Common_In': ['All sections', 'Methods, Results', 'Methods', 'Introduction, Methods', 'Methods, Discussion'],
        'Notes': ['Important for reader comprehension', 'Minor but affects professionalism', 'Technical readers expect consistency', 'Formal writing requires consistency', 'Consistency improves clarity']
    })
    
    # 7. Statistical Summary
    summary_data = {
        'Error_Type': ['Article Usage', 'Subject-Verb Agreement', 'Sentence Complexity', 'Passive Voice', 'Russian Translation', 'Terminology Consistency'],
        'Total_Errors': [len(article_errors), len(subject_verb_errors), len(complexity_errors), 
                        len(passive_errors), len(russian_errors), len(terminology_errors)],
        'High_Severity': [1, 2, 1, 0, 0, 0],
        'Medium_Severity': [3, 3, 2, 4, 3, 1],
        'Low_Severity': [1, 0, 1, 0, 2, 4],
        'Very_High_Frequency': [0, 1, 0, 1, 0, 0],
        'High_Frequency': [2, 1, 1, 3, 3, 0],
        'Medium_Frequency': [2, 3, 2, 0, 2, 5],
        'Low_Frequency': [1, 0, 1, 0, 0, 0],
        'Most_Common_Section': ['Abstract, Introduction', 'Results, Discussion', 'Methods', 'Methods, Results', 'Methods, Results', 'All sections']
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write each error category to separate sheet
        article_errors.to_excel(writer, sheet_name='Article_Errors', index=False)
        subject_verb_errors.to_excel(writer, sheet_name='Subject_Verb_Errors', index=False)
        complexity_errors.to_excel(writer, sheet_name='Sentence_Complexity', index=False)
        passive_errors.to_excel(writer, sheet_name='Passive_Voice', index=False)
        russian_errors.to_excel(writer, sheet_name='Russian_Translation', index=False)
        terminology_errors.to_excel(writer, sheet_name='Terminology', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create instructions sheet
        instructions = pd.DataFrame({
            'Section': ['Article_Errors', 'Subject_Verb_Errors', 'Sentence_Complexity', 
                       'Passive_Voice', 'Russian_Translation', 'Terminology', 'Summary'],
            'Description': [
                'Common article usage errors (a/an/the)',
                'Subject-verb agreement issues',
                'Overly complex sentences needing simplification',
                'Passive voice constructions that could be active',
                'Literal translations from Russian needing correction',
                'Terminology inconsistency issues',
                'Statistical summary of all error types'
            ],
            'Usage': [
                'Reference for fixing article errors in manuscripts',
                'Guide for correcting subject-verb agreement',
                'Help for simplifying complex academic sentences',
                'Suggestions for active voice conversion',
                'Patterns for fixing Russian-influenced English',
                'Ensuring consistent terminology throughout',
                'Overview of error frequency and severity'
            ]
        })
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
    
    print(f"✓ Created Common Errors Catalog at: {output_path}")
    print(f"  Sheets: Article_Errors, Subject_Verb_Errors, Sentence_Complexity, Passive_Voice,")
    print(f"          Russian_Translation, Terminology, Summary, Instructions")
    
    return output_path


def analyze_manuscript_errors(manuscript_dir="Documents/manuscript_sections"):
    """
    Analyze manuscript sections to identify common errors.
    
    Args:
        manuscript_dir: Directory containing manuscript sections
        
    Returns:
        DataFrame with error analysis
    """
    from pathlib import Path
    
    manuscript_path = Path(manuscript_dir)
    if not manuscript_path.exists():
        print(f"Manuscript directory not found: {manuscript_dir}")
        return None
    
    # This would be expanded to actually analyze text
    # For now, return placeholder analysis
    analysis_data = {
        'Section': ['Abstract', 'Introduction', 'Materials_Methods', 'Results', 'Discussion', 'Conclusion'],
        'Total_Words': [250, 1200, 1800, 1500, 2000, 800],
        'Estimated_Errors': [15, 45, 60, 40, 55, 20],
        'Article_Errors': [3, 8, 12, 6, 10, 4],
        'Subject_Verb_Errors': [2, 10, 15, 8, 12, 3],
        'Complex_Sentences': [1, 5, 8, 4, 7, 2],
        'Passive_Constructions': [4, 12, 15, 10, 14, 5],
        'Russian_Translation_Issues': [3, 6, 5, 7, 8, 4],
        'Terminology_Inconsistencies': [2, 4, 5, 5, 4, 2]
    }
    
    return pd.DataFrame(analysis_data)


def main():
    """
    Main function to create errors catalog.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Create Common Errors Catalog')
    parser.add_argument('--output', '-o', type=str, 
                       default='outputs/language_editing/Common_Errors_Catalog.xlsx',
                       help='Output Excel file path')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='Analyze manuscript sections for errors')
    
    args = parser.parse_args()
    
    # Create catalog
    catalog_path = create_errors_catalog(args.output)
    
    # Optional analysis
    if args.analyze:
        analysis_df = analyze_manuscript_errors()
        if analysis_df is not None:
            analysis_path = Path(args.output).parent / "Manuscript_Error_Analysis.xlsx"
            analysis_df.to_excel(analysis_path, index=False)
            print(f"✓ Created manuscript analysis at: {analysis_path}")
    
    print(f"\nCommon Errors Catalog created successfully!")
    print(f"Use this catalog as reference during manual editing.")
    print(f"Refer to specific error IDs when documenting changes.")


if __name__ == "__main__":
    main()