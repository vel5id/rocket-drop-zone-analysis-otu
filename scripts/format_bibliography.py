#!/usr/bin/env python3
"""
Bibliography Formatting Script for Task 4.4
References: IMPLEMENTATION_ROADMAP.md lines 554-602

This script processes bibliography files, fetches metadata from Crossref API,
formats references according to MDPI Aerospace style, and generates reports.

Functions:
- fetch_doi_metadata(doi): Fetch metadata from Crossref API
- format_reference_mdpi(metadata): Format reference according to MDPI Aerospace style
- process_bibliography(bib_file): Process bibliography file and generate outputs
"""

import requests
import bibtexparser
import pandas as pd
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/bibliography/bibliography_formatting.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def fetch_doi_metadata(doi: str) -> Optional[Dict[str, Any]]:
    """
    Fetch metadata from Crossref API for a given DOI.
    
    Args:
        doi: Digital Object Identifier (e.g., '10.1016/j.jaero.2020.04.015')
    
    Returns:
        Dictionary containing metadata or None if fetch fails.
    
    References: IMPLEMENTATION_ROADMAP.md line 568-574
    """
    # Clean DOI
    doi = doi.strip()
    if not doi.startswith('10.'):
        logger.warning(f"DOI '{doi}' does not start with '10.' - may be invalid")
    
    url = f"https://api.crossref.org/works/{doi}"
    
    try:
        logger.info(f"Fetching metadata for DOI: {doi}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()['message']
            logger.info(f"Successfully fetched metadata for DOI: {doi}")
            return data
        elif response.status_code == 404:
            logger.warning(f"DOI not found: {doi}")
            return None
        else:
            logger.error(f"Crossref API error {response.status_code} for DOI: {doi}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching DOI: {doi}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching DOI: {doi}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching DOI {doi}: {str(e)}")
        return None


def format_author_name(author: Dict[str, str]) -> str:
    """
    Format individual author name in MDPI style: Last, F.
    
    Args:
        author: Dictionary with 'given' and 'family' keys
    
    Returns:
        Formatted author name (e.g., "Smith, J.")
    """
    if 'family' not in author:
        return author.get('name', 'Unknown')
    
    family = author['family']
    given = author.get('given', '')
    
    if given:
        # Take first initial
        initials = ''.join([part[0] for part in given.split() if part])
        return f"{family}, {initials}."
    else:
        return family


def format_authors_list(authors: List[Dict[str, str]]) -> str:
    """
    Format list of authors in MDPI style: Author1, A.; Author2, B.
    
    Args:
        authors: List of author dictionaries
    
    Returns:
        Formatted authors string
    """
    if not authors:
        return "Unknown"
    
    formatted_authors = []
    for author in authors:
        formatted_authors.append(format_author_name(author))
    
    # Join with semicolons
    return "; ".join(formatted_authors)


def format_reference_mdpi(metadata: Dict[str, Any]) -> Optional[str]:
    """
    Format reference according to MDPI Aerospace style.
    
    Format: Author1, A.; Author2, B. Title. Journal Year, Volume, Pages.
    
    Args:
        metadata: Crossref metadata dictionary
    
    Returns:
        Formatted reference string or None if insufficient data.
    
    References: IMPLEMENTATION_ROADMAP.md line 576-580
    """
    try:
        # Extract authors
        authors = metadata.get('author', [])
        authors_str = format_authors_list(authors)
        
        # Extract title
        title = metadata.get('title', [''])[0]
        # Remove trailing period if present
        title = title.rstrip('.')
        
        # Extract journal
        container_title = metadata.get('container-title', [''])[0]
        if not container_title:
            container_title = metadata.get('short-container-title', [''])[0]
        
        # Extract year
        published_date = metadata.get('published', {}).get('date-parts', [[None]])[0]
        year = str(published_date[0]) if published_date and published_date[0] else metadata.get('year', '')
        
        # Extract volume
        volume = metadata.get('volume', '')
        
        # Extract pages
        page = metadata.get('page', '')
        
        # Extract DOI
        doi = metadata.get('DOI', '')
        
        # Validate required fields
        if not all([authors_str, title, container_title, year]):
            logger.warning(f"Insufficient metadata for formatting: authors={bool(authors_str)}, title={bool(title)}, journal={bool(container_title)}, year={bool(year)}")
            return None
        
        # Build MDPI format
        # Format: Author1, A.; Author2, B. Title. Journal Year, Volume, Pages.
        parts = [authors_str, f"{title}.", f"{container_title} {year}"]
        
        if volume:
            parts.append(f"Volume {volume}")
        
        if page:
            parts.append(f"Pages {page}")
        
        formatted_ref = " ".join(parts)
        
        # Add DOI if available
        if doi:
            formatted_ref += f" doi:{doi}"
        
        return formatted_ref
        
    except Exception as e:
        logger.error(f"Error formatting reference: {str(e)}")
        return None


def validate_doi(doi: str) -> bool:
    """
    Validate DOI format.
    
    Args:
        doi: Digital Object Identifier
    
    Returns:
        True if DOI appears valid, False otherwise
    """
    if not doi:
        return False
    
    # Basic DOI pattern: 10.xxxx/xxxx
    doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
    return bool(re.match(doi_pattern, doi, re.IGNORECASE))


def process_bibliography(bib_file: str) -> Dict[str, Any]:
    """
    Process bibliography file and generate formatted references and reports.
    
    Args:
        bib_file: Path to .bib file
    
    Returns:
        Dictionary with processing results
    
    References: IMPLEMENTATION_ROADMAP.md line 582-596
    """
    # Create output directory
    output_dir = Path('outputs/bibliography')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize results
    results = {
        'total_entries': 0,
        'entries_with_doi': 0,
        'successfully_formatted': 0,
        'failed_fetch': 0,
        'failed_format': 0,
        'formatted_references': [],
        'missing_metadata': [],
        'validation_report': []
    }
    
    try:
        # Read .bib file
        logger.info(f"Processing bibliography file: {bib_file}")
        with open(bib_file, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)
        
        results['total_entries'] = len(bib_database.entries)
        logger.info(f"Found {results['total_entries']} entries in bibliography")
        
        # Process each entry
        for i, entry in enumerate(bib_database.entries):
            entry_id = entry.get('ID', f'entry_{i+1}')
            doi = entry.get('doi', '')
            
            # Validate DOI
            if doi:
                results['entries_with_doi'] += 1
                is_valid = validate_doi(doi)
                
                validation_record = {
                    'Entry ID': entry_id,
                    'DOI': doi,
                    'Valid Format': is_valid,
                    'Has Metadata': False,
                    'Formatted': False,
                    'Error': ''
                }
                
                if not is_valid:
                    validation_record['Error'] = 'Invalid DOI format'
                    results['validation_report'].append(validation_record)
                    results['failed_fetch'] += 1
                    continue
                
                # Fetch metadata
                metadata = fetch_doi_metadata(doi)
                
                if metadata:
                    validation_record['Has Metadata'] = True
                    
                    # Format reference
                    formatted = format_reference_mdpi(metadata)
                    
                    if formatted:
                        validation_record['Formatted'] = True
                        results['successfully_formatted'] += 1
                        
                        # Add to formatted references
                        bib_entry = {
                            'original_id': entry_id,
                            'doi': doi,
                            'formatted_reference': formatted,
                            'metadata': {
                                'title': metadata.get('title', [''])[0],
                                'authors': len(metadata.get('author', [])),
                                'year': metadata.get('published', {}).get('date-parts', [[None]])[0][0] if metadata.get('published', {}).get('date-parts') else None,
                                'journal': metadata.get('container-title', [''])[0]
                            }
                        }
                        results['formatted_references'].append(bib_entry)
                        
                        logger.info(f"Successfully formatted entry {entry_id}")
                    else:
                        validation_record['Error'] = 'Formatting failed'
                        results['failed_format'] += 1
                        results['missing_metadata'].append({
                            'Entry ID': entry_id,
                            'DOI': doi,
                            'Missing Fields': 'Could not extract required fields',
                            'Available Fields': list(metadata.keys()) if metadata else []
                        })
                else:
                    validation_record['Error'] = 'Metadata fetch failed'
                    results['failed_fetch'] += 1
                    results['missing_metadata'].append({
                        'Entry ID': entry_id,
                        'DOI': doi,
                        'Missing Fields': 'No metadata from Crossref',
                        'Available Fields': []
                    })
                
                results['validation_report'].append(validation_record)
                
                # Rate limiting to be polite to Crossref API
                time.sleep(0.1)
            else:
                # Entry without DOI
                results['missing_metadata'].append({
                    'Entry ID': entry_id,
                    'DOI': '',
                    'Missing Fields': 'No DOI provided',
                    'Available Fields': list(entry.keys())
                })
                logger.warning(f"Entry {entry_id} has no DOI")
        
        # Generate output files
        generate_output_files(results, output_dir)
        
        logger.info(f"Processing complete. Successfully formatted: {results['successfully_formatted']}/{results['entries_with_doi']}")
        return results
        
    except Exception as e:
        logger.error(f"Error processing bibliography: {str(e)}")
        raise


def generate_output_files(results: Dict[str, Any], output_dir: Path) -> None:
    """
    Generate all output files: formatted references, missing metadata report,
    and DOI validation report.
    """
    # 1. Formatted references (.bib file)
    formatted_refs = []
    for ref in results['formatted_references']:
        # Create BibTeX entry with formatted reference
        bib_entry = f"""@article{{{ref['original_id']}_formatted,
  author = {{{ref['metadata']['authors']} authors}},
  title = {{{ref['metadata']['title']}}},
  journal = {{{ref['metadata']['journal']}}},
  year = {{{ref['metadata']['year']}}},
  doi = {{{ref['doi']}}},
  note = {{Formatted according to MDPI Aerospace style: {ref['formatted_reference']}}}
}}"""
        formatted_refs.append(bib_entry)
    
    formatted_bib_path = output_dir / 'formatted_references.bib'
    with open(formatted_bib_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(formatted_refs))
    logger.info(f"Formatted references saved to: {formatted_bib_path}")
    
    # 2. Missing metadata report (Excel)
    if results['missing_metadata']:
        missing_df = pd.DataFrame(results['missing_metadata'])
        missing_report_path = output_dir / 'Missing_Metadata_Report.xlsx'
        missing_df.to_excel(missing_report_path, index=False)
        logger.info(f"Missing metadata report saved to: {missing_report_path}")
    else:
        # Create empty report
        empty_df = pd.DataFrame(columns=['Entry ID', 'DOI', 'Missing Fields', 'Available Fields'])
        missing_report_path = output_dir / 'Missing_Metadata_Report.xlsx'
        empty_df.to_excel(missing_report_path, index=False)
        logger.info(f"Empty missing metadata report saved to: {missing_report_path}")
    
    # 3. DOI validation report (text file)
    validation_df = pd.DataFrame(results['validation_report'])
    validation_report_path = output_dir / 'DOI_Validation_Report.txt'
    
    with open(validation_report_path, 'w', encoding='utf-8') as f:
        f.write("DOI VALIDATION REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total entries: {results['total_entries']}\n")
        f.write(f"Entries with DOI: {results['entries_with_doi']}\n")
        f.write(f"Successfully formatted: {results['successfully_formatted']}\n")
        f.write(f"Failed fetch: {results['failed_fetch']}\n")
        f.write(f"Failed format: {results['failed_format']}\n")
        f.write("\n" + "=" * 50 + "\n\n")
        
        if not validation_df.empty:
            f.write("DETAILED VALIDATION RESULTS:\n")
            f.write("-" * 50 + "\n")
            for _, row in validation_df.iterrows():
                f.write(f"Entry ID: {row['Entry ID']}\n")
                f.write(f"DOI: {row['DOI']}\n")
                f.write(f"Valid Format: {row['Valid Format']}\n")
                f.write(f"Has Metadata: {row['Has Metadata']}\n")
                f.write(f"Formatted: {row['Formatted']}\n")
                if row['Error']:
                    f.write(f"Error: {row['Error']}\n")
                f.write("-" * 30 + "\n")
        else:
            f.write("No DOI validation data available.\n")
    
    logger.info(f"DOI validation report saved to: {validation_report_path}")
    
    # 4. Summary report (additional)
    summary_path = output_dir / 'Bibliography_Formatting_Summary.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Bibliography Formatting Summary\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Statistics\n")
        f.write(f"- Total bibliography entries: {results['total_entries']}\n")
        f.write(f"- Entries with DOI: {results['entries_with_doi']}\n")
        f.write(f"- Successfully formatted: {results['successfully_formatted']}\n")
        f.write(f"- Failed to fetch metadata: {results['failed_fetch']}\n")
        f.write(f"- Failed to format: {results['failed_format']}\n")
        f.write(f"- Success rate: {results['successfully_formatted']/max(results['entries_with_doi'], 1)*100:.1f}%\n\n")
        f.write("## Output Files\n")
        f.write(f"- `{formatted_bib_path}`: Formatted references in BibTeX format\n")
        f.write(f"- `{missing_report_path}`: Missing metadata report (Excel)\n")
        f.write(f"- `{validation_report_path}`: DOI validation report (text)\n")
        f.write(f"- `{output_dir / 'bibliography_formatting.log'}`: Processing log\n")
    
    logger.info(f"Summary report saved to: {summary_path}")


def main():
    """Main function to run bibliography formatting."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Format bibliography references according to MDPI Aerospace style'
    )
    parser.add_argument(
        '--input', '-i',
        default='data/bibliography/test_references.bib',
        help='Path to input .bib file (default: data/bibliography/test_references.bib)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='outputs/bibliography',
        help='Output directory (default: outputs/bibliography)'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        logger.info("Creating sample bibliography file...")
        # Create sample if doesn't exist
        sample_bib = Path('data/bibliography/test_references.bib')
        sample_bib.parent.mkdir(parents=True, exist_ok=True)
        sample_bib.write_text("""@article{sample,
  author = {Sample Author},
  title = {Sample Title},
  journal = {Sample Journal},
  year = {2023},
  doi = {10.1234/sample.2023.123456}
}""")
        args.input = str(sample_bib)
    
    # Process bibliography
    try:
        results = process_bibliography(args.input)
        
        # Print summary
        print("\n" + "="*60)
        print("BIBLIOGRAPHY FORMATTING COMPLETE")
        print("="*60)
        print(f"Total entries processed: {results['total_entries']}")
        print(f"Entries with DOI: {results['entries_with_doi']}")
        print(f"Successfully formatted: {results['successfully_formatted']}")
        print(f"Failed to fetch metadata: {results['failed_fetch']}")
        print(f"Failed to format: {results['failed_format']}")
        print(f"Success rate: {results['successfully_formatted']/max(results['entries_with_doi'], 1)*100:.1f}%")
        print("\nOutput files generated in outputs/bibliography/")
        print("  - formatted_references.bib")
        print("  - Missing_Metadata_Report.xlsx")
        print("  - DOI_Validation_Report.txt")
        print("  - Bibliography_Formatting_Summary.md")
        print("  - bibliography_formatting.log")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print(f"\nERROR: {str(e)}")
        print("Check log file for details: outputs/bibliography/bibliography_formatting.log")
        return 1


if __name__ == '__main__':
    sys.exit(main())