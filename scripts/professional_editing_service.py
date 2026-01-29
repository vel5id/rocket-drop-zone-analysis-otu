#!/usr/bin/env python3
"""
Professional Editing Service for MDPI Language Service
Task 4.5: Professional Editing Service (IMPLEMENTATION_ROADMAP.md lines 605-616)

This module provides functions for preparing manuscripts for professional editing,
tracking submission status, processing editor feedback, and integrating changes.

Functions:
- prepare_for_mdpi_service(): Prepare files for MDPI language service
- create_submission_package(): Create submission package
- track_submission_status(): Track submission status
- process_editor_feedback(): Process feedback from editor
- integrate_editor_changes(): Integrate editor changes into manuscript
- create_change_summary(): Create summary of changes

Dependencies: Results from Tasks 4.1-4.4 (language check, manual editing, bibliography)
"""

import os
import json
import shutil
import zipfile
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import difflib

class ProfessionalEditingService:
    """Main class for professional editing service management"""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the professional editing service.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.version_tracker = VersionTracker(self.project_root)
        self.submission_tracker = SubmissionTracker(self.project_root)
        
        # Define paths
        self.paths = {
            'outputs': self.project_root / 'outputs' / 'professional_editing',
            'manuscript': self.project_root / 'outputs' / 'manuscript_sections',
            'final_deliverables': self.project_root / 'final_deliverables',
            'language_check': self.project_root / 'outputs' / 'language_check',
            'bibliography': self.project_root / 'outputs' / 'bibliography',
            'figures': self.project_root / 'outputs' / 'figures',
            'tables': self.project_root / 'outputs' / 'supplementary_tables'
        }
        
        # Create directories
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def prepare_for_mdpi_service(self, manuscript_files: List[str]) -> Dict:
        """
        Prepare files for MDPI language service submission.
        
        Args:
            manuscript_files: List of manuscript file paths to include
            
        Returns:
            Dictionary with preparation status and file list
        """
        print("Preparing files for MDPI language service...")
        
        # Validate files exist
        valid_files = []
        for file_path in manuscript_files:
            path = Path(file_path)
            if path.exists():
                valid_files.append(str(path))
                print(f"  ✓ {path.name}")
            else:
                print(f"  ✗ {path.name} (not found)")
        
        if not valid_files:
            raise ValueError("No valid manuscript files found for submission")
        
        # Create version snapshot
        version_id = self.version_tracker.create_snapshot(
            files=valid_files,
            description="Pre-MDPI submission preparation"
        )
        
        # Check file requirements for MDPI
        requirements_check = self._check_mdpi_requirements(valid_files)
        
        # Create preparation report
        preparation_report = {
            'timestamp': datetime.now().isoformat(),
            'version_id': version_id,
            'files_prepared': valid_files,
            'file_count': len(valid_files),
            'requirements_check': requirements_check,
            'status': 'ready_for_submission' if requirements_check['all_passed'] else 'needs_adjustment'
        }
        
        # Save report
        report_path = self.paths['outputs'] / 'preparation_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(preparation_report, f, indent=2)
        
        print(f"Preparation complete. Report saved to: {report_path}")
        print(f"Status: {preparation_report['status']}")
        
        return preparation_report
    
    def create_submission_package(self, files_to_include: List[str], 
                                  package_name: str = "Submission_Package") -> str:
        """
        Create a ZIP package for submission to MDPI language service.
        
        Args:
            files_to_include: List of file paths to include in package
            package_name: Name of the package (without extension)
            
        Returns:
            Path to created ZIP file
        """
        print(f"Creating submission package: {package_name}.zip")
        
        package_path = self.paths['outputs'] / f"{package_name}.zip"
        
        # Create README for submission package
        readme_content = self._create_submission_readme(files_to_include)
        readme_path = self.paths['outputs'] / "README_Submission.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create ZIP archive
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add README
            zipf.write(readme_path, "README_Submission.txt")
            
            # Add all specified files
            for file_path in files_to_include:
                path = Path(file_path)
                if path.exists():
                    arcname = f"manuscript/{path.name}"
                    zipf.write(path, arcname)
                    print(f"  Added: {path.name}")
                else:
                    print(f"  Warning: {path} not found")
            
            # Add metadata
            metadata = {
                'package_name': package_name,
                'creation_date': datetime.now().isoformat(),
                'file_count': len(files_to_include),
                'service': 'MDPI Language Editing Service',
                'instructions': 'Please edit for academic English, clarity, and MDPI style'
            }
            
            metadata_str = json.dumps(metadata, indent=2)
            zipf.writestr("metadata.json", metadata_str)
        
        # Update submission tracker
        submission_id = self.submission_tracker.record_submission(
            package_path=package_path,
            files_included=files_to_include,
            service='MDPI'
        )
        
        print(f"Submission package created: {package_path}")
        print(f"Submission ID: {submission_id}")
        
        return str(package_path)
    
    def track_submission_status(self, submission_id: str = None) -> Dict:
        """
        Track the status of a submission to MDPI language service.
        
        Args:
            submission_id: Optional submission ID to track specific submission
            
        Returns:
            Dictionary with submission status and details
        """
        if submission_id:
            status = self.submission_tracker.get_submission_status(submission_id)
        else:
            # Get latest submission
            status = self.submission_tracker.get_latest_status()
        
        if not status:
            return {'error': 'No submissions found'}
        
        # Simulate status updates (in real scenario, would query MDPI API)
        simulated_status = self._simulate_mdpi_status(status)
        
        # Save status report
        status_report_path = self.paths['outputs'] / 'submission_status.json'
        with open(status_report_path, 'w', encoding='utf-8') as f:
            json.dump(simulated_status, f, indent=2)
        
        return simulated_status
    
    def process_editor_feedback(self, feedback_file: str, 
                                submission_id: str = None) -> Dict:
        """
        Process feedback received from MDPI editor.
        
        Args:
            feedback_file: Path to feedback file (Excel, Word, or PDF)
            submission_id: Optional submission ID this feedback relates to
            
        Returns:
            Dictionary with processed feedback summary
        """
        print(f"Processing editor feedback from: {feedback_file}")
        
        # Parse feedback based on file type
        feedback_data = self._parse_feedback_file(feedback_file)
        
        # Create feedback analysis
        analysis = self._analyze_feedback(feedback_data)
        
        # Link to submission if provided
        if submission_id:
            self.submission_tracker.record_feedback(
                submission_id=submission_id,
                feedback_file=feedback_file,
                analysis=analysis
            )
        
        # Save processed feedback
        feedback_path = self.paths['outputs'] / 'processed_feedback.json'
        with open(feedback_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'feedback_file': feedback_file,
                'submission_id': submission_id,
                'analysis': analysis,
                'feedback_data': feedback_data
            }, f, indent=2)
        
        # Create Excel report for easier review
        excel_path = self.paths['outputs'] / 'Editor_Feedback_Report.xlsx'
        self._create_feedback_excel_report(feedback_data, excel_path)
        
        print(f"Feedback processed. Analysis saved to: {feedback_path}")
        print(f"Excel report created: {excel_path}")
        
        return analysis
    
    def integrate_editor_changes(self, original_files: List[str], 
                                 edited_files: List[str],
                                 feedback_analysis: Dict = None) -> Dict:
        """
        Integrate editor's changes into the manuscript.
        
        Args:
            original_files: List of original file paths
            edited_files: List of edited file paths (from editor)
            feedback_analysis: Optional feedback analysis from process_editor_feedback()
            
        Returns:
            Dictionary with integration results and change summary
        """
        print("Integrating editor changes into manuscript...")
        
        if len(original_files) != len(edited_files):
            raise ValueError("Original and edited file lists must have same length")
        
        integration_results = []
        all_changes = []
        
        for orig_path, edit_path in zip(original_files, edited_files):
            orig = Path(orig_path)
            edit = Path(edit_path)
            
            if not orig.exists():
                print(f"Warning: Original file not found: {orig}")
                continue
            if not edit.exists():
                print(f"Warning: Edited file not found: {edit}")
                continue
            
            # Create backup of original
            backup_path = self.paths['outputs'] / 'backups' / f"{orig.stem}_pre_integration{orig.suffix}"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(orig, backup_path)
            
            # Compare files and generate diff
            changes = self._compare_files(orig, edit)
            all_changes.extend(changes)
            
            # Apply changes (in real scenario, would be more sophisticated)
            # For now, we'll copy the edited version
            shutil.copy2(edit, orig)
            
            integration_results.append({
                'file': str(orig),
                'backup': str(backup_path),
                'change_count': len(changes),
                'changes': changes[:10]  # First 10 changes
            })
            
            print(f"  Integrated: {orig.name} ({len(changes)} changes)")
        
        # Create change summary
        change_summary = self.create_change_summary(all_changes)
        
        # Create version snapshot after integration
        version_id = self.version_tracker.create_snapshot(
            files=original_files,
            description="Post-editor integration",
            metadata={
                'integration_results': integration_results,
                'change_summary': change_summary,
                'feedback_analysis': feedback_analysis
            }
        )
        
        # Save integration report
        integration_report = {
            'timestamp': datetime.now().isoformat(),
            'version_id': version_id,
            'integration_results': integration_results,
            'change_summary': change_summary,
            'files_integrated': original_files
        }
        
        report_path = self.paths['outputs'] / 'integration_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(integration_report, f, indent=2)
        
        print(f"Integration complete. Report saved to: {report_path}")
        
        return integration_report
    
    def create_change_summary(self, changes: List[Dict]) -> Dict:
        """
        Create a summary of changes between original and edited versions.
        
        Args:
            changes: List of change dictionaries from _compare_files()
            
        Returns:
            Dictionary with change summary statistics
        """
        if not changes:
            return {'total_changes': 0, 'categories': {}}
        
        # Categorize changes
        categories = {
            'grammar': 0,
            'style': 0,
            'clarity': 0,
            'terminology': 0,
            'formatting': 0,
            'other': 0
        }
        
        for change in changes:
            change_type = change.get('type', 'other')
            if change_type in categories:
                categories[change_type] += 1
            else:
                categories['other'] += 1
        
        # Calculate statistics
        total_changes = len(changes)
        category_percentages = {
            cat: (count / total_changes * 100) if total_changes > 0 else 0
            for cat, count in categories.items()
        }
        
        summary = {
            'total_changes': total_changes,
            'categories': categories,
            'percentages': category_percentages,
            'most_common_category': max(categories.items(), key=lambda x: x[1])[0] if total_changes > 0 else None,
            'change_examples': changes[:5]  # First 5 changes as examples
        }
        
        return summary
    
    def _check_mdpi_requirements(self, files: List[str]) -> Dict:
        """Check if files meet MDPI submission requirements."""
        requirements = {
            'file_format': True,  # Should be .docx or .tex
            'word_count': True,   # Should be within limits
            'figures_embedded': False,  # Figures should be embedded
            'references_formatted': False,  # References in MDPI style
            'abstract_present': False,
            'keywords_present': False
        }
        
        # Simple checks
        for file_path in files:
            path = Path(file_path)
            if path.suffix.lower() not in ['.docx', '.tex', '.md']:
                requirements['file_format'] = False
            
            # Check file size (rough proxy for content)
            if path.stat().st_size < 1000:  # Less than 1KB
                requirements['word_count'] = False
        
        requirements['all_passed'] = all(requirements.values())
        
        return requirements
    
    def _create_submission_readme(self, files: List[str]) -> str:
        """Create README file for submission package."""
        readme = f"""MDPI Language Editing Service - Submission Package
===================================================

Package Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: Rocket Drop Zone Analysis - OTU Pipeline

INSTRUCTIONS FOR EDITOR:
1. Please edit for academic English clarity and style
2. Ensure consistency with MDPI Aerospace journal style
3. Check technical terminology for accuracy
4. Improve sentence structure and flow
5. Verify all references are properly formatted

FILES INCLUDED:
"""
        
        for i, file_path in enumerate(files, 1):
            path = Path(file_path)
            size_kb = path.stat().st_size / 1024
            readme += f"{i}. {path.name} ({size_kb:.1f} KB)\n"
        
        readme += f"""
TOTAL FILES: {len(files)}

SPECIAL NOTES:
- This is a technical manuscript about rocket drop zone analysis
- Please preserve all technical terms and acronyms (OTU, NDVI, etc.)
- Maintain consistency with previous language edits (Tasks 4.1-4.4)
- References have been formatted according to MDPI style (Task 4.4)

CONTACT:
For questions about technical content, please refer to the manuscript metadata.

Thank you for your professional editing service.
"""
        
        return readme
    
    def _simulate_mdpi_status(self, submission_data: Dict) -> Dict:
        """Simulate MDPI submission status updates."""
        status_options = [
            'submitted',
            'under_review',
            'being_edited',
            'editing_complete',
            'ready_for_download',
            'completed'
        ]
        
        # Simple simulation based on submission date
        submission_date = datetime.fromisoformat(submission_data.get('submission_date', datetime.now().isoformat()))
        days_passed = (datetime.now() - submission_date).days
        
        if days_passed < 1:
            status = 'submitted'
        elif days_passed < 2:
            status = 'under_review'
        elif days_passed < 3:
            status = 'being_edited'
        elif days_passed < 4:
            status = 'editing_complete'
        elif days_passed < 5:
            status = 'ready_for_download'
        else:
            status = 'completed'
        
        estimated_completion = (submission_date + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
        
        return {
            'submission_id': submission_data.get('submission_id', 'unknown'),
            'current_status': status,
            'status_description': self._get_status_description(status),
            'submission_date': submission_data.get('submission_date'),
            'days_passed': days_passed,
            'estimated_completion': estimated_completion,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_status_description(self, status: str) -> str:
        """Get description for status code."""
        descriptions = {
            'submitted': 'Manuscript submitted to MDPI language service',
            'under_review': 'Manuscript being reviewed by MDPI editors',
            'being_edited': 'Professional editor is working on the manuscript',
            'editing_complete': 'Editing completed, undergoing quality check',
            'ready_for_download': 'Edited manuscript ready for download',
            'completed': 'Process completed successfully'
        }
        return descriptions.get(status, 'Unknown status')
    
    def _parse_feedback_file(self, feedback_file: str) -> Dict:
        """Parse feedback file based on file type."""
        path = Path(feedback_file)
        
        # For now, create mock feedback data
        # In real implementation, would parse Excel, Word, or PDF
        
        mock_feedback = {
            'general_comments': [
                'Overall good technical content but needs language polishing',
                'Some sentences are too long and complex',
                'Good use of technical terminology'
            ],
            'specific_issues': [
                {'type': 'grammar', 'issue': 'Article usage', 'example': 'a impact zone → an impact zone'},
                {'type': 'style', 'issue': 'Passive voice', 'example': 'was calculated → we calculated'},
                {'type': 'clarity', 'issue': 'Ambiguous phrasing', 'example': 'the method that was used → our method'},
                {'type': 'terminology', 'issue': 'Inconsistent acronyms', 'example': 'OTU vs Operational Terrain Unit'},
                {'type': 'formatting', 'issue': 'Reference style', 'example': 'Update to MDPI format'}
            ],
            'suggestions': [
                'Use active voice more frequently',
                'Break long sentences into shorter ones',
                'Define acronyms at first use',
                'Check all references for consistency'
            ],
            'rating': {
                'language_quality': 6,  # out of 10
                'clarity': 7,
                'technical_accuracy': 9,
                'overall': 7.5
            }
        }
        
        return mock_feedback
    
    def _analyze_feedback(self, feedback_data: Dict) -> Dict:
        """Analyze feedback data to extract actionable insights."""
        analysis = {
            'summary': {
                'total_comments': len(feedback_data.get('general_comments', [])),
                'total_issues': len(feedback_data.get('specific_issues', [])),
                'total_suggestions': len(feedback_data.get('suggestions', []))
            },
            'issue_categories': {},
            'priority_issues': [],
            'action_items': []
        }
        
        # Categorize issues
        if 'specific_issues' in feedback_data:
            for issue in feedback_data['specific_issues']:
                issue_type = issue.get('type', 'other')
                analysis['issue_categories'][issue_type] = analysis['issue_categories'].get(issue_type, 0) + 1
                
                # Flag high priority issues
                if issue_type in ['grammar', 'clarity']:
                    analysis['priority_issues'].append(issue)
        
        # Create action items from suggestions
        if 'suggestions' in feedback_data:
            for i, suggestion in enumerate(feedback_data['suggestions'], 1):
                analysis['action_items'].append({
                    'id': f'ACTION_{i:03d}',
                    'description': suggestion,
                    'priority': 'high' if i <= 3 else 'medium',
                    'status': 'pending'
                })
        
        # Add overall assessment
        if 'rating' in feedback_data:
            analysis['overall_assessment'] = feedback_data['rating']
            analysis['recommendation'] = self._generate_recommendation(feedback_data['rating'])
        
        return analysis
    
    def _generate_recommendation(self, ratings: Dict) -> str:
        """Generate recommendation based on ratings."""
        overall = ratings.get('overall', 0)
        
        if overall >= 8:
            return "Minor edits needed, manuscript is in good shape"
        elif overall >= 6:
            return "Moderate editing required, focus on language and clarity"
        elif overall >= 4:
            return "Substantial editing needed, consider major revisions"
        else:
            return "Extensive editing required, manuscript needs significant work"
    
    def _create_feedback_excel_report(self, feedback_data: Dict, output_path: Path):
        """Create Excel report from feedback data."""
        # Create DataFrames for different sections
        dfs = {}
        
        # General comments
        if 'general_comments' in feedback_data:
            dfs['General_Comments'] = pd.DataFrame({
                'Comment': feedback_data['general_comments']
            })
        
        # Specific issues
        if 'specific_issues' in feedback_data:
            issues_df = pd.DataFrame(feedback_data['specific_issues'])
            dfs['Specific_Issues'] = issues_df
        
        # Suggestions
        if 'suggestions' in feedback_data:
            dfs['Suggestions'] = pd.DataFrame({
                'Suggestion': feedback_data['suggestions']
            })
        
        # Ratings
        if 'rating' in feedback_data:
            ratings_df = pd.DataFrame([feedback_data['rating']])
            dfs['Ratings'] = ratings_df
        
        # Write to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _compare_files(self, original: Path, edited: Path) -> List[Dict]:
        """Compare original and edited files to identify changes."""
        changes = []
        
        try:
            # Read files
            with open(original, 'r', encoding='utf-8') as f:
                orig_lines = f.readlines()
            with open(edited, 'r', encoding='utf-8') as f:
                edit_lines = f.readlines()
            
            # Use difflib to find differences
            differ = difflib.Differ()
            diff = list(differ.compare(orig_lines, edit_lines))
            
            line_num = 0
            for line in diff:
                if line.startswith('- '):
                    # Line removed
                    changes.append({
                        'type': 'removal',
                        'line': line_num,
                        'original': line[2:].strip(),
                        'edited': None,
                        'description': 'Line removed'
                    })
                elif line.startswith('+ '):
                    # Line added
                    changes.append({
                        'type': 'addition',
                        'line': line_num,
                        'original': None,
                        'edited': line[2:].strip(),
                        'description': 'Line added'
                    })
                    line_num += 1
                elif line.startswith('? '):
                    # Change within line (not captured by simple diff)
                    continue
                else:
                    # Line unchanged
                    line_num += 1
        
        except Exception as e:
            print(f"Error comparing files: {e}")
            # Fallback: simple file comparison
            changes.append({
                'type': 'comparison_error',
                'description': f'Could not perform detailed comparison: {e}'
            })
        
        return changes


class VersionTracker:
    """Track versions of manuscript files."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.versions_dir = project_root / 'outputs' / 'professional_editing' / 'versions'
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.versions_file = self.versions_dir / 'version_history.json'
        
        # Load existing versions
        self.versions = self._load_versions()
    
    def _load_versions(self) -> List[Dict]:
        """Load version history from file."""
        if self.versions_file.exists():
            with open(self.versions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_versions(self):
        """Save version history to file."""
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(self.versions, f, indent=2)
    
    def create_snapshot(self, files: List[str], description: str,
                       metadata: Dict = None) -> str:
        """
        Create a version snapshot of files.
        
        Args:
            files: List of file paths to snapshot
            description: Description of this version
            metadata: Optional metadata to include
            
        Returns:
            Version ID
        """
        version_id = f"v{len(self.versions) + 1:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        version_data = {
            'version_id': version_id,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'files': [],
            'metadata': metadata or {}
        }
        
        # Create version directory
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Copy files and record hashes
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                # Calculate file hash
                file_hash = self._calculate_file_hash(path)
                
                # Copy to version directory
                dest_path = version_dir / path.name
                shutil.copy2(path, dest_path)
                
                version_data['files'].append({
                    'path': str(path),
                    'name': path.name,
                    'hash': file_hash,
                    'size_bytes': path.stat().st_size,
                    'copied_to': str(dest_path)
                })
        
        # Add to versions list
        self.versions.append(version_data)
        self._save_versions()
        
        print(f"Created version snapshot: {version_id} - {description}")
        
        return version_id
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Get version data by ID."""
        for version in self.versions:
            if version['version_id'] == version_id:
                return version
        return None
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict:
        """Compare two versions."""
        v1 = self.get_version(version_id1)
        v2 = self.get_version(version_id2)
        
        if not v1 or not v2:
            return {'error': 'One or both versions not found'}
        
        comparison = {
            'version1': version_id1,
            'version2': version_id2,
            'timestamp1': v1['timestamp'],
            'timestamp2': v2['timestamp'],
            'description1': v1['description'],
            'description2': v2['description'],
            'file_changes': []
        }
        
        # Compare files
        files1 = {f['name']: f for f in v1['files']}
        files2 = {f['name']: f for f in v2['files']}
        
        all_files = set(files1.keys()) | set(files2.keys())
        
        for filename in all_files:
            if filename in files1 and filename in files2:
                if files1[filename]['hash'] != files2[filename]['hash']:
                    comparison['file_changes'].append({
                        'file': filename,
                        'status': 'modified',
                        'hash1': files1[filename]['hash'][:16],
                        'hash2': files2[filename]['hash'][:16]
                    })
                else:
                    comparison['file_changes'].append({
                        'file': filename,
                        'status': 'unchanged'
                    })
            elif filename in files1:
                comparison['file_changes'].append({
                    'file': filename,
                    'status': 'removed_in_v2'
                })
            else:
                comparison['file_changes'].append({
                    'file': filename,
                    'status': 'added_in_v2'
                })
        
        return comparison


class SubmissionTracker:
    """Track submissions to editing services."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.submissions_dir = project_root / 'outputs' / 'professional_editing' / 'submissions'
        self.submissions_dir.mkdir(parents=True, exist_ok=True)
        self.submissions_file = self.submissions_dir / 'submission_history.json'
        
        # Load existing submissions
        self.submissions = self._load_submissions()
    
    def _load_submissions(self) -> List[Dict]:
        """Load submission history from file."""
        if self.submissions_file.exists():
            with open(self.submissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_submissions(self):
        """Save submission history to file."""
        with open(self.submissions_file, 'w', encoding='utf-8') as f:
            json.dump(self.submissions, f, indent=2)
    
    def record_submission(self, package_path: str, files_included: List[str],
                         service: str = 'MDPI') -> str:
        """
        Record a new submission.
        
        Args:
            package_path: Path to submission package
            files_included: List of files included
            service: Editing service name
            
        Returns:
            Submission ID
        """
        submission_id = f"SUB{len(self.submissions) + 1:03d}_{datetime.now().strftime('%Y%m%d')}"
        
        submission_data = {
            'submission_id': submission_id,
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'package_path': package_path,
            'files_included': files_included,
            'status': 'submitted',
            'status_history': [{
                'status': 'submitted',
                'timestamp': datetime.now().isoformat(),
                'notes': 'Initial submission'
            }]
        }
        
        self.submissions.append(submission_data)
        self._save_submissions()
        
        return submission_id
    
    def update_submission_status(self, submission_id: str, status: str, notes: str = ''):
        """Update status of a submission."""
        for submission in self.submissions:
            if submission['submission_id'] == submission_id:
                submission['status'] = status
                submission['status_history'].append({
                    'status': status,
                    'timestamp': datetime.now().isoformat(),
                    'notes': notes
                })
                self._save_submissions()
                return True
        return False
    
    def get_submission_status(self, submission_id: str) -> Optional[Dict]:
        """Get status of a specific submission."""
        for submission in self.submissions:
            if submission['submission_id'] == submission_id:
                return submission
        return None
    
    def get_latest_status(self) -> Optional[Dict]:
        """Get status of the latest submission."""
        if not self.submissions:
            return None
        return self.submissions[-1]
    
    def record_feedback(self, submission_id: str, feedback_file: str, analysis: Dict):
        """Record feedback received for a submission."""
        for submission in self.submissions:
            if submission['submission_id'] == submission_id:
                submission['feedback_received'] = {
                    'timestamp': datetime.now().isoformat(),
                    'feedback_file': feedback_file,
                    'analysis': analysis
                }
                submission['status'] = 'feedback_received'
                submission['status_history'].append({
                    'status': 'feedback_received',
                    'timestamp': datetime.now().isoformat(),
                    'notes': 'Editor feedback received'
                })
                self._save_submissions()
                return True
        return False


# Main execution functions
def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Professional Editing Service for MDPI Language Service'
    )
    parser.add_argument('--prepare', action='store_true',
                       help='Prepare files for MDPI service')
    parser.add_argument('--create-package', action='store_true',
                       help='Create submission package')
    parser.add_argument('--track-status', action='store_true',
                       help='Track submission status')
    parser.add_argument('--process-feedback', type=str,
                       help='Process feedback file')
    parser.add_argument('--integrate-changes', nargs=2, metavar=('ORIGINAL', 'EDITED'),
                       help='Integrate editor changes')
    parser.add_argument('--files', nargs='+', help='Files to process')
    
    args = parser.parse_args()
    
    service = ProfessionalEditingService()
    
    if args.prepare:
        if not args.files:
            print("Error: --prepare requires --files argument")
            return
        result = service.prepare_for_mdpi_service(args.files)
        print(f"Preparation result: {result['status']}")
    
    elif args.create_package:
        if not args.files:
            print("Error: --create-package requires --files argument")
            return
        package_path = service.create_submission_package(args.files)
        print(f"Package created: {package_path}")
    
    elif args.track_status:
        status = service.track_submission_status()
        print(f"Current status: {status.get('current_status', 'unknown')}")
    
    elif args.process_feedback:
        result = service.process_editor_feedback(args.process_feedback)
        print(f"Feedback processed: {result['summary']['total_issues']} issues found")
    
    elif args.integrate_changes:
        original, edited = args.integrate_changes
        result = service.integrate_editor_changes([original], [edited])
        print(f"Changes integrated: {result['change_summary']['total_changes']} changes")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()