#!/usr/bin/env python3
"""
OTU Database Check Script.
"""
import sqlite3
import json
from pathlib import Path
import sys

def check_database(db_path: str):
    """Check database structure and content."""
    print(f"Checking database: {db_path}")
    
    if not Path(db_path).exists():
        print(f"  [ERROR] File does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"  [OK] Connection successful")
        print(f"  Tables in database:")
        
        for table in tables:
            table_name = table[0]
            print(f"    - {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"      Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"        {col_name} ({col_type})")
            
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"      Records: {count}")
            
            # Show sample records
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample = cursor.fetchall()
                print(f"      Sample records:")
                for i, row in enumerate(sample):
                    print(f"        {i+1}: {row}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  [ERROR] Database check error: {e}")
        return False

def main():
    """Main check function."""
    print("=" * 60)
    print("OTU DATABASE FUNCTIONALITY CHECK")
    print("=" * 60)
    
    # Check main database
    main_db = "output/otu_cache.db"
    print(f"\n1. Main OTU database:")
    main_ok = check_database(main_db)
    
    # Check test database
    test_db = "output/test_cache.db"
    print(f"\n2. Test database:")
    test_ok = check_database(test_db)
    
    # Check files in output directory
    print(f"\n3. Files in output directory:")
    output_dir = Path("output")
    if output_dir.exists():
        for file in output_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"    {file.name}: {size_mb:.2f} MB")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("SUMMARY:")
    if main_ok and test_ok:
        print("  [SUCCESS] Databases are working correctly")
    else:
        print("  [WARNING] There are issues with databases")
    
    return main_ok and test_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)