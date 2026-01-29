"""
Task 2.5: Validation Framework Design

Implements БЛОК 2, Task 2.5 from revision plan.
Designs the validation framework for OTU methodology, including:
1. Data collection protocols
2. Validation metrics (correlation, kappa, ANOVA)
3. Success criteria (thresholds)
4. Implementation timeline
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import time
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'validation_framework_design.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ValidationMetricType(Enum):
    """Types of validation metrics."""
    CORRELATION = "correlation"
    CLASSIFICATION = "classification"
    STATISTICAL = "statistical"
    SPATIAL = "spatial"

@dataclass
class ValidationMetric:
    """Definition of a validation metric."""
    name: str
    type: ValidationMetricType
    description: str
    calculation: str
    interpretation: str
    success_threshold: float
    unit: str = ""

@dataclass
class DataCollectionProtocol:
    """Protocol for collecting validation data."""
    name: str
    data_type: str
    source: str
    collection_method: str
    frequency: str
    quality_controls: List[str]
    estimated_cost: str = ""
    time_required: str = ""

@dataclass
class SuccessCriterion:
    """Success criterion for validation."""
    metric_name: str
    threshold: float
    comparison: str  # ">=", "<=", "=="
    importance: str  # "critical", "important", "desirable"
    rationale: str

class ValidationFrameworkDesigner:
    """
    Designs validation framework for OTU methodology.
    """
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] ValidationFrameworkDesigner initialized")
        
        # Define output directories
        self.output_dir = Path("outputs/validation_framework")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_protocols = []
        self.validation_metrics = []
        self.success_criteria = []
        self.implementation_timeline = []
        
        logger.info("[INFO] Validation framework designer ready")
    
    def define_data_collection_protocols(self):
        """Define data collection protocols for validation."""
        logger.info("[DESIGN] Defining data collection protocols")
        
        protocols = [
            DataCollectionProtocol(
                name="Field Survey - Vegetation Assessment",
                data_type="Vegetation quality index (Q_VI)",
                source="Field measurements",
                collection_method="Quadrant sampling with species identification, NDVI ground truthing",
                frequency="Seasonal (Spring, Summer, Autumn)",
                quality_controls=[
                    "GPS accuracy check (±3m)",
                    "Duplicate measurements (10% of samples)",
                    "Photo documentation",
                    "Expert verification"
                ],
                estimated_cost="500-1000 KZT per sample",
                time_required="2-3 weeks per season"
            ),
            DataCollectionProtocol(
                name="Soil Sampling and Laboratory Analysis",
                data_type="Soil quality index (Q_SI)",
                source="Field sampling + lab analysis",
                collection_method="Soil cores (0-30cm depth), laboratory analysis for texture, pH, organic matter",
                frequency="Once per validation cycle",
                quality_controls=[
                    "Sterile sampling equipment",
                    "Chain of custody documentation",
                    "Laboratory QA/QC protocols",
                    "Reference samples"
                ],
                estimated_cost="2000-5000 KZT per sample",
                time_required="4-6 weeks for full analysis"
            ),
            DataCollectionProtocol(
                name="Biodiversity Assessment",
                data_type="Biodiversity index (Q_BI)",
                source="Field observations + camera traps",
                collection_method="Species richness counts, camera trap deployment (2 weeks)",
                frequency="Seasonal",
                quality_controls=[
                    "Expert taxonomist verification",
                    "Standardized observation protocols",
                    "Camera trap calibration",
                    "Data validation against regional databases"
                ],
                estimated_cost="1000-3000 KZT per site",
                time_required="3-4 weeks per season"
            ),
            DataCollectionProtocol(
                name="Topographic Survey",
                data_type="Relief index (Q_Relief)",
                source="LiDAR/DEM + field validation",
                collection_method="RTK GPS survey of slope and aspect, cross-validation with DEM",
                frequency="Once (static parameter)",
                quality_controls=[
                    "RTK GPS accuracy (±2cm horizontal, ±5cm vertical)",
                    "Cross-validation with satellite DEM",
                    "Multiple measurement points per OTU"
                ],
                estimated_cost="500-1500 KZT per OTU",
                time_required="1-2 weeks"
            ),
            DataCollectionProtocol(
                name="Historical Impact Assessment",
                data_type="Ground truth for OTU stability",
                source="Historical records + expert assessment",
                collection_method="Analysis of historical rocket stage impacts, erosion patterns, vegetation recovery",
                frequency="Retrospective analysis",
                quality_controls=[
                    "Multiple source verification",
                    "Expert consensus (≥3 experts)",
                    "Photo documentation analysis",
                    "Cross-reference with satellite time series"
                ],
                estimated_cost="Expert time only",
                time_required="2-3 weeks"
            )
        ]
        
        self.data_protocols = protocols
        logger.info(f"[OK] Defined {len(protocols)} data collection protocols")
        return protocols
    
    def define_validation_metrics(self):
        """Define validation metrics for OTU methodology."""
        logger.info("[DESIGN] Defining validation metrics")
        
        metrics = [
            ValidationMetric(
                name="Pearson Correlation Coefficient",
                type=ValidationMetricType.CORRELATION,
                description="Linear correlation between predicted Q_OTU and field-measured values",
                calculation="r = Σ[(x_i - x̄)(y_i - ȳ)] / √[Σ(x_i - x̄)² Σ(y_i - ȳ)²]",
                interpretation="Strength and direction of linear relationship",
                success_threshold=0.70,
                unit="dimensionless"
            ),
            ValidationMetric(
                name="Spearman Rank Correlation",
                type=ValidationMetricType.CORRELATION,
                description="Monotonic relationship between predicted and observed ranks",
                calculation="ρ = 1 - [6Σd_i² / n(n²-1)] where d_i = rank(x_i) - rank(y_i)",
                interpretation="Strength of monotonic relationship (robust to outliers)",
                success_threshold=0.65,
                unit="dimensionless"
            ),
            ValidationMetric(
                name="Cohen's Kappa Coefficient",
                type=ValidationMetricType.CLASSIFICATION,
                description="Agreement between predicted and observed stability classes",
                calculation="κ = (p_o - p_e) / (1 - p_e) where p_o = observed agreement, p_e = expected agreement",
                interpretation="Agreement beyond chance: <0 = poor, 0-0.2 = slight, 0.21-0.4 = fair, 0.41-0.6 = moderate, 0.61-0.8 = substantial, 0.81-1 = almost perfect",
                success_threshold=0.60,
                unit="dimensionless"
            ),
            ValidationMetric(
                name="Root Mean Square Error (RMSE)",
                type=ValidationMetricType.STATISTICAL,
                description="Average magnitude of prediction errors",
                calculation="RMSE = √[Σ(y_i - ŷ_i)² / n]",
                interpretation="Standard deviation of prediction errors (lower is better)",
                success_threshold=0.15,
                unit="Q_OTU units (0-1)"
            ),
            ValidationMetric(
                name="Mean Absolute Error (MAE)",
                type=ValidationMetricType.STATISTICAL,
                description="Average absolute difference between predictions and observations",
                calculation="MAE = Σ|y_i - ŷ_i| / n",
                interpretation="Average error magnitude (lower is better)",
                success_threshold=0.12,
                unit="Q_OTU units (0-1)"
            ),
            ValidationMetric(
                name="R-squared (Coefficient of Determination)",
                type=ValidationMetricType.STATISTICAL,
                description="Proportion of variance in observed values explained by predictions",
                calculation="R² = 1 - (SS_res / SS_tot)",
                interpretation="0-1, higher values indicate better explanatory power",
                success_threshold=0.50,
                unit="dimensionless"
            ),
            ValidationMetric(
                name="ANOVA F-statistic (Between-class variance)",
                type=ValidationMetricType.STATISTICAL,
                description="Tests whether stability classes have significantly different Q_OTU values",
                calculation="F = (between-group variance) / (within-group variance)",
                interpretation="Significant F (p < 0.05) indicates classes are distinguishable",
                success_threshold=4.0,  # Corresponds to p < 0.05 for typical sample sizes
                unit="dimensionless"
            ),
            ValidationMetric(
                name="Spatial Autocorrelation (Moran's I)",
                type=ValidationMetricType.SPATIAL,
                description="Tests spatial clustering of prediction errors",
                calculation="I = (n/Σw_ij) * [ΣΣw_ij(z_i - z̄)(z_j - z̄) / Σ(z_i - z̄)²]",
                interpretation="I ≈ 0: random spatial pattern, I > 0: clustering, I < 0: dispersion",
                success_threshold=0.20,  # Acceptable level of spatial autocorrelation
                unit="dimensionless"
            ),
            ValidationMetric(
                name="Bias (Mean Error)",
                type=ValidationMetricType.STATISTICAL,
                description="Systematic over- or under-prediction",
                calculation="Bias = Σ(y_i - ŷ_i) / n",
                interpretation="Positive: underestimation, Negative: overestimation",
                success_threshold=0.05,  # Absolute value
                unit="Q_OTU units (0-1)"
            ),
            ValidationMetric(
                name="Precision-Recall AUC (for binary classification)",
                type=ValidationMetricType.CLASSIFICATION,
                description="Area under precision-recall curve for high-risk vs low-risk classification",
                calculation="AUC = ∫ precision d(recall)",
                interpretation="0.5 = random, 1.0 = perfect classifier",
                success_threshold=0.75,
                unit="dimensionless"
            )
        ]
        
        self.validation_metrics = metrics
        logger.info(f"[OK] Defined {len(metrics)} validation metrics")
        return metrics
    
    def define_success_criteria(self):
        """Define success criteria for validation."""
        logger.info("[DESIGN] Defining success criteria")
        
        criteria = [
            SuccessCriterion(
                metric_name="Pearson Correlation Coefficient",
                threshold=0.70,
                comparison=">=",
                importance="critical",
                rationale="Strong linear relationship required for predictive validity"
            ),
            SuccessCriterion(
                metric_name="Cohen's Kappa Coefficient",
                threshold=0.60,
                comparison=">=",
                importance="critical",
                rationale="Substantial agreement needed for classification reliability"
            ),
            SuccessCriterion(
                metric_name="Root Mean Square Error (RMSE)",
                threshold=0.15,
                comparison="<=",
                importance="critical",
                rationale="Prediction errors should be less than 15% of scale"
            ),
            SuccessCriterion(
                metric_name="R-squared (Coefficient of Determination)",
                threshold=0.50,
                comparison=">=",
                importance="important",
                rationale="At least 50% of variance should be explained"
            ),
            SuccessCriterion(
                metric_name="Bias (Mean Error)",
                threshold=0.05,
                comparison="<=",  # Absolute value
                importance="important",
                rationale="Minimal systematic bias required for unbiased predictions"
            ),
            SuccessCriterion(
                metric_name="ANOVA F-statistic (Between-class variance)",
                threshold=4.0,
                comparison=">=",
                importance="important",
                rationale="Stability classes should be statistically distinguishable"
            ),
            SuccessCriterion(
                metric_name="Spearman Rank Correlation",
                threshold=0.65,
                comparison=">=",
                importance="desirable",
                rationale="Good monotonic relationship desirable for ranking consistency"
            ),
            SuccessCriterion(
                metric_name="Precision-Recall AUC",
                threshold=0.75,
                comparison=">=",
                importance="desirable",
                rationale="Good binary classification performance for risk assessment"
            ),
            SuccessCriterion(
                metric_name="Spatial Autocorrelation (Moran's I)",
                threshold=0.20,
                comparison="<=",  # Absolute value
                importance="desirable",
                rationale="Acceptable level of spatial clustering in errors"
            )
        ]
        
        self.success_criteria = criteria
        logger.info(f"[OK] Defined {len(criteria)} success criteria")
        return criteria
    
    def create_implementation_timeline(self):
        """Create implementation timeline for validation framework."""
        logger.info("[DESIGN] Creating implementation timeline")
        
        timeline = [
            {
                "phase": "Phase 1: Preparation (Weeks 1-4)",
                "activities": [
                    "Finalize validation protocol document",
                    "Obtain necessary permits and approvals",
                    "Recruit and train field team",
                    "Procure equipment and materials",
                    "Develop data collection forms and digital tools"
                ],
                "deliverables": [
                    "Validation Protocol v1.0",
                    "Trained field team (4-6 people)",
                    "Equipment ready for deployment",
                    "Ethical approvals secured"
                ],
                "responsible": "Project Manager + Field Coordinator"
            },
            {
                "phase": "Phase 2: Field Data Collection (Weeks 5-16)",
                "activities": [
                    "Conduct vegetation assessments (Spring season)",
                    "Collect soil samples",
                    "Deploy biodiversity monitoring",
                    "Perform topographic surveys",
                    "Collect historical impact data"
                ],
                "deliverables": [
                    "Vegetation quality dataset (n≥50)",
                    "Soil analysis results (n≥30)",
                    "Biodiversity observations (n≥40)",
                    "Topographic validation points (n≥100)",
                    "Historical impact database"
                ],
                "responsible": "Field Team + Data Manager"
            },
            {
                "phase": "Phase 3: Laboratory Analysis (Weeks 10-20)",
                "activities": [
                    "Process soil samples in laboratory",
                    "Analyze vegetation samples",
                    "Process camera trap data",
                    "Quality control checks"
                ],
                "deliverables": [
                    "Laboratory analysis reports",
                    "Processed biodiversity data",
                    "Quality-controlled datasets"
                ],
                "responsible": "Laboratory Technicians + Data Manager"
            },
            {
                "phase": "Phase 4: Data Analysis (Weeks 17-24)",
                "activities": [
                    "Compute validation metrics",
                    "Statistical analysis",
                    "Spatial analysis",
                    "Compare predictions vs observations"
                ],
                "deliverables": [
                    "Validation metrics report",
                    "Statistical significance tests",
                    "Error maps and visualizations",
                    "Preliminary validation conclusions"
                ],
                "responsible": "Statistical Analyst + GIS Specialist"
            },
            {
                "phase": "Phase 5: Reporting and Integration (Weeks 21-28)",
                "activities": [
                    "Prepare validation report",
                    "Integrate findings into manuscript",
                    "Update methodology based on results",
                    "Prepare supplementary materials"
                ],
                "deliverables": [
                    "Comprehensive Validation Report",
                    "Updated manuscript sections",
                    "Supplementary validation materials",
                    "Recommendations for methodology improvement"
                ],
                "responsible": "Lead Author + Validation Team"
            }
        ]
        
        self.implementation_timeline = timeline
        logger.info(f"[OK] Created implementation timeline with {len(timeline)} phases")
        return timeline
    
    def generate_validation_protocol_document(self):
        """Generate comprehensive validation protocol document."""
        logger.info("[DOCUMENT] Generating validation protocol document")
        
        protocol = {
            "title": "Validation Protocol for Optimal Take-off Unit (OTU) Methodology",
            "version": "1.0",
            "date": time.strftime("%Y-%m-%d"),
            "overview": "This document outlines the validation framework for assessing the accuracy and reliability of the OTU methodology for rocket stage impact zone analysis.",
            "objectives": [
                "Assess predictive accuracy of Q_OTU calculations",
                "Validate stability classification system",
                "Evaluate spatial prediction performance",
                "Identify systematic biases and limitations",
                "Provide evidence for methodological robustness"
            ],
            "data_collection_protocols": [vars(p) for p in self.data_protocols],
            "validation_metrics": [vars(m) for m in self.validation_metrics],
            "success_criteria": [vars(c) for c in self.success_criteria],
            "implementation_timeline": self.implementation_timeline,
            "sample_size_justification": {
                "vegetation_samples": "n≥50 (95% confidence, ±10% margin of error)",
                "soil_samples": "n≥30 (adequate for regional representation)",
                "biodiversity_sites": "n≥40 (stratified by vegetation type)",
                "topographic_points": "n≥100 (dense coverage for DEM validation)",
                "total_validation_otus": "20-30 OTUs (representing all stability classes)"
            },
            "quality_assurance": [
                "Standard Operating Procedures (SOPs) for all measurements",
                "Regular calibration of equipment",
                "Duplicate measurements (10% of samples)",
                "Blind data entry and verification",
                "Expert review of ambiguous cases"
            ],
            "data_management": {
                "storage": "Secure cloud storage with version control",
                "backup": "Daily automated backups to offsite location",
                "access_control": "Role-based access with audit trail",
                "metadata": "Comprehensive metadata following FAIR principles"
            },
            "ethical_considerations": [
                "Informed consent from landowners for field access",
                "Minimal environmental impact during sampling",
                "Data anonymization for sensitive locations",
                "Compliance with national environmental regulations"
            ],
            "risk_mitigation": [
                "Contingency plans for field team safety",
                "Alternative data sources if primary collection fails",
                "Quality control checkpoints throughout process",
                "Peer review of analysis results"
            ]
        }
        
        # Save protocol to JSON
        json_path = self.output_dir / "validation_protocol.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(protocol, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        self._generate_summary_report(protocol)
        
        logger.info(f"[OK] Validation protocol document generated: {json_path}")
        return protocol
    
    def _generate_summary_report(self, protocol: Dict):
        """Generate human-readable summary report."""
        report_path = self.output_dir / "validation_protocol_summary.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Validation Protocol Summary\n\n")
            f.write(f"**Title**: {protocol['title']}\n")
            f.write(f"**Version**: {protocol['version']}\n")
            f.write(f"**Date**: {protocol['date']}\n\n")
            
            f.write("## Objectives\n")
            for i, obj in enumerate(protocol['objectives'], 1):
                f.write(f"{i}. {obj}\n")
            f.write("\n")
            
            f.write("## Data Collection Protocols\n")
            f.write(f"Number of protocols: {len(protocol['data_collection_protocols'])}\n\n")
            
            f.write("## Validation Metrics\n")
            f.write(f"Number of metrics: {len(protocol['validation_metrics'])}\n")
            f.write("Key metrics:\n")
            for metric in protocol['validation_metrics'][:5]:  # Show first 5
                f.write(f"- {metric['name']} (threshold: {metric['success_threshold']})\n")
            f.write("\n")
            
            f.write("## Success Criteria\n")
            f.write(f"Number of criteria: {len(protocol['success_criteria'])}\n")
            critical = sum(1 for c in protocol['success_criteria'] if c['importance'] == 'critical')
            f.write(f"- Critical: {critical}\n")
            f.write(f"- Important: {sum(1 for c in protocol['success_criteria'] if c['importance'] == 'important')}\n")
            f.write(f"- Desirable: {sum(1 for c in protocol['success_criteria'] if c['importance'] == 'desirable')}\n\n")
            
            f.write("## Implementation Timeline\n")
            f.write(f"Phases: {len(protocol['implementation_timeline'])}\n")
            for phase in protocol['implementation_timeline']:
                f.write(f"- {phase['phase']}: {len(phase['activities'])} activities\n")
            f.write("\n")
            
            f.write("## Sample Size Justification\n")
            for key, value in protocol['sample_size_justification'].items():
                f.write(f"- {key}: {value}\n")
            f.write("\n")
            
            f.write("## Quality Assurance\n")
            for item in protocol['quality_assurance']:
                f.write(f"- {item}\n")
        
        logger.info(f"[OK] Summary report generated: {report_path}")
    
    def export_to_excel(self):
        """Export validation framework components to Excel workbook."""
        logger.info("[EXPORT] Exporting to Excel")
        
        excel_path = self.output_dir / "validation_framework.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Data collection protocols
            protocols_df = pd.DataFrame([vars(p) for p in self.data_protocols])
            protocols_df.to_excel(writer, sheet_name='Data Protocols', index=False)
            
            # Validation metrics
            metrics_df = pd.DataFrame([vars(m) for m in self.validation_metrics])
            metrics_df.to_excel(writer, sheet_name='Validation Metrics', index=False)
            
            # Success criteria
            criteria_df = pd.DataFrame([vars(c) for c in self.success_criteria])
            criteria_df.to_excel(writer, sheet_name='Success Criteria', index=False)
            
            # Implementation timeline (flattened)
            timeline_data = []
            for phase in self.implementation_timeline:
                for activity in phase['activities']:
                    timeline_data.append({
                        'Phase': phase['phase'],
                        'Activity': activity,
                        'Responsible': phase['responsible']
                    })
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df.to_excel(writer, sheet_name='Timeline', index=False)
        
        logger.info(f"[OK] Excel workbook exported: {excel_path}")
        return excel_path
    
    def run_full_design(self):
        """Execute full validation framework design process."""
        logger.info("[PROCESS] Starting full validation framework design")
        
        # Step 1: Define components
        self.define_data_collection_protocols()
        self.define_validation_metrics()
        self.define_success_criteria()
        self.create_implementation_timeline()
        
        # Step 2: Generate documents
        protocol = self.generate_validation_protocol_document()
        
        # Step 3: Export to Excel
        excel_path = self.export_to_excel()
        
        # Step 4: Calculate and log statistics
        elapsed = time.time() - self.start_time
        stats = {
            "data_protocols": len(self.data_protocols),
            "validation_metrics": len(self.validation_metrics),
            "success_criteria": len(self.success_criteria),
            "timeline_phases": len(self.implementation_timeline),
            "output_files": [
                str(self.output_dir / "validation_protocol.json"),
                str(self.output_dir / "validation_protocol_summary.md"),
                str(excel_path)
            ],
            "processing_time_seconds": round(elapsed, 2)
        }
        
        stats_path = self.output_dir / "design_statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"[COMPLETE] Validation framework design completed in {elapsed:.2f} seconds")
        logger.info(f"[STATS] {stats}")
        
        return stats


def main():
    """Main execution function."""
    print("=" * 60)
    print("Validation Framework Design - Task 2.5")
    print("=" * 60)
    
    try:
        designer = ValidationFrameworkDesigner()
        stats = designer.run_full_design()
        
        print("\n" + "=" * 60)
        print("DESIGN COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"• Data collection protocols: {stats['data_protocols']}")
        print(f"• Validation metrics: {stats['validation_metrics']}")
        print(f"• Success criteria: {stats['success_criteria']}")
        print(f"• Timeline phases: {stats['timeline_phases']}")
        print(f"• Processing time: {stats['processing_time_seconds']} seconds")
        print(f"\nOutput files saved to: outputs/validation_framework/")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"[ERROR] Design process failed: {e}", exc_info=True)
        print(f"\n[ERROR] Design process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
