"""
Task 2.3: Sensitivity Analysis - Sobol Indices

Implements БЛОК 2, Task 2.3 from revision plan.
Performs Sobol variance decomposition sensitivity analysis for Q_OTU calculation.
Uses Saltelli sampling and computes first-order and total-order Sobol indices.
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

# Try to import SALib, but provide fallback if not installed
try:
    from SALib.sample import saltelli
    from SALib.analyze import sobol
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False
    print("WARNING: SALib not installed. Install with: pip install SALib")
    print("Using simplified Sobol implementation for demonstration.")

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'sensitivity_analysis_sobol.log', encoding='utf-8'),
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

class SobolSensitivityAnalyzer:
    """
    Sobol sensitivity analyzer for Q_OTU.
    Performs variance decomposition to compute first-order and total-order Sobol indices.
    """
    
    def __init__(self, n_samples: int = 1024):
        self.start_time = time.time()
        self.n_samples = n_samples
        logger.info(f"[INIT] SobolSensitivityAnalyzer initialized with N={n_samples}")
        
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
        
        # Define parameter bounds for Sobol analysis
        self.problem = {
            'num_vars': 7,
            'names': ['q_vi', 'q_si', 'q_bi', 'q_relief', 'k_vi', 'k_si', 'k_bi'],
            'bounds': [
                [0.2, 0.9],    # q_vi
                [0.1, 0.8],    # q_si
                [0.3, 0.85],   # q_bi
                [0.4, 0.95],   # q_relief
                [0.1, 0.6],    # k_vi (weights must sum to ~1)
                [0.1, 0.6],    # k_si
                [0.1, 0.6]     # k_bi
            ]
        }
        
        logger.info(f"[INFO] Baseline Q_OTU: {compute_q_otu(self.baseline):.3f}")
        logger.info(f"[INFO] Parameter bounds defined for Sobol analysis")
    
    def generate_samples(self) -> np.ndarray:
        """Generate Saltelli samples for Sobol analysis."""
        logger.info(f"[PROCESS] Generating Saltelli samples for Sobol analysis")
        
        if not SALIB_AVAILABLE:
            logger.warning("[WARNING] SALib not available, using simplified sampling")
            return self._generate_simplified_samples()
        
        try:
            # Generate Saltelli samples
            param_values = saltelli.sample(self.problem, self.n_samples, calc_second_order=True)
            logger.info(f"[OK] Generated {len(param_values)} Saltelli samples")
            return param_values
        except Exception as e:
            logger.error(f"[ERROR] Failed to generate Saltelli samples: {e}")
            logger.info("[INFO] Falling back to simplified sampling")
            return self._generate_simplified_samples()
    
    def _generate_simplified_samples(self) -> np.ndarray:
        """Generate simplified samples when SALib is not available."""
        logger.info("[PROCESS] Generating simplified Sobol samples")
        
        # Simplified Latin Hypercube sampling
        n_params = self.problem['num_vars']
        n_total = self.n_samples * (2 * n_params + 2)  # Approximate Saltelli size
        
        np.random.seed(42)
        samples = np.zeros((n_total, n_params))
        
        for i in range(n_params):
            bounds = self.problem['bounds'][i]
            # Latin hypercube sampling
            lhs = np.random.uniform(0, 1, n_total)
            perm = np.random.permutation(n_total)
            samples[:, i] = bounds[0] + (bounds[1] - bounds[0]) * lhs[perm]
        
        logger.info(f"[OK] Generated {len(samples)} simplified samples")
        return samples
    
    def evaluate_model(self, param_values: np.ndarray) -> np.ndarray:
        """Evaluate Q_OTU model for all parameter samples."""
        logger.info(f"[PROCESS] Evaluating Q_OTU model for {len(param_values)} samples")
        
        results = []
        
        for i, params in enumerate(param_values):
            # Create OTUParameters object
            otu_params = OTUParameters(
                q_vi=params[0],
                q_si=params[1],
                q_bi=params[2],
                q_relief=params[3],
                k_vi=params[4],
                k_si=params[5],
                k_bi=params[6]
            )
            
            # Compute Q_OTU
            q_otu = compute_q_otu(otu_params)
            results.append(q_otu)
            
            # Log progress every 100 samples
            if (i + 1) % 100 == 0:
                logger.info(f"[PROGRESS] Evaluated {i + 1}/{len(param_values)} samples")
        
        results_array = np.array(results)
        logger.info(f"[OK] Model evaluation complete. Mean Q_OTU: {results_array.mean():.3f}")
        return results_array
    
    def compute_sobol_indices(self, param_values: np.ndarray, model_output: np.ndarray) -> Dict[str, Any]:
        """Compute Sobol indices using SALib or simplified method."""
        logger.info("[PROCESS] Computing Sobol indices")
        
        if not SALIB_AVAILABLE:
            logger.warning("[WARNING] SALib not available, computing simplified indices")
            return self._compute_simplified_indices(param_values, model_output)
        
        try:
            # Use SALib for Sobol analysis
            sobol_results = sobol.analyze(self.problem, model_output, calc_second_order=True, print_to_console=False)
            
            # Extract results
            results = {
                'S1': sobol_results['S1'].tolist(),           # First-order indices
                'S1_conf': sobol_results['S1_conf'].tolist(), # Confidence intervals for S1
                'ST': sobol_results['ST'].tolist(),           # Total-order indices
                'ST_conf': sobol_results['ST_conf'].tolist(), # Confidence intervals for ST
                'S2': sobol_results['S2'].tolist() if 'S2' in sobol_results else [],  # Second-order indices
                'S2_conf': sobol_results['S2_conf'].tolist() if 'S2_conf' in sobol_results else [],
                'parameter_names': self.problem['names'],
                'total_variance': float(np.var(model_output)),
                'mean_output': float(np.mean(model_output))
            }
            
            logger.info("[OK] Sobol indices computed using SALib")
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to compute Sobol indices with SALib: {e}")
            logger.info("[INFO] Falling back to simplified method")
            return self._compute_simplified_indices(param_values, model_output)
    
    def _compute_simplified_indices(self, param_values: np.ndarray, model_output: np.ndarray) -> Dict[str, Any]:
        """Compute simplified sensitivity indices when SALib is not available."""
        logger.info("[PROCESS] Computing simplified sensitivity indices")
        
        n_params = self.problem['num_vars']
        n_samples = len(model_output)
        
        # Basic variance-based sensitivity (simplified)
        total_variance = np.var(model_output)
        
        # Compute first-order indices using brute-force approximation
        S1 = np.zeros(n_params)
        S1_conf = np.zeros(n_params)
        ST = np.zeros(n_params)
        ST_conf = np.zeros(n_params)
        
        # For each parameter, compute sensitivity
        for i in range(n_params):
            # Sort by parameter value
            sorted_indices = np.argsort(param_values[:, i])
            sorted_output = model_output[sorted_indices]
            
            # Divide into bins
            n_bins = min(20, n_samples // 10)
            bins = np.array_split(sorted_output, n_bins)
            
            # Compute variance of means (between bins) and mean of variances (within bins)
            bin_means = [np.mean(bin) for bin in bins]
            bin_vars = [np.var(bin) for bin in bins]
            
            variance_between = np.var(bin_means)
            variance_within = np.mean(bin_vars)
            
            # Simplified first-order index (proportion of variance explained)
            if total_variance > 0:
                S1[i] = variance_between / total_variance
                ST[i] = 1 - (variance_within / total_variance)  # Simplified total-order
            
            # Simple confidence interval approximation
            S1_conf[i] = S1[i] * 0.1  # 10% of value as approximation
            ST_conf[i] = ST[i] * 0.1
        
        # Ensure indices are in [0, 1]
        S1 = np.clip(S1, 0, 1)
        ST = np.clip(ST, 0, 1)
        
        results = {
            'S1': S1.tolist(),
            'S1_conf': S1_conf.tolist(),
            'ST': ST.tolist(),
            'ST_conf': ST_conf.tolist(),
            'S2': [],  # No second-order in simplified version
            'S2_conf': [],
            'parameter_names': self.problem['names'],
            'total_variance': float(total_variance),
            'mean_output': float(np.mean(model_output)),
            'method': 'simplified_variance_decomposition'
        }
        
        logger.info("[OK] Simplified sensitivity indices computed")
        return results
    
    def interpret_interaction_effects(self, sobol_results: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret interaction effects from Sobol indices."""
        logger.info("[PROCESS] Interpreting interaction effects")
        
        S1 = np.array(sobol_results['S1'])
        ST = np.array(sobol_results['ST'])
        param_names = sobol_results['parameter_names']
        
        # Calculate interaction indices (difference between total and first-order)
        interaction_indices = ST - S1
        
        # Identify parameters with significant interactions
        significant_interactions = []
        for i, (name, interaction) in enumerate(zip(param_names, interaction_indices)):
            if interaction > 0.05:  # Threshold for significant interaction
                significant_interactions.append({
                    'parameter': name,
                    'interaction_index': float(interaction),
                    'first_order': float(S1[i]),
                    'total_order': float(ST[i]),
                    'interpretation': self._get_interaction_interpretation(name, interaction)
                })
        
        # Rank parameters by importance
        importance_ranking = []
        for i, name in enumerate(param_names):
            importance_ranking.append({
                'parameter': name,
                'first_order_rank': i + 1,
                'total_order_rank': i + 1,
                'first_order_value': float(S1[i]),
                'total_order_value': float(ST[i]),
                'interaction_effect': float(interaction_indices[i])
            })
        
        # Sort by total-order importance
        importance_ranking.sort(key=lambda x: x['total_order_value'], reverse=True)
        for i, item in enumerate(importance_ranking):
            item['total_order_rank'] = i + 1
        
        # Sort by first-order importance
        importance_ranking.sort(key=lambda x: x['first_order_value'], reverse=True)
        for i, item in enumerate(importance_ranking):
            item['first_order_rank'] = i + 1
        
        # Sort back by total-order for final output
        importance_ranking.sort(key=lambda x: x['total_order_value'], reverse=True)
        
        interpretation = {
            'significant_interactions': significant_interactions,
            'importance_ranking': importance_ranking,
            'total_variance_explained': float(np.sum(S1)),
            'total_interaction_effect': float(np.sum(interaction_indices)),
            'most_influential_parameter': importance_ranking[0]['parameter'] if importance_ranking else None,
            'parameter_with_most_interactions': max(significant_interactions, key=lambda x: x['interaction_index'])['parameter'] if significant_interactions else None
        }
        
        logger.info(f"[OK] Interaction effects interpreted. Found {len(significant_interactions)} significant interactions")
        return interpretation
    
    def _get_interaction_interpretation(self, param_name: str, interaction_index: float) -> str:
        """Get human-readable interpretation of interaction effect."""
        interpretations = {
            'q_vi': "Vegetation quality interacts with other parameters (e.g., relief affects vegetation impact)",
            'q_si': "Soil quality shows interactions with weights and other environmental factors",
            'q_bi': "Biodiversity interacts with vegetation and soil parameters",
            'q_relief': "Relief interacts strongly with all quality indices (multiplicative effect in Q_OTU)",
            'k_vi': "Vegetation weight interacts with other weights (competition for influence)",
            'k_si': "Soil weight shows interaction effects in the weighted sum",
            'k_bi': "Biodiversity weight interacts with other weighting factors"
        }
        
        base_interpretation = interpretations.get(param_name, "Parameter interacts with other factors in the model")
        
        if interaction_index > 0.1:
            strength = "strong"
        elif interaction_index > 0.05:
            strength = "moderate"
        else:
            strength = "weak"
        
        return f"{strength.capitalize()} interaction: {base_interpretation}"
    
    def create_sobol_plots(self, sobol_results: Dict[str, Any], interpretation: Dict[str, Any], output_dir: Path):
        """Create plots for Sobol analysis results."""
        logger.info("[PROCESS] Creating Sobol analysis plots")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        S1 = np.array(sobol_results['S1'])
        S1_conf = np.array(sobol_results['S1_conf'])
        ST = np.array(sobol_results['ST'])
        ST_conf = np.array(sobol_results['ST_conf'])
        param_names = sobol_results['parameter_names']
        
        # 1. Sobol indices bar chart
        plt.figure(figsize=(12, 8))
        
        x_pos = np.arange(len(param_names))
        width = 0.35
        
        plt.bar(x_pos - width/2, S1, width, yerr=S1_conf, 
               label='First-order (S1)', color='steelblue', alpha=0.8, capsize=5)
        plt.bar(x_pos + width/2, ST, width, yerr=ST_conf,
               label='Total-order (ST)', color='coral', alpha=0.8, capsize=5)
        
        plt.xlabel('Parameter', fontsize=12)
        plt.ylabel('Sobol Index', fontsize=12)
        plt.title('Sobol Sensitivity Indices for Q_OTU Parameters', fontsize=14)
        plt.xticks(x_pos, param_names, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y