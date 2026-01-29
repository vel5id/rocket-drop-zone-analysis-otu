"""
Task 2.2: Sensitivity Analysis - Monte Carlo

Implements БЛОК 2, Task 2.2 from revision plan.
Performs Monte Carlo sensitivity analysis for Q_OTU calculation.
Uses Dirichlet distribution for weights and uniform distributions for quality indices.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import sys
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
from scipy import stats
import seaborn as sns

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'sensitivity_analysis_monte_carlo.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OTUParameters:
    """Parameters for a sample OTU."""
    q_vi: float  # Vegetation quality index (0-1)
    q_si: float  # Soil quality index (0-1)
    q_bi: float  # Biodiversity index (0-1)
    q_relief: float  # Relief index (0-1)
    k_vi: float = 0.35  # Vegetation weight
    k_si: float = 0.35  # Soil weight
    k_bi: float = 0.30  # Biodiversity weight

def compute_q_otu(params: OTUParameters) -> float:
    """Compute Q_OTU using the formula from indices/q_otu.py."""
    # Normalize weights
    total_weight = params.k_vi + params.k_si + params.k_bi
    if total_weight == 0:
        k_vi_norm = k_si_norm = k_bi_norm = 1/3
    else:
        k_vi_norm = params.k_vi / total_weight
        k_si_norm = params.k_si / total_weight
        k_bi_norm = params.k_bi / total_weight
    
    # Linear combination
    linear_part = (k_vi_norm * params.q_vi + 
                   k_si_norm * params.q_si + 
                   k_bi_norm * params.q_bi)
    
    # Multiply by relief
    result = linear_part * params.q_relief
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, result))

class MonteCarloSensitivityAnalyzer:
    """
    Monte Carlo sensitivity analyzer for Q_OTU.
    Uses Dirichlet distribution for weights and uniform distributions for quality indices.
    """
    
    def __init__(self, n_samples: int = 1000):
        self.start_time = time.time()
        self.n_samples = n_samples
        logger.info(f"[INIT] MonteCarloSensitivityAnalyzer initialized with N={n_samples}")
        
        # Define baseline parameters (representative OTU)
        self.baseline = OTUParameters(
            q_vi=0.65,    # Moderate vegetation
            q_si=0.45,    # Moderate soil quality
            q_bi=0.55,    # Moderate biodiversity
            q_relief=0.75, # Good relief
            k_vi=0.35,
            k_si=0.35,
            k_bi=0.30
        )
        
        # Define stability classes for reclassification
        self.stability_classes = {
            'Very Low': (0.0, 0.2),
            'Low': (0.2, 0.4),
            'Moderate': (0.4, 0.6),
            'High': (0.6, 0.8),
            'Very High': (0.8, 1.0)
        }
        
        # Define parameter distributions
        self.parameter_distributions = {
            'q_vi': {'type': 'uniform', 'min': 0.2, 'max': 0.9},
            'q_si': {'type': 'uniform', 'min': 0.1, 'max': 0.8},
            'q_bi': {'type': 'uniform', 'min': 0.3, 'max': 0.85},
            'q_relief': {'type': 'uniform', 'min': 0.4, 'max': 0.95},
            'weights': {'type': 'dirichlet', 'alpha': [3.5, 3.5, 3.0]}  # Dirichlet for (k_vi, k_si, k_bi)
        }
        
        logger.info(f"[INFO] Baseline Q_OTU: {compute_q_otu(self.baseline):.3f}")
        logger.info(f"[INFO] Parameter distributions defined")
    
    def generate_samples(self) -> pd.DataFrame:
        """Generate Monte Carlo samples for all parameters."""
        logger.info(f"[PROCESS] Generating {self.n_samples} Monte Carlo samples")
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Generate samples for quality indices (uniform distributions)
        samples = {}
        
        # Quality indices - uniform distributions
        for param, dist in self.parameter_distributions.items():
            if param == 'weights':
                continue
                
            if dist['type'] == 'uniform':
                samples[param] = np.random.uniform(
                    dist['min'], dist['max'], self.n_samples
                )
                logger.info(f"[OK] Generated {param}: uniform({dist['min']:.2f}, {dist['max']:.2f})")
        
        # Weights - Dirichlet distribution
        alpha = self.parameter_distributions['weights']['alpha']
        dirichlet_samples = np.random.dirichlet(alpha, self.n_samples)
        samples['k_vi'] = dirichlet_samples[:, 0]
        samples['k_si'] = dirichlet_samples[:, 1]
        samples['k_bi'] = dirichlet_samples[:, 2]
        
        logger.info(f"[OK] Generated weights: Dirichlet(alpha={alpha})")
        
        # Create DataFrame
        df = pd.DataFrame(samples)
        
        # Add sample IDs
        df['sample_id'] = range(1, self.n_samples + 1)
        
        # Compute Q_OTU for each sample
        logger.info("[PROCESS] Computing Q_OTU for all samples")
        q_otu_values = []
        
        for idx, row in df.iterrows():
            params = OTUParameters(
                q_vi=row['q_vi'],
                q_si=row['q_si'],
                q_bi=row['q_bi'],
                q_relief=row['q_relief'],
                k_vi=row['k_vi'],
                k_si=row['k_si'],
                k_bi=row['k_bi']
            )
            q_otu_values.append(compute_q_otu(params))
        
        df['q_otu'] = q_otu_values
        
        # Determine stability class for each sample
        df['stability_class'] = df['q_otu'].apply(self._classify_stability)
        
        logger.info(f"[OK] Generated {len(df)} samples with Q_OTU values")
        return df
    
    def _classify_stability(self, q_otu: float) -> str:
        """Classify Q_OTU into stability class."""
        for class_name, (min_val, max_val) in self.stability_classes.items():
            if min_val <= q_otu < max_val:
                return class_name
        return 'Unknown'
    
    def compute_reclassification_rates(self, samples_df: pd.DataFrame) -> Dict[str, float]:
        """Compute reclassification rates compared to baseline."""
        logger.info("[PROCESS] Computing reclassification rates")
        
        baseline_q_otu = compute_q_otu(self.baseline)
        baseline_class = self._classify_stability(baseline_q_otu)
        
        # Count samples in each class
        class_counts = samples_df['stability_class'].value_counts()
        total_samples = len(samples_df)
        
        # Calculate reclassification rate (samples NOT in baseline class)
        samples_not_in_baseline = total_samples - class_counts.get(baseline_class, 0)
        reclassification_rate = (samples_not_in_baseline / total_samples) * 100
        
        # Calculate class distribution percentages
        class_distribution = {}
        for class_name in self.stability_classes.keys():
            count = class_counts.get(class_name, 0)
            class_distribution[class_name] = (count / total_samples) * 100
        
        results = {
            'baseline_q_otu': baseline_q_otu,
            'baseline_class': baseline_class,
            'reclassification_rate_%': reclassification_rate,
            'class_distribution_%': class_distribution,
            'total_samples': total_samples,
            'samples_not_in_baseline': samples_not_in_baseline
        }
        
        logger.info(f"[OK] Reclassification rate: {reclassification_rate:.1f}%")
        return results
    
    def compute_correlation_statistics(self, samples_df: pd.DataFrame) -> pd.DataFrame:
        """Compute correlation statistics between parameters and Q_OTU."""
        logger.info("[PROCESS] Computing correlation statistics")
        
        parameters = ['q_vi', 'q_si', 'q_bi', 'q_relief', 'k_vi', 'k_si', 'k_bi']
        records = []
        
        for param in parameters:
            # Pearson correlation
            pearson_corr, pearson_p = stats.pearsonr(samples_df[param], samples_df['q_otu'])
            
            # Spearman correlation (non-parametric)
            spearman_corr, spearman_p = stats.spearmanr(samples_df[param], samples_df['q_otu'])
            
            # R-squared (coefficient of determination)
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                samples_df[param], samples_df['q_otu']
            )
            r_squared = r_value ** 2
            
            # Sensitivity coefficient (change in Q_OTU per unit change in parameter)
            # Using linear regression slope
            sensitivity_coefficient = slope
            
            records.append({
                'parameter': param,
                'parameter_type': 'Weight' if param.startswith('k_') else 'Quality_Index',
                'mean_value': samples_df[param].mean(),
                'std_value': samples_df[param].std(),
                'pearson_correlation': pearson_corr,
                'pearson_p_value': pearson_p,
                'spearman_correlation': spearman_corr,
                'spearman_p_value': spearman_p,
                'r_squared': r_squared,
                'sensitivity_coefficient': sensitivity_coefficient,
                'q_otu_mean': samples_df['q_otu'].mean(),
                'q_otu_std': samples_df['q_otu'].std()
            })
        
        correlation_df = pd.DataFrame(records)
        correlation_df = correlation_df.sort_values('pearson_correlation', key=abs, ascending=False)
        
        logger.info(f"[OK] Correlation statistics computed for {len(parameters)} parameters")
        return correlation_df
    
    def compute_distribution_statistics(self, samples_df: pd.DataFrame) -> Dict[str, Any]:
        """Compute distribution statistics for Q_OTU."""
        logger.info("[PROCESS] Computing distribution statistics")
        
        q_otu_values = samples_df['q_otu']
        
        # Basic statistics
        stats_dict = {
            'mean': float(q_otu_values.mean()),
            'median': float(q_otu_values.median()),
            'std': float(q_otu_values.std()),
            'min': float(q_otu_values.min()),
            'max': float(q_otu_values.max()),
            'q1': float(q_otu_values.quantile(0.25)),
            'q3': float(q_otu_values.quantile(0.75)),
            'iqr': float(q_otu_values.quantile(0.75) - q_otu_values.quantile(0.25)),
            'skewness': float(stats.skew(q_otu_values)),
            'kurtosis': float(stats.kurtosis(q_otu_values)),
            'cv': float(q_otu_values.std() / q_otu_values.mean() * 100) if q_otu_values.mean() > 0 else 0
        }
        
        # Percentiles
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        for p in percentiles:
            stats_dict[f'percentile_{p}'] = float(q_otu_values.quantile(p/100))
        
        # Probability of being in each stability class
        for class_name in self.stability_classes.keys():
            count = len(samples_df[samples_df['stability_class'] == class_name])
            stats_dict[f'prob_{class_name.replace(" ", "_").lower()}'] = count / len(samples_df)
        
        logger.info(f"[OK] Distribution statistics computed")
        return stats_dict
    
    def create_histogram_plots(self, samples_df: pd.DataFrame, output_dir: Path):
        """Create histogram plots for Q_OTU distribution and parameter distributions."""
        logger.info("[PROCESS] Creating histogram plots")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Q_OTU distribution histogram
        plt.figure(figsize=(12, 8))
        
        # Main histogram
        plt.subplot(2, 2, 1)
        plt.hist(samples_df['q_otu'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
        plt.axvline(x=compute_q_otu(self.baseline), color='red', linestyle='--', 
                   linewidth=2, label=f'Baseline Q_OTU = {compute_q_otu(self.baseline):.3f}')
        plt.xlabel('Q_OTU', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Q_OTU (Monte Carlo Samples)', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # 2. Stability class distribution
        plt.subplot(2, 2, 2)
        class_counts = samples_df['stability_class'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(class_counts)))
        plt.bar(class_counts.index, class_counts.values, color=colors, edgecolor='black')
        plt.xlabel('Stability Class', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.title('Stability Class Distribution', fontsize=14)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')
        
        # 3. Q_OTU vs parameter scatter (most correlated parameter)
        correlation_df = self.compute_correlation_statistics(samples_df)
        most_correlated = correlation_df.iloc[0]['parameter']
        
        plt.subplot(2, 2, 3)
        plt.scatter(samples_df[most_correlated], samples_df['q_otu'], 
                   alpha=0.5, s=10, color='green')
        plt.xlabel(f'{most_correlated}', fontsize=12)
        plt.ylabel('Q_OTU', fontsize=12)
        plt.title(f'Q_OTU vs {most_correlated} (Most Correlated)', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # Add regression line
        z = np.polyfit(samples_df[most_correlated], samples_df['q_otu'], 1)
        p = np.poly1d(z)
        plt.plot(samples_df[most_correlated], p(samples_df[most_correlated]), 
                "r--", linewidth=2, label=f'R² = {correlation_df.iloc[0]["r_squared"]:.3f}')
        plt.legend()
        
        # 4. Weights distribution (Dirichlet)
        plt.subplot(2, 2, 4)
        weights_data = [samples_df['k_vi'], samples_df['k_si'], samples_df['k_bi']]
        plt.boxplot(weights_data, labels=['k_vi', 'k_si', 'k_bi'])
        plt.xlabel('Weight Parameter', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.title('Distribution of Weight Parameters (Dirichlet)', fontsize=14)
        plt.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plot_path = output_dir / 'monte_carlo_summary.png'
        plt.savefig(plot_path, dpi=300)
        plt.close()
        
        logger.info(f"[OK] Summary plot saved: {plot_path}")
        
        # 5. Individual parameter histograms
        parameters = ['q_vi', 'q_si', 'q_bi', 'q_relief']
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        for idx, param in enumerate(parameters):
            ax = axes[idx]
            ax.hist(samples_df[param], bins=25, edgecolor='black', alpha=0.7, 
                   color=plt.cm.tab20c(idx))
            ax.axvline(x=getattr(self.baseline, param), color='red', linestyle='--',
                      linewidth=2, label=f'Baseline = {getattr(self.baseline, param):.3f}')
            ax.set_xlabel(f'{param} Value', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_title(f'Distribution of {param}', fontsize=12)
            ax.grid(True, alpha=0.3)
