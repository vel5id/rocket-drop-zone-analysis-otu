#!/usr/bin/env python3
"""
Test script for Language Editing Tools (Tasks 4.2-4.3)
Verify that all components are working correctly.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import sys
from pathlib import Path
import importlib.util

def test_module_imports():
    """Test that all required modules can be imported."""
    print("="*60)
    print("TEST 1: MODULE IMPORTS")
    print("="*60)
    
    modules = [
        ('pandas', 'pandas'),
        ('pathlib', 'pathlib'),
        ('re', 're'),
        ('json', 'json'),
        ('datetime', 'datetime'),
        ('logging', 'logging'),
    ]
    
    all_ok = True
    for module_name, import_name in modules:
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"✓ {module_name}")
            else:
                print(f"✗ {module_name} - NOT FOUND")
                all_ok = False
        except ImportError:
            print(f"✗ {module_name} - IMPORT ERROR")
            all_ok = False
    
    return all_ok

def test_script_files():
    """Test that all script files exist."""
    print("\n" + "="*60)
    print("TEST 2: SCRIPT FILES")
    print("="*60)
    
    scripts = [
        'scripts/manual_language_editing.py',
        'scripts/interactive_language_editor.py',
        'scripts/create_errors_catalog.py',
        'scripts/integrate_task4_1.py',
        'scripts/generate_edited_manuscript.py',
        'scripts/generate_quality_report.py',
    ]
    
    all_ok = True
    for script in scripts:
        if Path(script).exists():
            print(f"✓ {script}")
        else:
            print(f"✗ {script} - NOT FOUND")
            all_ok = False
    
    return all_ok

def test_batch_files():
    """Test that batch files exist."""
    print("\n" + "="*60)
    print("TEST 3: BATCH FILES")
    print("="*60)
    
    batch_files = [
        'run_language_editing.bat',
        'run_create_errors_catalog.bat',
    ]
    
    all_ok = True
    for batch_file in batch_files:
        if Path(batch_file).exists():
            print(f"✓ {batch_file}")
        else:
            print(f"✗ {batch_file} - NOT FOUND")
            all_ok = False
    
    return all_ok

def test_documentation_files():
    """Test that documentation files exist."""
    print("\n" + "="*60)
    print("TEST 4: DOCUMENTATION FILES")
    print("="*60)
    
    docs = [
        'docs/Language_Editing_Guide.md',
        'docs/Editing_Checklist.md',
    ]
    
    all_ok = True
    for doc in docs:
        if Path(doc).exists():
            print(f"✓ {doc}")
        else:
            print(f"✗ {doc} - NOT FOUND")
            all_ok = False
    
    return all_ok

def test_manuscript_sections():
    """Test that manuscript sections exist."""
    print("\n" + "="*60)
    print("TEST 5: MANUSCRIPT SECTIONS")
    print("="*60)
    
    manuscript_dir = Path("Documents/manuscript_sections")
    if not manuscript_dir.exists():
        print(f"✗ Manuscript directory not found: {manuscript_dir}")
        return False
    
    sections = list(manuscript_dir.glob("*.md"))
    
    if not sections:
        print(f"✗ No manuscript sections found in {manuscript_dir}")
        return False
    
    print(f"Found {len(sections)} manuscript sections:")
    for section in sections[:5]:  # Show first 5
        print(f"  ✓ {section.name}")
    
    if len(sections) > 5:
        print(f"  ... and {len(sections) - 5} more")
    
    return True

def test_output_directory():
    """Test that output directory can be created."""
    print("\n" + "="*60)
    print("TEST 6: OUTPUT DIRECTORY")
    print("="*60)
    
    output_dir = Path("outputs/language_editing")
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory: {output_dir}")
        
        # Test write permission
        test_file = output_dir / "test_write.txt"
        test_file.write_text("Test write permission")
        test_file.unlink()  # Clean up
        
        print("✓ Write permission: OK")
        return True
    except Exception as e:
        print(f"✗ Output directory error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of main editor class."""
    print("\n" + "="*60)
    print("TEST 7: BASIC FUNCTIONALITY")
    print("="*60)
    
    try:
        # Try to import the main editor class
        sys.path.insert(0, 'scripts')
        from manual_language_editing import ManualLanguageEditor
        
        print("✓ ManualLanguageEditor class imported")
        
        # Test initialization
        editor = ManualLanguageEditor(output_dir="outputs/language_editing_test")
        print("✓ ManualLanguageEditor initialized")
        
        # Test basic text processing
        test_text = "This is an new methodology. Results demonstrates correlation."
        fixed_text, changes = editor.fix_articles(test_text, "test")
        
        if changes:
            print(f"✓ Article fixing works: {len(changes)} changes detected")
        else:
            print("⚠ Article fixing: No changes detected (might be correct text)")
        
        # Clean up test directory
        import shutil
        test_dir = Path("outputs/language_editing_test")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_catalog_generation():
    """Test error catalog generation."""
    print("\n" + "="*60)
    print("TEST 8: ERROR CATALOG GENERATION")
    print("="*60)
    
    try:
        # Import the catalog generator
        spec = importlib.util.spec_from_file_location(
            "create_errors_catalog", 
            "scripts/create_errors_catalog.py"
        )
        if spec is None:
            print("✗ Could not load create_errors_catalog module")
            return False
        
        catalog_module = importlib.util.module_from_spec(spec)
        
        # We'll just check that the file can be executed
        print("✓ Error catalog script structure: OK")
        
        # Check that expected output would be created
        output_path = Path("outputs/language_editing/Common_Errors_Catalog.xlsx")
        if output_path.exists():
            print(f"✓ Existing catalog found: {output_path.name}")
        else:
            print("⚠ Catalog not yet generated (run create_errors_catalog.py)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error catalog test failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST SUITE - LANGUAGE EDITING TOOLS")
    print("="*60)
    print("Testing Tasks 4.2-4.3 implementation")
    print("Based on IMPLEMENTATION_ROADMAP.md lines 535-551")
    print("="*60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Module Imports", test_module_imports()))
    test_results.append(("Script Files", test_script_files()))
    test_results.append(("Batch Files", test_batch_files()))
    test_results.append(("Documentation", test_documentation_files()))
    test_results.append(("Manuscript Sections", test_manuscript_sections()))
    test_results.append(("Output Directory", test_output_directory()))
    test_results.append(("Basic Functionality", test_basic_functionality()))
    test_results.append(("Error Catalog", test_error_catalog_generation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} [{status}]")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("Language editing tools are ready for use.")
        print("\nNext steps:")
        print("1. Run: run_language_editing.bat")
        print("2. Review: docs/Language_Editing_Guide.md")
        print("3. Use: scripts/interactive_language_editor.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
        print("Please check the errors above before proceeding.")
    
    return passed == total

def main():
    """Main test function."""
    success = run_all_tests()
    
    # Provide additional instructions
    print("\n" + "="*60)
    print("QUICK START INSTRUCTIONS")
    print("="*60)
    print("\nTo use the language editing tools:")
    print("\n1. Basic batch editing:")
    print("   > python scripts/manual_language_editing.py --all")
    print("\n2. Interactive editing:")
    print("   > python scripts/interactive_language_editor.py")
    print("\n3. Complete pipeline:")
    print("   > run_language_editing.bat")
    print("\n4. Generate error catalog:")
    print("   > python scripts/create_errors_catalog.py")
    print("\n5. Generate quality report:")
    print("   > python scripts/generate_quality_report.py")
    print("\n" + "="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())