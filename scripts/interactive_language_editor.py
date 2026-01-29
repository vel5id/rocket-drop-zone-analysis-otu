#!/usr/bin/env python3
"""
Interactive Language Editor for Tasks 4.2-4.3
Based on IMPLEMENTATION_ROADMAP.md lines 535-551

Interactive tool for step-by-step manual editing of manuscript sections
with highlighting of problematic areas, suggestions for fixes,
and accept/reject functionality for edits.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import sys
import os
from pathlib import Path
from manual_language_editing import ManualLanguageEditor
import pandas as pd
from datetime import datetime

class InteractiveLanguageEditor:
    """
    Interactive editor with GUI-like interface for manual language editing.
    """
    
    def __init__(self, manuscript_dir="Documents/manuscript_sections",
                 output_dir="outputs/language_editing"):
        """
        Initialize the interactive editor.
        """
        self.editor = ManualLanguageEditor(manuscript_dir, output_dir)
        self.current_section = None
        self.current_text = None
        self.current_changes = []
        
    def display_menu(self):
        """
        Display main menu.
        """
        print("\n" + "="*60)
        print("INTERACTIVE LANGUAGE EDITOR")
        print("="*60)
        print("1. Select manuscript section to edit")
        print("2. Apply all fixes automatically")
        print("3. Step-by-step editing")
        print("4. Review and accept/reject changes")
        print("5. Compare original vs edited")
        print("6. Save and export")
        print("7. Exit")
        print("="*60)
    
    def select_section(self):
        """
        Select a manuscript section to edit.
        """
        sections = list(self.editor.manuscript_dir.glob("*.md"))
        
        if not sections:
            print("No manuscript sections found!")
            return False
        
        print("\nAvailable manuscript sections:")
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section.name}")
        
        try:
            choice = int(input("\nSelect section number: "))
            if 1 <= choice <= len(sections):
                self.current_section = sections[choice-1]
                with open(self.current_section, 'r', encoding='utf-8') as f:
                    self.current_text = f.read()
                print(f"✓ Loaded: {self.current_section.name}")
                return True
            else:
                print("Invalid selection!")
                return False
        except ValueError:
            print("Please enter a valid number!")
            return False
    
    def display_section_preview(self):
        """
        Display preview of the current section.
        """
        if not self.current_text:
            print("No section loaded!")
            return
        
        print(f"\n{'='*60}")
        print(f"SECTION PREVIEW: {self.current_section.name}")
        print(f"{'='*60}")
        
        # Show first 10 lines
        lines = self.current_text.split('\n')[:10]
        for i, line in enumerate(lines, 1):
            print(f"{i:3}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        if len(self.current_text.split('\n')) > 10:
            print("... (truncated)")
        
        # Show statistics
        word_count = len(self.current_text.split())
        line_count = len(self.current_text.split('\n'))
        print(f"\nStatistics: {word_count} words, {line_count} lines")
    
    def step_by_step_editing(self):
        """
        Step-by-step editing with user confirmation for each fix type.
        """
        if not self.current_text:
            print("Please select a section first!")
            return
        
        print(f"\n{'='*60}")
        print(f"STEP-BY-STEP EDITING: {self.current_section.name}")
        print(f"{'='*60}")
        
        # Use the editor's interactive mode
        fixed_text, changes = self.editor._interactive_edit(
            self.current_text, 
            self.current_section.stem
        )
        
        self.current_text = fixed_text
        self.current_changes = changes
        
        print(f"\n✓ Step-by-step editing complete!")
        print(f"  Applied {len(changes)} changes")
    
    def apply_all_fixes(self):
        """
        Apply all fixes automatically.
        """
        if not self.current_text:
            print("Please select a section first!")
            return
        
        print(f"\nApplying all fixes to {self.current_section.name}...")
        
        fixed_text, changes = self.editor.apply_all_fixes(
            self.current_text,
            self.current_section.stem
        )
        
        self.current_text = fixed_text
        self.current_changes = changes
        
        print(f"✓ Applied all fixes: {len(changes)} changes made")
    
    def review_changes(self):
        """
        Review and accept/reject individual changes.
        """
        if not self.current_changes:
            print("No changes to review!")
            return
        
        print(f"\n{'='*60}")
        print(f"REVIEW CHANGES: {len(self.current_changes)} changes")
        print(f"{'='*60}")
        
        accepted_changes = []
        rejected_changes = []
        
        for i, change in enumerate(self.current_changes, 1):
            print(f"\nChange {i}/{len(self.current_changes)}")
            print(f"Type: {change['change_type']}")
            print(f"Line: {change['line_number']}")
            print(f"\nOriginal: {change['original'][:100]}{'...' if len(change['original']) > 100 else ''}")
            print(f"Fixed:    {change['fixed'][:100]}{'...' if len(change['fixed']) > 100 else ''}")
            
            response = input("\nAccept this change? (y/n/s=skip all): ").strip().lower()
            
            if response == 'y':
                accepted_changes.append(change)
                print("✓ Accepted")
            elif response == 'n':
                rejected_changes.append(change)
                print("✗ Rejected")
            elif response == 's':
                print("Skipping remaining changes...")
                # Add remaining to rejected
                rejected_changes.extend(self.current_changes[i:])
                break
            else:
                print("Invalid input, rejecting change")
                rejected_changes.append(change)
        
        print(f"\nReview complete:")
        print(f"  Accepted: {len(accepted_changes)} changes")
        print(f"  Rejected: {len(rejected_changes)} changes")
        
        # TODO: Apply accepted changes to text
        # For now, just update the changes list
        self.current_changes = accepted_changes
    
    def compare_versions(self):
        """
        Compare original vs edited versions.
        """
        if not self.current_section or not self.current_text:
            print("Please select and edit a section first!")
            return
        
        # Read original
        with open(self.current_section, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        print(f"\n{'='*60}")
        print(f"COMPARISON: {self.current_section.name}")
        print(f"{'='*60}")
        
        original_lines = original_text.split('\n')
        edited_lines = self.current_text.split('\n')
        
        max_lines = min(20, len(original_lines), len(edited_lines))
        
        print("\nLine | Original | Edited")
        print("-"*80)
        
        for i in range(max_lines):
            orig = original_lines[i][:40] + ("..." if len(original_lines[i]) > 40 else "")
            edit = edited_lines[i][:40] + ("..." if len(edited_lines[i]) > 40 else "")
            
            if orig != edit:
                # Highlight differences
                print(f"{i+1:4} | \033[91m{orig}\033[0m | \033[92m{edit}\033[0m")
            else:
                print(f"{i+1:4} | {orig} | {edit}")
        
        if len(original_lines) > max_lines or len(edited_lines) > max_lines:
            print("... (truncated)")
    
    def save_and_export(self):
        """
        Save edited section and export changes.
        """
        if not self.current_text or not self.current_section:
            print("Nothing to save!")
            return
        
        # Save edited version
        output_path = self.editor.output_dir / f"{self.current_section.stem}_edited.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.current_text)
        
        # Save changes
        if self.current_changes:
            changes_df = pd.DataFrame(self.current_changes)
            changes_path = self.editor.output_dir / f"{self.current_section.stem}_changes.csv"
            changes_df.to_csv(changes_path, index=False)
            
            # Update editor's change log
            self.editor._update_change_log(self.current_section.stem, self.current_changes)
        
        print(f"\n✓ Saved edited version to: {output_path}")
        if self.current_changes:
            print(f"✓ Saved changes log to: {changes_path}")
        
        # Export to Excel
        excel_path = self.editor.export_change_log_excel()
        if excel_path:
            print(f"✓ Exported change log to Excel: {excel_path}")
    
    def run(self):
        """
        Main interactive loop.
        """
        print("\n" + "="*60)
        print("WELCOME TO INTERACTIVE LANGUAGE EDITOR")
        print("="*60)
        print("This tool helps you manually edit manuscript sections")
        print("with step-by-step guidance and change tracking.")
        print("="*60)
        
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == '1':
                    self.select_section()
                    if self.current_section:
                        self.display_section_preview()
                
                elif choice == '2':
                    if self.current_section:
                        self.apply_all_fixes()
                    else:
                        print("Please select a section first!")
                
                elif choice == '3':
                    if self.current_section:
                        self.step_by_step_editing()
                    else:
                        print("Please select a section first!")
                
                elif choice == '4':
                    if self.current_changes:
                        self.review_changes()
                    else:
                        print("No changes to review! Apply fixes first.")
                
                elif choice == '5':
                    if self.current_section:
                        self.compare_versions()
                    else:
                        print("Please select a section first!")
                
                elif choice == '6':
                    self.save_and_export()
                
                elif choice == '7':
                    print("\nThank you for using Interactive Language Editor!")
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid choice! Please enter 1-7.")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")


def main():
    """
    Main function.
    """
    editor = InteractiveLanguageEditor()
    editor.run()


if __name__ == "__main__":
    main()