#!/usr/bin/env python3
"""
Quick test script for comparative cost analysis.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.comparative_cost_analysis import main

if __name__ == "__main__":
    print("Testing comparative cost analysis...")
    main()