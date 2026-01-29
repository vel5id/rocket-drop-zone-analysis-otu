#!/usr/bin/env python3
"""
Test script for bibliography formatting (offline mode).
Uses mock data instead of real Crossref API calls.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from format_bibliography import (
    format_author_name,
    format_authors_list,
    format_reference_mdpi,
    validate_doi,
    generate_output_files
)
import pandas as pd
from pathlib import Path
from datetime import datetime

def test_functions():
    """Test individual functions."""
    print("Testing bibliography formatting functions...")
    
    # Test validate_doi
    assert validate_doi("10.1016/j.jaero.2020.04.015") == True
    assert validate_doi("10.1234/invalid") == False
    assert validate_doi("") == False
    
    # Test format_author_name
    author = {"family": "Smith", "given": "John"}
    assert format_author_name(author) == "Smith, J."
    
    author2 = {"family": "Johnson", "given": "Alice B."}
    assert format_author_name(author2) == "Johnson, A.B."
    
    # Test format_authors_list
    authors = [
        {"family": "Smith", "given": "John"},
        {"family": "Johnson", "given": "Alice"}
    ]
    assert format_authors_list(authors) == "Smith, J.; Johnson, A."
    
    print("✓ All function tests passed!")

def create_mock_results():
    """Create mock processing results for testing output generation."""
    # Create output directory
    output_dir = Path('outputs/bibliography')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock results
    results = {
        'total_entries': 10,
        'entries_with_doi': 8,
        'successfully_formatted': 6,
        'failed_fetch': 1,
        'failed_format': 1,
        'formatted_references': [
            {
                'original_id': 'smith2020rocket',
                'doi': '10.1016/j.jaero.2020.04.015',
                'formatted_reference': 'Smith, J.; Johnson, A.; Brown, R. Environmental Impact Assessment of Rocket Stage Drop Zones in Central Asia. Journal of Aerospace Engineering 2020, Volume 33, Pages 123-145. doi:10.1016/j.jaero.2020.04.015',
                'metadata': {
                    'title': 'Environmental Impact Assessment of Rocket Stage Drop Zones in Central Asia',
                    'authors': 3,
                    'year': 2020,
                    'journal': 'Journal of Aerospace Engineering'
                }
            },
            {
                'original_id': 'chen2021remote',
                'doi': '10.1016/j.rse.2021.112345',
                'formatted_reference': 'Chen, W.; Li, M.; Wang, H. Remote Sensing Monitoring of Vegetation Recovery in Impact Zones Using Sentinel-2. Remote Sensing of Environment 2021, Volume 256, Pages 112345. doi:10.1016/j.rse.2021.112345',
                'metadata': {
                    'title': 'Remote Sensing Monitoring of Vegetation Recovery in Impact Zones Using Sentinel-2',
                    'authors': 3,
                    'year': 2021,
                    'journal': 'Remote Sensing of Environment'
                }
            }
        ],
        'missing_metadata': [
            {
                'Entry ID': 'test_no_doi',
                'DOI': '',
                'Missing Fields': 'No DOI provided',
                'Available Fields': ['author', 'title', 'journal', 'year']
            },
            {
                'Entry ID': 'test_invalid_doi',
                'DOI': '10.9999/invalid.2022.999999',
                'Missing Fields': 'Metadata fetch failed',
                'Available Fields': []
            }
        ],
        'validation_report': [
            {
                'Entry ID': 'smith2020rocket',
                'DOI': '10.1016/j.jaero.2020.04.015',
                'Valid Format': True,
                'Has Metadata': True,
                'Formatted': True,
                'Error': ''
            },
            {
                'Entry ID': 'chen2021remote',
                'DOI': '10.1016/j.rse.2021.112345',
                'Valid Format': True,
                'Has Metadata': True,
                'Formatted': True,
                'Error': ''
            },
            {
                'Entry ID': 'test_invalid_doi',
                'DOI': '10.9999/invalid.2022.999999',
                'Valid Format': True,
                'Has Metadata': False,
                'Formatted': False,
                'Error': 'Metadata fetch failed'
            }
        ]
    }
    
    return results, output_dir

def main():
    """Run tests and generate sample output files."""
    print("=" * 60)
    print("Testing Bibliography Formatting Script")
    print("=" * 60)
    
    # Test functions
    test_functions()
    
    # Create mock results
    print("\nGenerating mock output files...")
    results, output_dir = create_mock_results()
    
    # Generate output files
    generate_output_files(results, output_dir)
    
    # Verify files were created
    files = [
        'formatted_references.bib',
        'Missing_Metadata_Report.xlsx', 
        'DOI_Validation_Report.txt',
        'Bibliography_Formatting_Summary.md'
    ]
    
    for file in files:
        file_path = output_dir / file
        if file_path.exists():
            print(f"✓ Created: {file_path}")
            if file == 'DOI_Validation_Report.txt':
                # Show preview
                with open(file_path, 'r') as f:
                    content = f.read(500)
                    print(f"  Preview:\n{content[:200]}...")
        else:
            print(f"✗ Missing: {file_path}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print(f"Output directory: {output_dir.absolute()}")
    print("=" * 60)

if __name__ == '__main__':
    main()