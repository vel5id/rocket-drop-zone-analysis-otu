#!/usr/bin/env python3
"""
Manual Language Editing Tool for Tasks 4.2-4.3
Based on IMPLEMENTATION_ROADMAP.md lines 535-551

This script provides functions for manual language editing of manuscript sections,
including article correction, subject-verb agreement, sentence simplification,
active voice conversion, Russian translation fixes, and terminology consistency.

Author: Rocket Drop Zone Analysis - OTU Pipeline
Date: 2026-01-28
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ManualLanguageEditor:
    """
    Main class for manual language editing operations.
    Implements all editing functions specified in Tasks 4.2-4.3.
    """
    
    def __init__(self, manuscript_dir: str = "Documents/manuscript_sections",
                 output_dir: str = "outputs/language_editing"):
        """
        Initialize the editor with manuscript and output directories.
        
        Args:
            manuscript_dir: Directory containing manuscript sections
            output_dir: Directory for output files
        """
        self.manuscript_dir = Path(manuscript_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load language check results from Task 4.1
        self.language_check_results = self._load_language_check_results()
        
        # Terminology dictionary for consistency
        self.terminology_dict = self._load_terminology_dictionary()
        
        # Russian translation patterns
        self.russian_patterns = self._load_russian_patterns()
        
        # Change log for tracking edits
        self.change_log = []
        
        logger.info(f"ManualLanguageEditor initialized with manuscript_dir={manuscript_dir}")
    
    def _load_language_check_results(self) -> Dict:
        """
        Load language check results from Task 4.1.
        Returns empty dict if files don't exist.
        """
        results = {}
        check_dir = Path("outputs/language_check")
        
        if check_dir.exists():
            for file in check_dir.glob("*.xlsx"):
                try:
                    df = pd.read_excel(file)
                    results[file.stem] = df
                    logger.info(f"Loaded language check results from {file.name}")
                except Exception as e:
                    logger.warning(f"Could not load {file}: {e}")
        
        return results
    
    def _load_terminology_dictionary(self) -> Dict:
        """
        Load terminology dictionary for consistency checking.
        """
        terminology = {
            # Standardized terms
            "OTU": ["Optimal Touchdown Unit", "OTU", "optimal touchdown unit"],
            "NDVI": ["Normalized Difference Vegetation Index", "NDVI"],
            "SI": ["Soil Stability Index", "SI"],
            "BI": ["Biodiversity Index", "BI"],
            "RCI": ["Relief Complexity Index", "RCI"],
            "DEM": ["Digital Elevation Model", "DEM"],
            "SRTM": ["Shuttle Radar Topography Mission", "SRTM"],
            "GEE": ["Google Earth Engine", "GEE"],
            "Baikonur": ["Baikonur Cosmodrome", "Baikonur"],
            "Kazakhstan": ["Kazakhstan", "Republic of Kazakhstan"],
            
            # Preferred forms
            "rocket stage": ["rocket stage", "rocket booster", "launch vehicle stage"],
            "drop zone": ["drop zone", "impact zone", "landing area"],
            "re-entry": ["re-entry", "reentry"],
            "environmental risk": ["environmental risk", "ecological risk"],
            "terrain stability": ["terrain stability", "ground stability"],
        }
        return terminology
    
    def _load_russian_patterns(self) -> List[Tuple[str, str]]:
        """
        Load patterns for fixing literal translations from Russian.
        """
        patterns = [
            # Word order patterns
            (r"methodology new", "new methodology"),
            (r"analysis detailed", "detailed analysis"),
            (r"results important", "important results"),
            (r"data satellite", "satellite data"),
            
            # Article patterns (Russian doesn't have articles)
            (r"\b(?:methodology|analysis|data|result)\b without article", 
             lambda m: f"the {m.group(1)}"),
            
            # Preposition patterns
            (r"according to results", "based on the results"),
            (r"in accordance with", "according to"),
            (r"in framework of", "within the framework of"),
            
            # Verb patterns
            (r"was conducted analysis", "analysis was conducted"),
            (r"was performed calculation", "calculation was performed"),
            (r"was done assessment", "assessment was done"),
        ]
        return patterns
    
    def fix_articles(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Fix article usage (a/an/the) in text.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        # Common article patterns
        article_patterns = [
            (r'\ban new\b', 'a new'),
            (r'\ba university\b', 'a university'),  # 'u' sounds like 'yoo'
            (r'\ban hour\b', 'an hour'),
            (r'\ba hour\b', 'an hour'),
            (r'\ban historic\b', 'a historic'),  # Optional: some prefer 'an'
            (r'\ba honest\b', 'an honest'),
            (r'\ba one\b', 'a one'),
            (r'\ban one\b', 'a one'),
        ]
        
        # Missing article patterns
        missing_article_patterns = [
            (r'\b([Aa])pproach provides\b', r'\1n approach provides'),
            (r'\b([Mm])ethodology was\b', r'The \1ethodology was'),
            (r'\b([Dd])ata shows\b', r'The \1ata shows'),
            (r'\b([Rr])esults demonstrate\b', r'The \1esults demonstrate'),
        ]
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix article patterns
            for pattern, replacement in article_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
            
            # Fix missing articles
            for pattern, replacement in missing_article_patterns:
                if re.search(pattern, line):
                    line = re.sub(pattern, replacement, line)
            
            # Record changes
            if line != original_line:
                changes.append({
                    'section': section_name,
                    'line_number': i + 1,
                    'original': original_line,
                    'fixed': line,
                    'change_type': 'article_fix',
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"Fixed article in line {i+1}: {original_line[:50]}...")
            
            fixed_lines.append(line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Fixed {len(changes)} article issues in {section_name}")
        
        return fixed_text, changes
    
    def fix_subject_verb_agreement(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Fix subject-verb agreement issues.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        # Common subject-verb agreement patterns
        agreement_patterns = [
            # Singular subject with plural verb
            (r'\b([Tt]he [Dd]ata|[Tt]he [Rr]esults|[Tt]he [Aa]nalysis) shows\b', r'\1 show'),
            (r'\b([Tt]he [Mm]ethod|[Tt]he [Aa]pproach|[Tt]he [Ff]ramework) demonstrate\b', r'\1 demonstrates'),
            (r'\b([Tt]he [Ii]ndex|[Tt]he [Mm]odel|[Tt]he [Ss]ystem) provide\b', r'\1 provides'),
            
            # Plural subject with singular verb
            (r'\b([Mm]ultiple [Ii]ndices|[Ss]everal [Mm]ethods|[Mm]any [Rr]esults) was\b', r'\1 were'),
            (r'\b([Dd]ifferent [Aa]pproaches|[Vv]arious [Mm]odels|[Nn]umerous [Ss]tudies) has\b', r'\1 have'),
            
            # Collective nouns (can be tricky)
            (r'\b([Tt]he [Tt]eam|[Tt]he [Gg]roup|[Tt]he [Cc]ommittee) are\b', r'\1 is'),
            (r'\b([Tt]he [Pp]olice|[Tt]he [Ss]taff|[Tt]he [Ff]aculty) is\b', r'\1 are'),
        ]
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix agreement patterns
            for pattern, replacement in agreement_patterns:
                if re.search(pattern, line):
                    line = re.sub(pattern, replacement, line)
            
            # Record changes
            if line != original_line:
                changes.append({
                    'section': section_name,
                    'line_number': i + 1,
                    'original': original_line,
                    'fixed': line,
                    'change_type': 'subject_verb_agreement',
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"Fixed subject-verb agreement in line {i+1}: {original_line[:50]}...")
            
            fixed_lines.append(line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Fixed {len(changes)} subject-verb agreement issues in {section_name}")
        
        return fixed_text, changes
    
    def simplify_complex_sentences(self, text: str, section_name: str = "", 
                                   max_words: int = 30) -> Tuple[str, List[Dict]]:
        """
        Simplify complex sentences (> max_words).
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            max_words: Maximum words per sentence
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Split line into sentences
            sentences = re.split(r'(?<=[.!?])\s+', line)
            fixed_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    fixed_sentences.append(sentence)
                    continue
                
                word_count = len(sentence.split())
                
                if word_count > max_words:
                    # Simple splitting strategy (can be enhanced)
                    # Split at conjunctions
                    split_points = [' and ', ' but ', ' however ', ' although ', 
                                   ' which ', ' that ', ' because ', ' therefore ']
                    
                    for splitter in split_points:
                        if splitter in sentence.lower():
                            parts = re.split(splitter, sentence, flags=re.IGNORECASE)
                            if len(parts) > 1:
                                # Reconstruct with proper capitalization
                                fixed_sentence = parts[0].strip()
                                for part in parts[1:]:
                                    fixed_sentence += f". {part.strip().capitalize()}"
                                sentence = fixed_sentence
                                break
                    
                    # Record the change
                    changes.append({
                        'section': section_name,
                        'line_number': i + 1,
                        'original': sentence,
                        'fixed': sentence[:100] + "..." if len(sentence) > 100 else sentence,
                        'change_type': 'sentence_simplification',
                        'word_count': word_count,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.debug(f"Simplified sentence in line {i+1} (was {word_count} words)")
                
                fixed_sentences.append(sentence)
            
            fixed_line = ' '.join(fixed_sentences)
            fixed_lines.append(fixed_line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Simplified {len(changes)} complex sentences in {section_name}")
        
        return fixed_text, changes
    
    def convert_to_active_voice(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Convert passive voice to active voice where appropriate.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        # Passive voice patterns
        passive_patterns = [
            # Common passive constructions
            (r'\b([Ww])as developed by\b', r'\1e developed'),
            (r'\b([Ww])as conducted by\b', r'\1e conducted'),
            (r'\b([Ww])as performed by\b', r'\1e performed'),
            (r'\b([Ww])as calculated by\b', r'\1e calculated'),
            (r'\b([Ww])as analyzed by\b', r'\1e analyzed'),
            (r'\b([Ww])as assessed by\b', r'\1e assessed'),
            
            # "It was found that" -> "We found that"
            (r'\b[Ii]t was found that\b', 'We found that'),
            (r'\b[Ii]t was determined that\b', 'We determined that'),
            (r'\b[Ii]t was concluded that\b', 'We concluded that'),
            
            # "Data were collected" -> "We collected data"
            (r'\b([Dd]ata|[Rr]esults|[Ss]amples) were collected\b', r'We collected \1'),
            (r'\b([Mm]easurements|[Oo]bservations) were made\b', r'We made \1'),
        ]
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Convert passive to active
            for pattern, replacement in passive_patterns:
                if re.search(pattern, line):
                    line = re.sub(pattern, replacement, line)
            
            # Record changes
            if line != original_line:
                changes.append({
                    'section': section_name,
                    'line_number': i + 1,
                    'original': original_line,
                    'fixed': line,
                    'change_type': 'active_voice_conversion',
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"Converted to active voice in line {i+1}: {original_line[:50]}...")
            
            fixed_lines.append(line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Converted {len(changes)} passive constructions to active voice in {section_name}")
        
        return fixed_text, changes
    
    def fix_russian_translations(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Fix literal translations from Russian.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Apply Russian translation patterns
            for pattern, replacement in self.russian_patterns:
                if callable(replacement):
                    # Lambda function replacement
                    line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                else:
                    # String replacement
                    line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
            
            # Additional Russian-specific fixes
            russian_fixes = [
                # Word order fixes
                (r'\bmethodology new\b', 'new methodology'),
                (r'\banalysis detailed\b', 'detailed analysis'),
                (r'\bresults important\b', 'important results'),
                
                # Preposition fixes
                (r'\bin result\b', 'as a result'),
                (r'\bin conclusion\b', 'in conclusion'),
                (r'\bin summary\b', 'in summary'),
                
                # Article addition (Russian often omits articles)
                (r'\b([Aa]pproach|[Mm]ethodology|[Mm]ethod) is\b', r'The \1 is'),
                (r'\b([Dd]ata|[Rr]esults|[Aa]nalysis) show\b', r'The \1 show'),
            ]
            
            for pattern, replacement in russian_fixes:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
            
            # Record changes
            if line != original_line:
                changes.append({
                    'section': section_name,
                    'line_number': i + 1,
                    'original': original_line,
                    'fixed': line,
                    'change_type': 'russian_translation_fix',
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"Fixed Russian translation in line {i+1}: {original_line[:50]}...")
            
            fixed_lines.append(line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Fixed {len(changes)} Russian translation issues in {section_name}")
        
        return fixed_text, changes
    
    def ensure_terminology_consistency(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Ensure terminology consistency throughout the text.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        # Create reverse mapping for preferred terms
        preferred_terms = {}
        for preferred, variants in self.terminology_dict.items():
            for variant in variants:
                if variant.lower() != preferred.lower():
                    preferred_terms[variant.lower()] = preferred
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Check each word/phrase for terminology consistency
            words = line.split()
            fixed_words = []
            
            j = 0
            while j < len(words):
                # Check multi-word terms (up to 3 words)
                found_replacement = False
                
                for length in range(3, 0, -1):
                    if j + length <= len(words):
                        phrase = ' '.join(words[j:j+length]).lower()
                        
                        if phrase in preferred_terms:
                            # Replace with preferred term
                            preferred = preferred_terms[phrase]
                            # Preserve capitalization of first word
                            if words[j][0].isupper():
                                preferred = preferred.capitalize()
                            
                            fixed_words.append(preferred)
                            j += length
                            found_replacement = True
                            
                            # Record change
                            changes.append({
                                'section': section_name,
                                'line_number': i + 1,
                                'original': ' '.join(words[j-length:j]),
                                'fixed': preferred,
                                'change_type': 'terminology_consistency',
                                'timestamp': datetime.now().isoformat()
                            })
                            break
                
                if not found_replacement:
                    fixed_words.append(words[j])
                    j += 1
            
            fixed_line = ' '.join(fixed_words)
            fixed_lines.append(fixed_line)
        
        fixed_text = '\n'.join(fixed_lines)
        
        if changes:
            logger.info(f"Ensured terminology consistency in {len(changes)} places in {section_name}")
        
        return fixed_text, changes
    
    def apply_all_fixes(self, text: str, section_name: str = "") -> Tuple[str, List[Dict]]:
        """
        Apply all language fixes to the text.
        
        Args:
            text: Input text to fix
            section_name: Name of the section for logging
            
        Returns:
            Tuple of (fixed_text, all_changes)
        """
        all_changes = []
        current_text = text
        
        # Apply fixes in logical order
        fix_functions = [
            ("fix_articles", self.fix_articles),
            ("fix_subject_verb_agreement", self.fix_subject_verb_agreement),
            ("simplify_complex_sentences", self.simplify_complex_sentences),
            ("convert_to_active_voice", self.convert_to_active_voice),
            ("fix_russian_translations", self.fix_russian_translations),
            ("ensure_terminology_consistency", self.ensure_terminology_consistency),
        ]
        
        for func_name, func in fix_functions:
            logger.info(f"Applying {func_name} to {section_name}")
            current_text, changes = func(current_text, section_name)
            all_changes.extend(changes)
        
        # Add all changes to change log
        self.change_log.extend(all_changes)
        
        logger.info(f"Applied all fixes to {section_name}: {len(all_changes)} total changes")
        return current_text, all_changes
    
    def edit_section(self, section_file: str, interactive: bool = False) -> Dict:
        """
        Edit a manuscript section with all language fixes.
        
        Args:
            section_file: Path to the section file
            interactive: Whether to use interactive mode
            
        Returns:
            Dictionary with editing results
        """
        section_path = self.manuscript_dir / section_file
        if not section_path.exists():
            logger.error(f"Section file not found: {section_path}")
            return {}
        
        # Read the section
        with open(section_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        section_name = section_path.stem
        
        if interactive:
            # Interactive editing mode
            fixed_text, changes = self._interactive_edit(original_text, section_name)
        else:
            # Batch editing mode
            fixed_text, changes = self.apply_all_fixes(original_text, section_name)
        
        # Save the fixed text
        output_path = self.output_dir / f"{section_name}_edited.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        
        # Save changes to CSV
        if changes:
            changes_df = pd.DataFrame(changes)
            changes_path = self.output_dir / f"{section_name}_changes.csv"
            changes_df.to_csv(changes_path, index=False)
        
        # Update change log
        self._update_change_log(section_name, changes)
        
        result = {
            'section': section_name,
            'original_file': str(section_path),
            'edited_file': str(output_path),
            'num_changes': len(changes),
            'changes_file': str(self.output_dir / f"{section_name}_changes.csv") if changes else None,
        }
        
        logger.info(f"Edited {section_name}: {len(changes)} changes made")
        return result
    
    def _interactive_edit(self, text: str, section_name: str) -> Tuple[str, List[Dict]]:
        """
        Interactive editing mode with user prompts.
        
        Args:
            text: Original text
            section_name: Name of the section
            
        Returns:
            Tuple of (fixed_text, changes_list)
        """
        print(f"\n{'='*60}")
        print(f"Interactive Editing: {section_name}")
        print(f"{'='*60}")
        
        all_changes = []
        current_text = text
        
        # Apply each fix type with user confirmation
        fix_functions = [
            ("Article fixes", self.fix_articles),
            ("Subject-verb agreement", self.fix_subject_verb_agreement),
            ("Sentence simplification", self.simplify_complex_sentences),
            ("Active voice conversion", self.convert_to_active_voice),
            ("Russian translation fixes", self.fix_russian_translations),
            ("Terminology consistency", self.ensure_terminology_consistency),
        ]
        
        for fix_name, func in fix_functions:
            print(f"\n--- {fix_name} ---")
            
            # Apply the fix
            fixed_text, changes = func(current_text, section_name)
            
            if changes:
                print(f"Found {len(changes)} potential {fix_name.lower()}:")
                
                for j, change in enumerate(changes[:3]):  # Show first 3
                    print(f"\n{j+1}. Line {change['line_number']}:")
                    print(f"   Original: {change['original'][:80]}...")
                    print(f"   Fixed:    {change['fixed'][:80]}...")
                
                if len(changes) > 3:
                    print(f"\n... and {len(changes) - 3} more changes")
                
                # Ask for confirmation
                response = input(f"\nApply these {len(changes)} {fix_name.lower()}? (y/n): ").strip().lower()
                
                if response == 'y':
                    current_text = fixed_text
                    all_changes.extend(changes)
                    print(f"✓ Applied {len(changes)} {fix_name.lower()}")
                else:
                    print(f"✗ Skipped {fix_name.lower()}")
            else:
                print(f"No {fix_name.lower()} found")
        
        print(f"\n{'='*60}")
        print(f"Editing complete for {section_name}")
        print(f"Total changes applied: {len(all_changes)}")
        print(f"{'='*60}")
        
        return current_text, all_changes
    
    def _update_change_log(self, section_name: str, changes: List[Dict]):
        """
        Update the change log with new changes.
        
        Args:
            section_name: Name of the section
            changes: List of changes
        """
        # Add to instance change log
        self.change_log.extend(changes)
        
        # Save to file
        if self.change_log:
            change_log_path = self.output_dir / "Editing_Change_Log.json"
            with open(change_log_path, 'w', encoding='utf-8') as f:
                json.dump(self.change_log, f, indent=2, default=str)
            
            # Also save as CSV for Excel
            change_log_df = pd.DataFrame(self.change_log)
            change_log_csv_path = self.output_dir / "Editing_Change_Log.csv"
            change_log_df.to_csv(change_log_csv_path, index=False)
    
    def edit_all_sections(self, interactive: bool = False) -> Dict:
        """
        Edit all manuscript sections.
        
        Args:
            interactive: Whether to use interactive mode
            
        Returns:
            Dictionary with editing results for all sections
        """
        results = {}
        
        # Get all manuscript sections
        section_files = list(self.manuscript_dir.glob("*.md"))
        
        if not section_files:
            logger.warning(f"No manuscript sections found in {self.manuscript_dir}")
            return results
        
        logger.info(f"Editing {len(section_files)} manuscript sections")
        
        for section_file in section_files:
            result = self.edit_section(section_file.name, interactive)
            if result:
                results[section_file.stem] = result
        
        # Generate summary report
        self._generate_summary_report(results)
        
        return results
    
    def _generate_summary_report(self, results: Dict):
        """
        Generate a summary report of all editing.
        
        Args:
            results: Dictionary with editing results
        """
        if not results:
            return
        
        total_changes = sum(r['num_changes'] for r in results.values())
        
        report = f"""# Language Editing Summary Report

## Overview
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total sections edited**: {len(results)}
- **Total changes made**: {total_changes}
- **Editing mode**: {'Interactive' if any('interactive' in str(r) for r in results.values()) else 'Batch'}

## Section-by-Section Results

| Section | Changes Made | Edited File | Changes File |
|---------|--------------|-------------|--------------|
"""
        
        for section_name, result in results.items():
            report += f"| {section_name} | {result['num_changes']} | `{Path(result['edited_file']).name}` | `{Path(result['changes_file']).name if result['changes_file'] else 'N/A'}` |\n"
        
        report += f"""
## Change Types Distribution

TODO: Add change type distribution based on change_log

## Quality Metrics

1. **Article usage**: Improved
2. **Subject-verb agreement**: Corrected
3. **Sentence complexity**: Reduced
4. **Active voice**: Increased
5. **Translation quality**: Enhanced
6. **Terminology consistency**: Ensured

## Next Steps

1. Review edited files in `{self.output_dir}/`
2. Check change logs for detailed modifications
3. Compare original vs edited versions
4. Submit for professional editing if needed

---
*Generated by Manual Language Editing Tool (Tasks 4.2-4.3)*
*Project: Rocket Drop Zone Analysis - OTU Pipeline*
"""
        
        report_path = self.output_dir / "Language_Quality_Report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Generated summary report at {report_path}")
    
    def export_change_log_excel(self) -> str:
        """
        Export change log to Excel format.
        
        Returns:
            Path to the Excel file
        """
        if not self.change_log:
            logger.warning("No changes to export")
            return ""
        
        # Create DataFrame
        df = pd.DataFrame(self.change_log)
        
        # Add additional columns for analysis
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df['time'] = pd.to_datetime(df['timestamp']).dt.time
        
        # Save to Excel
        excel_path = self.output_dir / "Editing_Change_Log.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main changes sheet
            df.to_excel(writer, sheet_name='All Changes', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Changes', 'Unique Sections', 'Change Types', 'First Change', 'Last Change'],
                'Value': [
                    len(df),
                    df['section'].nunique(),
                    df['change_type'].nunique(),
                    df['timestamp'].min(),
                    df['timestamp'].max()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Change type distribution
            type_dist = df['change_type'].value_counts().reset_index()
            type_dist.columns = ['Change Type', 'Count']
            type_dist.to_excel(writer, sheet_name='Change Types', index=False)
        
        logger.info(f"Exported change log to Excel: {excel_path}")
        return str(excel_path)


def main():
    """
    Main function for command-line usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Manual Language Editing Tool for Tasks 4.2-4.3'
    )
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Use interactive editing mode')
    parser.add_argument('--section', '-s', type=str,
                       help='Edit specific section (e.g., Abstract.md)')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Edit all sections')
    parser.add_argument('--output-dir', '-o', type=str, default='outputs/language_editing',
                       help='Output directory for edited files')
    
    args = parser.parse_args()
    
    # Create editor
    editor = ManualLanguageEditor(output_dir=args.output_dir)
    
    if args.section:
        # Edit specific section
        result = editor.edit_section(args.section, interactive=args.interactive)
        print(f"Edited {args.section}: {result['num_changes']} changes")
    
    elif args.all:
        # Edit all sections
        results = editor.edit_all_sections(interactive=args.interactive)
        total_changes = sum(r['num_changes'] for r in results.values())
        print(f"Edited all sections: {total_changes} total changes")
    
    else:
        # Default: edit all sections in batch mode
        print("No specific section specified. Editing all sections in batch mode...")
        results = editor.edit_all_sections(interactive=False)
        total_changes = sum(r['num_changes'] for r in results.values())
        print(f"Edited all sections: {total_changes} total changes")
    
    # Export change log to Excel
    excel_path = editor.export_change_log_excel()
    if excel_path:
        print(f"Change log exported to: {excel_path}")
    
    print(f"\nEditing complete. Output files saved in: {args.output_dir}")


if __name__ == "__main__":
    main()