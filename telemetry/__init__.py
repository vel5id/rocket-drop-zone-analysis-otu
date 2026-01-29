"""
Telemetry module for scientific reproducibility and versioning.

Provides functionality to:
1. Generate unique Analysis IDs
2. Save simulation configurations with dates
3. Export full data packages for archival
4. Track version history

Implements FUNC-4 from spec.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib


class TelemetryRecorder:
    """Records simulation metadata for reproducibility."""
    
    def __init__(self, base_dir: Path = Path("telemetry")):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_analysis_id(self, config: Dict[str, Any]) -> str:
        """
        Generate a unique Analysis ID based on configuration hash.
        
        Args:
            config: Simulation configuration dictionary
            
        Returns:
            Unique Analysis ID string (format: ANALYSIS-{date}-{hash})
        """
        # Create a deterministic hash of the configuration
        config_str = json.dumps(config, sort_keys=True, default=str)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:8]
        
        # Include date for readability
        date_str = datetime.now().strftime("%Y%m%d")
        
        return f"ANALYSIS-{date_str}-{config_hash}"
    
    def save_configuration(self, config: Dict[str, Any], analysis_id: Optional[str] = None) -> str:
        """
        Save simulation configuration to telemetry storage.
        
        Args:
            config: Simulation configuration dictionary
            analysis_id: Optional Analysis ID; will be generated if not provided
            
        Returns:
            Analysis ID used
        """
        if analysis_id is None:
            analysis_id = self.generate_analysis_id(config)
        
        # Create analysis directory
        analysis_dir = self.base_dir / analysis_id
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration as JSON
        config_path = analysis_dir / "configuration.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "config": config
            }, f, indent=2, default=str)
        
        # Save a simplified version for quick reference
        summary_path = analysis_dir / "summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(self._format_config_summary(config, analysis_id))
        
        return analysis_id
    
    def _format_config_summary(self, config: Dict[str, Any], analysis_id: str) -> str:
        """Format configuration as human-readable summary."""
        lines = [
            f"Analysis ID: {analysis_id}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 50,
            "SIMULATION CONFIGURATION",
            "=" * 50,
        ]
        
        # Date parameters
        date_params = ["target_date", "start_date", "end_date"]
        for param in date_params:
            if param in config:
                lines.append(f"{param}: {config[param]}")
        
        # Simulation parameters
        sim_params = ["iterations", "use_gpu", "launch_lat", "launch_lon", "azimuth"]
        for param in sim_params:
            if param in config:
                lines.append(f"{param}: {config[param]}")
        
        # Separation parameters
        sep_params = ["sep_altitude", "sep_velocity", "sep_fp_angle", "sep_azimuth"]
        for param in sep_params:
            if param in config:
                lines.append(f"{param}: {config[param]}")
        
        lines.append("=" * 50)
        return "\n".join(lines)
    
    def export_data_package(self, analysis_id: str, 
                           result_data: Optional[Dict[str, Any]] = None,
                           include_tables: bool = True) -> Path:
        """
        Export complete data package for archival.
        
        Args:
            analysis_id: Analysis ID to export
            result_data: Optional simulation results to include
            include_tables: Whether to include generated tables
            
        Returns:
            Path to exported package directory
        """
        analysis_dir = self.base_dir / analysis_id
        if not analysis_dir.exists():
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # Create export directory
        export_dir = analysis_dir / "export"
        export_dir.mkdir(exist_ok=True)
        
        # Copy configuration
        import shutil
        config_src = analysis_dir / "configuration.json"
        config_dst = export_dir / "configuration.json"
        shutil.copy2(config_src, config_dst)
        
        # Save results if provided
        if result_data:
            results_path = export_dir / "simulation_results.json"
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, default=str)
        
        # Include generated tables if requested
        if include_tables:
            tables_src = Path("outputs/supplementary_tables")
            if tables_src.exists():
                tables_dst = export_dir / "tables"
                shutil.copytree(tables_src, tables_dst, dirs_exist_ok=True)
        
        # Create README
        readme_path = export_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_readme(analysis_id, result_data))
        
        # Create archive (optional)
        # For now, just return directory path
        
        return export_dir
    
    def _generate_readme(self, analysis_id: str, result_data: Optional[Dict]) -> str:
        """Generate README for exported package."""
        return f"""# Analysis Package: {analysis_id}

## Overview
This package contains all data and configuration for a rocket drop zone simulation
performed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

## Contents
- `configuration.json`: Complete simulation configuration
- `simulation_results.json`: Simulation results (if available)
- `tables/`: Generated supplementary tables (if available)

## Reproducibility
To reproduce this analysis:
1. Load configuration.json
2. Run simulation with the same parameters
3. Compare results with simulation_results.json

## Contact
For questions about this analysis, refer to the project documentation.
"""


# Singleton instance for easy import
_default_recorder = TelemetryRecorder()

def record_simulation(config: Dict[str, Any], 
                     result_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to record a simulation in telemetry.
    
    Args:
        config: Simulation configuration
        result_data: Optional simulation results
        
    Returns:
        Analysis ID
    """
    analysis_id = _default_recorder.save_configuration(config)
    
    if result_data:
        _default_recorder.export_data_package(analysis_id, result_data)
    
    return analysis_id

def get_analysis_dir(analysis_id: str) -> Path:
    """Get directory path for a given Analysis ID."""
    return _default_recorder.base_dir / analysis_id