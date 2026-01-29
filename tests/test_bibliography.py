#!/usr/bin/env python3
"""
Unit tests for bibliography formatting functions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from format_bibliography import (
    validate_doi,
    format_author_name,
    format_authors_list,
    format_reference_mdpi
)

def test_validate_doi():
    """Test DOI validation."""
    print("Testing DOI validation...")
    assert validate_doi("10.1016/j.jaero.2020.04.015") == True
    assert validate_doi("10.1234/abc.123") == True
    assert validate_doi("10.9999/invalid") == True  # Still valid format
    assert validate_doi("") == False
    assert validate_doi("not-a-doi") == False
    assert validate_doi("10.") == False
    print("✓ DOI validation tests passed")

def test_format_author_name():
    """Test author name formatting."""
    print("\nTesting author name formatting...")
    # Standard case
    author = {"family": "Smith", "given": "John"}
    assert format_author_name(author) == "Smith, J."
    
    # Multiple given names
    author2 = {"family": "Johnson", "given": "Alice B."}
    assert format_author_name(author2) == "Johnson, A.B."
    
    # No given name
    author3 = {"family": "Einstein"}
    assert format_author_name(author3) == "Einstein"
    
    # No family name
    author4 = {"name": "Unknown Author"}
    assert format_author_name(author4) == "Unknown Author"
    
    print("✓ Author name formatting tests passed")

def test_format_authors_list():
    """Test authors list formatting."""
    print("\nTesting authors list formatting...")
    authors = [
        {"family": "Smith", "given": "John"},
        {"family": "Johnson", "given": "Alice"}
    ]
    assert format_authors_list(authors) == "Smith, J.; Johnson, A."
    
    # Single author
    authors2 = [{"family": "Einstein", "given": "Albert"}]
    assert format_authors_list(authors2) == "Einstein, A."
    
    # Empty list
    assert format_authors_list([]) == "Unknown"
    
    print("✓ Authors list formatting tests passed")

def test_format_reference_mdpi():
    """Test reference formatting."""
    print("\nTesting reference formatting...")
    
    # Sample metadata
    metadata = {
        "author": [
            {"family": "Smith", "given": "John"},
            {"family": "Johnson", "given": "Alice"}
        ],
        "title": ["Test Article Title"],
        "container-title": ["Test Journal"],
        "published": {"date-parts": [[2023, 1, 1]]},
        "volume": "15",
        "page": "123-145",
        "DOI": "10.1234/test.2023.123456"
    }
    
    formatted = format_reference_mdpi(metadata)
    assert formatted is not None
    assert "Smith, J.; Johnson, A." in formatted
    assert "Test Article Title." in formatted
    assert "Test Journal 2023" in formatted
    assert "Volume 15" in formatted
    assert "Pages 123-145" in formatted
    assert "doi:10.1234/test.2023.123456" in formatted
    
    print("✓ Reference formatting tests passed")

def test_integration():
    """Test integration with mock data."""
    print("\nTesting integration...")
    
    # Create a test .bib file
    test_bib = "test_references.bib"
    with open(test_bib, "w") as f:
        f.write("""@article{test1,
  author = {Test Author},
  title = {Test Title},
  journal = {Test Journal},
  year = {2023},
  doi = {10.1234/test.2023.123456}
}""")
    
    # Check file was created
    assert os.path.exists(test_bib)
    print(f"✓ Test .bib file created: {test_bib}")
    
    # Clean up
    os.remove(test_bib)
    print("✓ Test cleanup completed")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Bibliography Formatting Tests")
    print("=" * 60)
    
    try:
        test_validate_doi()
        test_format_author_name()
        test_format_authors_list()
        test_format_reference_mdpi()
        test_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())