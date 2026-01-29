#!/usr/bin/env python3
"""
Quick test to generate bibliography output files.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the requests.get function to avoid actual API calls
import requests
from unittest.mock import Mock, patch

# Create mock response for Crossref API
def create_mock_response(doi):
    """Create a mock response for a given DOI."""
    mock_response = Mock()
    
    # Sample metadata for known DOIs
    sample_metadata = {
        "10.1016/j.jaero.2020.04.015": {
            "status": "ok",
            "message": {
                "author": [
                    {"family": "Smith", "given": "John"},
                    {"family": "Johnson", "given": "Alice"},
                    {"family": "Brown", "given": "Robert"}
                ],
                "title": ["Environmental Impact Assessment of Rocket Stage Drop Zones in Central Asia"],
                "container-title": ["Journal of Aerospace Engineering"],
                "published": {"date-parts": [[2020, 4, 15]]},
                "volume": "33",
                "issue": "4",
                "page": "123-145",
                "DOI": "10.1016/j.jaero.2020.04.015"
            }
        },
        "10.1016/j.rse.2021.112345": {
            "status": "ok",
            "message": {
                "author": [
                    {"family": "Chen", "given": "Wei"},
                    {"family": "Li", "given": "Ming"},
                    {"family": "Wang", "given": "Hong"}
                ],
                "title": ["Remote Sensing Monitoring of Vegetation Recovery in Impact Zones Using Sentinel-2"],
                "container-title": ["Remote Sensing of Environment"],
                "published": {"date-parts": [[2021, 6, 1]]},
                "volume": "256",
                "page": "112345",
                "DOI": "10.1016/j.rse.2021.112345"
            }
        }
    }
    
    if doi in sample_metadata:
        mock_response.status_code = 200
        mock_response.json.return_value = sample_metadata[doi]
    else:
        mock_response.status_code = 404
    
    return mock_response

# Patch requests.get before importing format_bibliography
with patch('requests.get', side_effect=create_mock_response):
    from format_bibliography import process_bibliography
    
    print("Running bibliography formatting with mock API...")
    print("=" * 60)
    
    # Process the test bibliography
    results = process_bibliography('data/bibliography/test_references.bib')
    
    print("\nProcessing Results:")
    print(f"Total entries: {results['total_entries']}")
    print(f"Entries with DOI: {results['entries_with_doi']}")
    print(f"Successfully formatted: {results['successfully_formatted']}")
    print(f"Failed fetch: {results['failed_fetch']}")
    print(f"Failed format: {results['failed_format']}")
    
    print("\nGenerated files in outputs/bibliography/:")
    import glob
    files = glob.glob('outputs/bibliography/*')
    for f in files:
        print(f"  - {os.path.basename(f)}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")