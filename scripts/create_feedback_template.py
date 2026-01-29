#!/usr/bin/env python3
"""
Create Editor Feedback Template Excel file for MDPI Language Service.
Task 4.5: Professional Editing Service
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

def create_editor_feedback_template():
    """Create Excel template for editor feedback."""
    
    # Create DataFrames for different sheets
    print("Creating Editor Feedback Template...")
    
    # Sheet 1: General Assessment
    general_assessment = pd.DataFrame({
        'Assessment_Category': [
            'Overall Language Quality',
            'Clarity of Expression',
            'Technical Accuracy',
            'Logical Flow',
            'Adherence to MDPI Style',
            'Reference Formatting',
            'Figure/Tabel Quality',
            'Overall Recommendation'
        ],
        'Rating (1-10)': ['' for _ in range(8)],
        'Comments': ['' for _ in range(8)],
        'Priority': ['' for _ in range(8)]
    })
    
    # Sheet 2: Specific Issues
    specific_issues = pd.DataFrame({
        'Page_Number': [''] * 20,
        'Line_Number': [''] * 20,
        'Issue_Type': [''] * 20,
        'Original_Text': [''] * 20,
        'Suggested_Correction': [''] * 20,
        'Explanation': [''] * 20,
        'Priority': [''] * 20,
        'Status': ['Pending'] * 20
    })
    
    # Sheet 3: Grammar & Style
    grammar_style = pd.DataFrame({
        'Issue_Category': [
            'Article Usage (a/an/the)',
            'Subject-Verb Agreement',
            'Tense Consistency',
            'Preposition Usage',
            'Sentence Structure',
            'Passive Voice Overuse',
            'Word Choice',
            'Punctuation',
            'Capitalization',
            'Acronym Usage'
        ],
        'Count': [0] * 10,
        'Examples': [''] * 10,
        'Recommendations': [''] * 10
    })
    
    # Sheet 4: Terminology & Consistency
    terminology = pd.DataFrame({
        'Term': ['OTU', 'NDVI', 'SRTM', 'DEM', 'IAS', 'Protodyakonov', 'Bonitet'] + [''] * 13,
        'First_Definition_Page': [''] * 20,
        'Consistency_Check': [''] * 20,
        'Suggested_Improvements': [''] * 20,
        'Notes': [''] * 20
    })
    
    # Sheet 5: Action Items
    action_items = pd.DataFrame({
        'Action_ID': [f'ACT{i:03d}' for i in range(1, 21)],
        'Description': [''] * 20,
        'Priority': [''] * 20,
        'Assigned_To': [''] * 20,
        'Due_Date': [''] * 20,
        'Status': ['Pending'] * 20,
        'Notes': [''] * 20
    })
    
    # Sheet 6: Summary & Recommendations
    summary = pd.DataFrame({
        'Section': [
            'Executive Summary',
            'Major Strengths',
            'Key Areas for Improvement',
            'Estimated Revision Time',
            'Next Steps',
            'Editor Contact'
        ],
        'Content': [
            'Overall assessment of the manuscript...',
            '1. Strong technical content\n2. Good methodology description\n3. Clear figures',
            '1. Language polishing needed\n2. Sentence structure improvement\n3. Reference formatting',
            '3-5 business days',
            '1. Address high-priority issues\n2. Review all suggestions\n3. Submit revised version',
            'Editor: [Name]\nEmail: [editor@mdpi.com]\nPhone: [Optional]'
        ]
    })
    
    # Create Excel writer
    output_path = Path('Editor_Feedback_Template.xlsx')
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write sheets
        general_assessment.to_excel(writer, sheet_name='General_Assessment', index=False)
        specific_issues.to_excel(writer, sheet_name='Specific_Issues', index=False)
        grammar_style.to_excel(writer, sheet_name='Grammar_Style', index=False)
        terminology.to_excel(writer, sheet_name='Terminology', index=False)
        action_items.to_excel(writer, sheet_name='Action_Items', index=False)
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and worksheet objects for formatting
        workbook = writer.book
        worksheet = writer.sheets['General_Assessment']
        
        # Add header information
        worksheet['A1'] = 'MDPI Language Editing Service - Editor Feedback Template'
        worksheet['A2'] = f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        worksheet['A3'] = 'Project: Rocket Drop Zone Analysis - OTU Pipeline'
        worksheet['A4'] = 'Task 4.5: Professional Editing Service'
    
    print(f"Template created: {output_path}")
    print("\nSheet Structure:")
    print("1. General_Assessment - Overall ratings and comments")
    print("2. Specific_Issues - Line-by-line issues")
    print("3. Grammar_Style - Grammar and style improvements")
    print("4. Terminology - Technical term consistency")
    print("5. Action_Items - Actionable items for revision")
    print("6. Summary - Executive summary and recommendations")
    
    return output_path

def create_sample_feedback():
    """Create a sample filled feedback template for demonstration."""
    
    print("\nCreating Sample Feedback Report...")
    
    # Sample data for demonstration
    sample_general = pd.DataFrame({
        'Assessment_Category': [
            'Overall Language Quality',
            'Clarity of Expression',
            'Technical Accuracy',
            'Logical Flow',
            'Adherence to MDPI Style',
            'Reference Formatting',
            'Figure/Table Quality',
            'Overall Recommendation'
        ],
        'Rating (1-10)': [7, 6, 9, 7, 6, 5, 8, 7],
        'Comments': [
            'Good technical content but needs language polishing',
            'Some sentences are too complex and could be simplified',
            'Excellent technical accuracy and methodology',
            'Logical flow is generally good but could be improved in discussion',
            'Needs adjustment to MDPI Aerospace style',
            'References need formatting according to MDPI guidelines',
            'Figures are clear and well-prepared',
            'Accept with minor revisions'
        ],
        'Priority': ['High', 'High', 'Low', 'Medium', 'Medium', 'High', 'Low', 'N/A']
    })
    
    sample_issues = pd.DataFrame({
        'Page_Number': [1, 1, 2, 3, 3, 4, 5, ''] * 2,
        'Line_Number': [15, 22, 8, 12, 18, 5, 9, ''] * 2,
        'Issue_Type': [
            'Grammar', 'Style', 'Clarity', 'Terminology', 'Formatting',
            'Grammar', 'Style', ''
        ] * 2,
        'Original_Text': [
            'a impact zone', 'was calculated', 'the method that was used',
            'OTU vs Operational Terrain Unit', 'Reference [1] format',
            'there is many factors', 'it can be seen that', ''
        ] * 2,
        'Suggested_Correction': [
            'an impact zone', 'we calculated', 'our method',
            'Use OTU consistently', 'Update to MDPI format',
            'there are many factors', 'The results show that', ''
        ] * 2,
        'Explanation': [
            'Article usage', 'Active voice preferred', 'Simplify phrasing',
            'Inconsistent acronym usage', 'MDPI style required',
            'Subject-verb agreement', 'More direct phrasing', ''
        ] * 2,
        'Priority': ['High', 'Medium', 'High', 'Medium', 'High', 'High', 'Medium', ''] * 2,
        'Status': ['Pending'] * 16
    })
    
    output_path = Path('outputs/professional_editing/Editor_Feedback_Sample.xlsx')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        sample_general.to_excel(writer, sheet_name='General_Assessment', index=False)
        sample_issues.to_excel(writer, sheet_name='Specific_Issues', index=False)
    
    print(f"Sample feedback created: {output_path}")
    return output_path

if __name__ == '__main__':
    # Create template
    template_path = create_editor_feedback_template()
    
    # Create sample in outputs directory
    sample_path = create_sample_feedback()
    
    print(f"\nFiles created:")
    print(f"1. Template: {template_path}")
    print(f"2. Sample: {sample_path}")
    print("\nInstructions:")
    print("1. Use the template to collect editor feedback")
    print("2. The sample shows how feedback should be structured")
    print("3. Integrate with professional_editing_service.py for processing")