"""
Task 2.6: Validation Framework Implementation

Implements БЛОК 2, Task 2.6 from revision plan.
Implements the ValidationFramework class with:
1. Simulation of validation data
2. Calculation of all validation metrics
3. Creation of Supplementary Figure S2 (validation workflow)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import sys
import time
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from scipy import stats
from sklearn.metrics import confusion_matrix, cohen_kappa_score, precision_recall_curve, auc
import seaborn as sns

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'validation_framework_implementation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Container for validation results."""
    metric_name: str
    value: float
    interpretation: str
    meets_threshold: bool
    threshold: float

class ValidationFramework:
    """
    Implementation of validation framework for OTU methodology.
    Calculates validation metrics and generates validation reports.
    """
    
    def __init__(self, random_seed: int = 42):
        self.start_time = time.time()
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        logger.info(f"[INIT] ValidationFramework initialized with random_seed={random_seed}")
        
        # Define output directories
        self.output_dir = Path("outputs/validation_framework")
        self.figures_dir = Path("outputs/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Define stability classes
        self.stability_classes = {
            'Very Low': (0.0, 0.2),
            'Low': (0.2, 0.4),
            'Moderate': (0.4, 0.6),
            'High': (0.6, 0.8),
            'Very High': (0.8, 1.0)
        }
        
        # Define success thresholds (from Task 2.5)
        self.success_thresholds = {
            'pearson_correlation': 0.70,
            'spearman_correlation': 0.65,
            'cohens_kappa': 0.60,
            'rmse': 0.15,
            'mae': 0.12,
            'r_squared': 0.50,
            'anova_f': 4.0,
            'morans_i': 0.20,  # absolute value
            'bias': 0.05,      # absolute value
            'precision_recall_auc': 0.75
        }
        
        # Initialize results storage
        self.validation_results = []
        self.predicted_data = None
        self.observed_data = None
        
        logger.info("[INFO] Validation framework ready for implementation")
    
    def simulate_validation_data(self, n_samples: int = 100) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Simulate validation data (predicted vs observed).
        In real application, this would be replaced with actual field data.
        """
        logger.info(f"[SIMULATION] Generating simulated validation data (n={n_samples})")
        
        # Generate predicted Q_OTU values (from model)
        predicted_q_otu = np.random.uniform(0.1, 0.9, n_samples)
        
        # Generate observed Q_OTU values with some error
        # Simulate realistic errors: bias + random noise
        bias = np.random.uniform(-0.05, 0.05)  # Small systematic bias
        noise_std = 0.1  # Random noise standard deviation
        
        observed_q_otu = predicted_q_otu + bias + np.random.normal(0, noise_std, n_samples)
        
        # Clip to [0, 1] range
        observed_q_otu = np.clip(observed_q_otu, 0.0, 1.0)
        
        # Assign stability classes
        predicted_classes = [self._classify_stability(q) for q in predicted_q_otu]
        observed_classes = [self._classify_stability(q) for q in observed_q_otu]
        
        # Create DataFrames
        predicted_df = pd.DataFrame({
            'otu_id': [f'OTU_{i:03d}' for i in range(1, n_samples + 1)],
            'predicted_q_otu': predicted_q_otu,
            'predicted_class': predicted_classes,
            'q_vi': np.random.uniform(0.2, 0.9, n_samples),
            'q_si': np.random.uniform(0.1, 0.8, n_samples),
            'q_bi': np.random.uniform(0.3, 0.85, n_samples),
            'q_relief': np.random.uniform(0.4, 0.95, n_samples)
        })
        
        observed_df = pd.DataFrame({
            'otu_id': [f'OTU_{i:03d}' for i in range(1, n_samples + 1)],
            'observed_q_otu': observed_q_otu,
            'observed_class': observed_classes,
            'field_measurement_date': pd.date_range('2025-06-01', periods=n_samples, freq='D'),
            'measurement_team': np.random.choice(['Team_A', 'Team_B', 'Team_C'], n_samples),
            'measurement_quality': np.random.choice(['High', 'Medium', 'Low'], n_samples, p=[0.7, 0.2, 0.1])
        })
        
        self.predicted_data = predicted_df
        self.observed_data = observed_df
        
        logger.info(f"[OK] Simulated validation data generated: {n_samples} samples")
        logger.info(f"      Predicted Q_OTU range: {predicted_q_otu.min():.3f} - {predicted_q_otu.max():.3f}")
        logger.info(f"      Observed Q_OTU range: {observed_q_otu.min():.3f} - {observed_q_otu.max():.3f}")
        
        return predicted_df, observed_df
    
    def _classify_stability(self, q_otu: float) -> str:
        """Classify Q_OTU into stability class."""
        for class_name, (min_val, max_val) in self.stability_classes.items():
            if min_val <= q_otu < max_val:
                return class_name
        return 'Unknown'
    
    def calculate_pearson_correlation(self) -> ValidationResult:
        """Calculate Pearson correlation coefficient."""
        logger.info("[METRIC] Calculating Pearson correlation coefficient")
        
        if self.predicted_data is None or self.observed_data is None:
            raise ValueError("Validation data not loaded. Run simulate_validation_data() first.")
        
        # Merge data
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        # Calculate Pearson correlation
        r_value, p_value = stats.pearsonr(merged['predicted_q_otu'], merged['observed_q_otu'])
        
        # Interpretation
        if abs(r_value) >= 0.8:
            interpretation = "Very strong correlation"
        elif abs(r_value) >= 0.6:
            interpretation = "Strong correlation"
        elif abs(r_value) >= 0.4:
            interpretation = "Moderate correlation"
        elif abs(r_value) >= 0.2:
            interpretation = "Weak correlation"
        else:
            interpretation = "Very weak or no correlation"
        
        interpretation += f" (p={p_value:.4f})"
        
        result = ValidationResult(
            metric_name="Pearson Correlation Coefficient",
            value=r_value,
            interpretation=interpretation,
            meets_threshold=abs(r_value) >= self.success_thresholds['pearson_correlation'],
            threshold=self.success_thresholds['pearson_correlation']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] Pearson correlation: {r_value:.4f} (threshold: {result.threshold})")
        
        return result
    
    def calculate_spearman_correlation(self) -> ValidationResult:
        """Calculate Spearman rank correlation coefficient."""
        logger.info("[METRIC] Calculating Spearman rank correlation coefficient")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        # Calculate Spearman correlation
        rho_value, p_value = stats.spearmanr(merged['predicted_q_otu'], merged['observed_q_otu'])
        
        # Interpretation
        if abs(rho_value) >= 0.8:
            interpretation = "Very strong monotonic relationship"
        elif abs(rho_value) >= 0.6:
            interpretation = "Strong monotonic relationship"
        elif abs(rho_value) >= 0.4:
            interpretation = "Moderate monotonic relationship"
        elif abs(rho_value) >= 0.2:
            interpretation = "Weak monotonic relationship"
        else:
            interpretation = "Very weak or no monotonic relationship"
        
        interpretation += f" (p={p_value:.4f})"
        
        result = ValidationResult(
            metric_name="Spearman Rank Correlation",
            value=rho_value,
            interpretation=interpretation,
            meets_threshold=abs(rho_value) >= self.success_thresholds['spearman_correlation'],
            threshold=self.success_thresholds['spearman_correlation']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] Spearman correlation: {rho_value:.4f} (threshold: {result.threshold})")
        
        return result
    
    def calculate_cohens_kappa(self) -> ValidationResult:
        """Calculate Cohen's Kappa coefficient for classification agreement."""
        logger.info("[METRIC] Calculating Cohen's Kappa coefficient")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        # Calculate Cohen's Kappa
        kappa = cohen_kappa_score(merged['predicted_class'], merged['observed_class'])
        
        # Interpretation (Landis & Koch, 1977)
        if kappa < 0:
            interpretation = "Poor agreement (worse than chance)"
        elif kappa <= 0.2:
            interpretation = "Slight agreement"
        elif kappa <= 0.4:
            interpretation = "Fair agreement"
        elif kappa <= 0.6:
            interpretation = "Moderate agreement"
        elif kappa <= 0.8:
            interpretation = "Substantial agreement"
        else:
            interpretation = "Almost perfect agreement"
        
        result = ValidationResult(
            metric_name="Cohen's Kappa Coefficient",
            value=kappa,
            interpretation=interpretation,
            meets_threshold=kappa >= self.success_thresholds['cohens_kappa'],
            threshold=self.success_thresholds['cohens_kappa']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] Cohen's Kappa: {kappa:.4f} (threshold: {result.threshold})")
        
        return result
    
    def calculate_error_metrics(self) -> Tuple[ValidationResult, ValidationResult]:
        """Calculate RMSE and MAE."""
        logger.info("[METRIC] Calculating error metrics (RMSE, MAE)")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        errors = merged['observed_q_otu'] - merged['predicted_q_otu']
        
        # RMSE
        rmse = np.sqrt(np.mean(errors ** 2))
        
        # MAE
        mae = np.mean(np.abs(errors))
        
        # RMSE interpretation
        if rmse <= 0.05:
            rmse_interpretation = "Excellent prediction accuracy"
        elif rmse <= 0.10:
            rmse_interpretation = "Good prediction accuracy"
        elif rmse <= 0.15:
            rmse_interpretation = "Acceptable prediction accuracy"
        elif rmse <= 0.20:
            rmse_interpretation = "Marginal prediction accuracy"
        else:
            rmse_interpretation = "Poor prediction accuracy"
        
        # MAE interpretation
        if mae <= 0.04:
            mae_interpretation = "Very small average error"
        elif mae <= 0.08:
            mae_interpretation = "Small average error"
        elif mae <= 0.12:
            mae_interpretation = "Moderate average error"
        elif mae <= 0.16:
            mae_interpretation = "Large average error"
        else:
            mae_interpretation = "Very large average error"
        
        rmse_result = ValidationResult(
            metric_name="Root Mean Square Error (RMSE)",
            value=rmse,
            interpretation=rmse_interpretation,
            meets_threshold=rmse <= self.success_thresholds['rmse'],
            threshold=self.success_thresholds['rmse']
        )
        
        mae_result = ValidationResult(
            metric_name="Mean Absolute Error (MAE)",
            value=mae,
            interpretation=mae_interpretation,
            meets_threshold=mae <= self.success_thresholds['mae'],
            threshold=self.success_thresholds['mae']
        )
        
        self.validation_results.extend([rmse_result, mae_result])
        logger.info(f"[OK] RMSE: {rmse:.4f} (threshold: {rmse_result.threshold})")
        logger.info(f"[OK] MAE: {mae:.4f} (threshold: {mae_result.threshold})")
        
        return rmse_result, mae_result
    
    def calculate_r_squared(self) -> ValidationResult:
        """Calculate R-squared (coefficient of determination)."""
        logger.info("[METRIC] Calculating R-squared")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        # Calculate R-squared
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            merged['predicted_q_otu'], merged['observed_q_otu']
        )
        r_squared = r_value ** 2
        
        # Interpretation
        if r_squared >= 0.8:
            interpretation = "Excellent explanatory power"
        elif r_squared >= 0.6:
            interpretation = "Good explanatory power"
        elif r_squared >= 0.4:
            interpretation = "Moderate explanatory power"
        elif r_squared >= 0.2:
            interpretation = "Weak explanatory power"
        else:
            interpretation = "Very weak explanatory power"
        
        interpretation += f" (linear regression slope: {slope:.3f})"
        
        result = ValidationResult(
            metric_name="R-squared (Coefficient of Determination)",
            value=r_squared,
            interpretation=interpretation,
            meets_threshold=r_squared >= self.success_thresholds['r_squared'],
            threshold=self.success_thresholds['r_squared']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] R-squared: {r_squared:.4f} (threshold: {result.threshold})")
        
        return result
    
    def calculate_anova_f_statistic(self) -> ValidationResult:
        """Calculate ANOVA F-statistic for between-class variance."""
        logger.info("[METRIC] Calculating ANOVA F-statistic")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        # Prepare data for ANOVA
        groups = []
        for class_name in self.stability_classes.keys():
            class_data = merged[merged['predicted_class'] == class_name]['observed_q_otu']
            if len(class_data) > 0:
                groups.append(class_data)
        
        # Perform one-way ANOVA
        if len(groups) >= 2:
            f_statistic, p_value = stats.f_oneway(*groups)
        else:
            f_statistic, p_value = 0.0, 1.0
        
        # Interpretation
        if p_value < 0.001:
            interpretation = "Highly significant difference between classes (p < 0.001)"
        elif p_value < 0.01:
            interpretation = "Very significant difference between classes (p < 0.01)"
        elif p_value < 0.05:
            interpretation = "Significant difference between classes (p < 0.05)"
        else:
            interpretation = "No significant difference between classes"
        
        interpretation += f" (F={f_statistic:.2f}, p={p_value:.4f})"
        
        result = ValidationResult(
            metric_name="ANOVA F-statistic (Between-class variance)",
            value=f_statistic,
            interpretation=interpretation,
            meets_threshold=f_statistic >= self.success_thresholds['anova_f'] and p_value < 0.05,
            threshold=self.success_thresholds['anova_f']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] ANOVA F-statistic: {f_statistic:.2f} (p={p_value:.4f}, threshold: {result.threshold})")
        
        return result
    
    def calculate_bias(self) -> ValidationResult:
        """Calculate bias (mean error)."""
        logger.info("[METRIC] Calculating bias (mean error)")
        
        merged = pd.merge(self.predicted_data, self.observed_data, on='otu_id')
        
        errors = merged['observed_q_otu'] - merged['predicted_q_otu']
        bias = np.mean(errors)
        
        # Interpretation
        if abs(bias) <= 0.01:
            interpretation = "Negligible bias"
        elif abs(bias) <= 0.03:
            interpretation = "Small bias"
        elif abs(bias) <= 0.05:
            interpretation = "Moderate bias"
        elif abs(bias) <= 0.08:
            interpretation = "Substantial bias"
        else:
            interpretation = "Large bias"
        
        direction = "overestimation" if bias < 0 else "underestimation"
        interpretation += f" ({abs(bias):.3f} {direction})"
        
        result = ValidationResult(
            metric_name="Bias (Mean Error)",
            value=bias,
            interpretation=interpretation,
            meets_threshold=abs(bias) <= self.success_thresholds['bias'],
            threshold=self.success_thresholds['bias']
        )
        
        self.validation_results.append(result)
        logger.info(f"[OK] Bias: {bias:.4f} (threshold: {result.threshold})")
        
        return result