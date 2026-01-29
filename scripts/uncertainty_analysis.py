"""
Task 2.8: Uncertainty Analysis

Implements БЛОК 2, Task 2.8 from revision plan (lines 221-248).
Analyzes sources of uncertainty in OTU methodology, including:
1. DEM errors (±10-15m)
2. NDVI variability (±0.1-0.15)
3. Ballistics accuracy (±500m)
4. Soil data uncertainty (±20%)
5. Propagation of uncertainty methods (Monte Carlo, Taylor series, Sensitivity bounds)
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
from dataclasses import dataclass, asdict
from scipy import stats
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'uncertainty_analysis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UncertaintySource:
    """Represents a source of uncertainty in the OTU methodology."""
    name: str
    parameter: str
    uncertainty_type: str  # "random", "systematic", "epistemic"
    magnitude: float
    unit: str
    description: str
    mitigation_strategy: str

@dataclass
class UncertaintyPropagationResult:
    """Results of uncertainty propagation analysis."""
    source: str
    contribution_to_q_otu_variance: float
    relative_importance: float  # 0-1
    propagation_method: str

class UncertaintyAnalyzer:
    """
    Analyzes uncertainty in OTU methodology according to IMPLEMENTATION_ROADMAP.md (lines 221-248).
    """
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] UncertaintyAnalyzer initialized")
        
        # Define output directories according to roadmap requirements
        self.uncertainty_dir = Path("outputs/uncertainty")
        self.output_dir = Path("outputs/uncertainty_analysis")  # legacy compatibility
        self.figures_dir = Path("outputs/figures")
        self.uncertainty_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Define uncertainty sources
        self.uncertainty_sources = []
        self.propagation_results = []
        
        logger.info("[INFO] Uncertainty analyzer ready")
    
    def define_uncertainty_sources(self) -> List[UncertaintySource]:
        """Define major sources of uncertainty in OTU methodology as per roadmap."""
        logger.info("[ANALYSIS] Defining uncertainty sources (Roadmap lines 234-237)")
        
        sources = [
            UncertaintySource(
                name="DEM Vertical Accuracy",
                parameter="Elevation",
                uncertainty_type="random",
                magnitude=12.5,  # ±10-15m average (SRTM specification)
                unit="meters",
                description="Vertical error in Digital Elevation Model (SRTM 30m or ALOS 12.5m). Affects slope, aspect, and relief calculations.",
                mitigation_strategy="Use higher-resolution DEM where available; apply error propagation to slope calculations; consider DEM error in relief index."
            ),
            UncertaintySource(
                name="NDVI Measurement Variability",
                parameter="Vegetation Index",
                uncertainty_type="random",
                magnitude=0.125,  # ±0.1-0.15 (seasonal, atmospheric)
                unit="NDVI units",
                description="Temporal and atmospheric variability in NDVI measurements from Sentinel-2. Affects vegetation quality index (Q_VI).",
                mitigation_strategy="Use multi-temporal composites; apply atmospheric correction; validate with ground measurements."
            ),
            UncertaintySource(
                name="Ballistics Prediction Accuracy",
                parameter="Impact Location",
                uncertainty_type="systematic",
                magnitude=500.0,  # ±500m (Monte Carlo std)
                unit="meters",
                description="Uncertainty in predicted rocket stage impact location due to atmospheric conditions, wind, and stage separation dynamics.",
                mitigation_strategy="Use Monte Carlo ballistic simulations; incorporate meteorological data; apply safety buffers in OTU selection."
            ),
            UncertaintySource(
                name="Soil Parameter Estimation",
                parameter="Soil Quality",
                uncertainty_type="epistemic",
                magnitude=0.20,  # ±20% (SoilGrids accuracy)
                unit="Q_SI units",
                description="Uncertainty in soil quality index due to spatial interpolation, laboratory measurement errors, and temporal variability.",
                mitigation_strategy="Increase soil sampling density; use geostatistical interpolation; account for seasonal variations."
            ),
            UncertaintySource(
                name="Biodiversity Sampling Error",
                parameter="Biodiversity Index",
                uncertainty_type="random",
                magnitude=0.15,
                unit="Q_BI units",
                description="Sampling error in biodiversity assessments due to limited observation time, seasonal variations, and observer bias.",
                mitigation_strategy="Standardized sampling protocols; extended observation periods; expert verification; camera trap validation."
            ),
            UncertaintySource(
                name="Weighting Coefficient Uncertainty",
                parameter="k_VI, k_SI, k_BI",
                uncertainty_type="epistemic",
                magnitude=0.10,
                unit="weight units",
                description="Uncertainty in expert-derived weighting coefficients for vegetation, soil, and biodiversity components.",
                mitigation_strategy="Sensitivity analysis; expert consensus methods; validation against independent criteria."
            ),
            UncertaintySource(
                name="Spatial Resolution Limitations",
                parameter="All spatial parameters",
                uncertainty_type="systematic",
                magnitude=30.0,  # Sentinel-2 pixel size
                unit="meters",
                description="Limitations due to satellite sensor spatial resolution (10-30m). Sub-pixel heterogeneity not captured.",
                mitigation_strategy="Use highest available resolution; consider sub-pixel unmixing; validate with higher-resolution data."
            ),
            UncertaintySource(
                name="Temporal Misalignment",
                parameter="All time-dependent parameters",
                uncertainty_type="systematic",
                magnitude=14.0,  # days
                unit="days",
                description="Misalignment between satellite acquisition dates, field measurements, and ballistic prediction times.",
                mitigation_strategy="Temporal interpolation; use of cloud-free composites; consideration of phenological cycles."
            )
        ]
        
        self.uncertainty_sources = sources
        logger.info(f"[OK] Defined {len(sources)} uncertainty sources as per roadmap")
        return sources
    
    def quantify_uncertainty_contributions(self) -> Dict[str, Any]:
        """Quantify contributions of each uncertainty source to Q_OTU variance using Monte Carlo."""
        logger.info("[ANALYSIS] Quantifying uncertainty contributions (Monte Carlo propagation)")
        
        # This is a simplified Monte Carlo approach to estimate uncertainty propagation
        np.random.seed(42)
        n_simulations = 10000
        
        # Baseline parameters (representative OTU)
        baseline_params = {
            'q_vi': 0.65,
            'q_si': 0.45,
            'q_bi': 0.55,
            'q_relief': 0.75,
            'k_vi': 0.35,
            'k_si': 0.35,
            'k_bi': 0.30
        }
        
        # Define uncertainty distributions for each parameter
        uncertainty_distributions = {
            'q_vi': {'type': 'normal', 'mean': baseline_params['q_vi'], 'std': 0.08},  # NDVI uncertainty
            'q_si': {'type': 'normal', 'mean': baseline_params['q_si'], 'std': 0.10},  # Soil uncertainty
            'q_bi': {'type': 'normal', 'mean': baseline_params['q_bi'], 'std': 0.07},  # Biodiversity uncertainty
            'q_relief': {'type': 'normal', 'mean': baseline_params['q_relief'], 'std': 0.05},  # Relief uncertainty
            'k_vi': {'type': 'uniform', 'min': 0.25, 'max': 0.45},  # Weight uncertainty
            'k_si': {'type': 'uniform', 'min': 0.25, 'max': 0.45},
            'k_bi': {'type': 'uniform', 'min': 0.20, 'max': 0.40}
        }
        
        # Generate Monte Carlo samples
        samples = {}
        for param, dist in uncertainty_distributions.items():
            if dist['type'] == 'normal':
                samples[param] = np.random.normal(dist['mean'], dist['std'], n_simulations)
            elif dist['type'] == 'uniform':
                samples[param] = np.random.uniform(dist['min'], dist['max'], n_simulations)
        
        # Clip to valid ranges
        for param in ['q_vi', 'q_si', 'q_bi', 'q_relief']:
            samples[param] = np.clip(samples[param], 0.0, 1.0)
        
        # Compute Q_OTU for all samples
        q_otu_values = []
        for i in range(n_simulations):
            # Normalize weights
            total_weight = samples['k_vi'][i] + samples['k_si'][i] + samples['k_bi'][i]
            if total_weight == 0:
                k_vi_norm = k_si_norm = k_bi_norm = 1/3
            else:
                k_vi_norm = samples['k_vi'][i] / total_weight
                k_si_norm = samples['k_si'][i] / total_weight
                k_bi_norm = samples['k_bi'][i] / total_weight
            
            # Linear combination
            linear_part = (k_vi_norm * samples['q_vi'][i] + 
                          k_si_norm * samples['q_si'][i] + 
                          k_bi_norm * samples['q_bi'][i])
            
            # Multiply by relief
            q_otu = linear_part * samples['q_relief'][i]
            q_otu_values.append(max(0.0, min(1.0, q_otu)))
        
        q_otu_values = np.array(q_otu_values)
        
        # Calculate baseline Q_OTU
        baseline_q_otu = self._compute_baseline_q_otu(baseline_params)
        
        # Calculate statistics
        q_otu_mean = np.mean(q_otu_values)
        q_otu_std = np.std(q_otu_values)
        q_otu_cv = q_otu_std / q_otu_mean if q_otu_mean > 0 else 0
        
        # Calculate contributions using variance decomposition
        contributions = []
        for param in uncertainty_distributions.keys():
            # Simple correlation-based contribution estimate
            correlation = np.corrcoef(samples[param], q_otu_values)[0, 1]
            contribution = correlation ** 2  # R-squared from simple regression
            
            # Adjust for parameter variance
            param_std = np.std(samples[param])
            if param_std > 0:
                normalized_contribution = contribution * (param_std / np.std(q_otu_values))
            else:
                normalized_contribution = contribution
            
            contributions.append({
                'parameter': param,
                'correlation_with_q_otu': correlation,
                'variance_contribution': contribution,
                'normalized_contribution': normalized_contribution
            })
        
        # Sort by contribution
        contributions.sort(key=lambda x: x['normalized_contribution'], reverse=True)
        
        # Map to uncertainty sources
        source_mapping = {
            'q_vi': 'NDVI Measurement Variability',
            'q_si': 'Soil Parameter Estimation',
            'q_bi': 'Biodiversity Sampling Error',
            'q_relief': 'DEM Vertical Accuracy',
            'k_vi': 'Weighting Coefficient Uncertainty',
            'k_si': 'Weighting Coefficient Uncertainty',
            'k_bi': 'Weighting Coefficient Uncertainty'
        }
        
        # Aggregate by source
        source_contributions = {}
        for contrib in contributions:
            source_name = source_mapping.get(contrib['parameter'], 'Other')
            if source_name not in source_contributions:
                source_contributions[source_name] = {
                    'total_contribution': 0.0,
                    'parameters': []
                }
            source_contributions[source_name]['total_contribution'] += contrib['normalized_contribution']
            source_contributions[source_name]['parameters'].append(contrib['parameter'])
        
        # Create propagation results
        self.propagation_results = []
        for source_name, data in source_contributions.items():
            result = UncertaintyPropagationResult(
                source=source_name,
                contribution_to_q_otu_variance=data['total_contribution'],
                relative_importance=data['total_contribution'] / sum([d['total_contribution'] for d in source_contributions.values()]),
                propagation_method="Monte Carlo simulation with variance decomposition"
            )
            self.propagation_results.append(result)
        
        # Save results
        results = {
            'baseline_q_otu': float(baseline_q_otu),
            'q_otu_statistics': {
                'mean': float(q_otu_mean),
                'std': float(q_otu_std),
                'cv': float(q_otu_cv),
                'min': float(np.min(q_otu_values)),
                'max': float(np.max(q_otu_values)),
                'percentile_5': float(np.percentile(q_otu_values, 5)),
                'percentile_95': float(np.percentile(q_otu_values, 95))
            },
            'parameter_contributions': contributions,
            'source_contributions': source_contributions,
            'simulation_parameters': {
                'n_simulations': n_simulations,
                'random_seed': 42,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        results_path = self.output_dir / "uncertainty_propagation_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"[OK] Monte Carlo uncertainty propagation completed")
        logger.info(f"      Q_OTU statistics: mean={q_otu_mean:.3f}, std={q_otu_std:.3f}, CV={q_otu_cv:.2%}")
        logger.info(f"      Results saved to {results_path}")
        
        return results
    
    def first_order_taylor_series(self) -> Dict[str, Any]:
        """First-order Taylor series propagation of uncertainty (Roadmap line 241)."""
        logger.info("[ANALYSIS] First-order Taylor series propagation")
        
        # Baseline parameters
        params = {
            'q_vi': 0.65,
            'q_si': 0.45,
            'q_bi': 0.55,
            'q_relief': 0.75,
            'k_vi': 0.35,
            'k_si': 0.35,
            'k_bi': 0.30
        }
        
        # Uncertainties (standard deviations)
        uncertainties = {
            'q_vi': 0.08,    # NDVI uncertainty
            'q_si': 0.10,    # Soil uncertainty
            'q_bi': 0.07,    # Biodiversity uncertainty
            'q_relief': 0.05, # Relief uncertainty
            'k_vi': 0.05,    # Weight uncertainty
            'k_si': 0.05,
            'k_bi': 0.05
        }
        
        # Compute partial derivatives numerically
        epsilon = 1e-6
        baseline_q_otu = self._compute_baseline_q_otu(params)
        
        partials = {}
        for param in params.keys():
            params_plus = params.copy()
            params_plus[param] += epsilon
            q_otu_plus = self._compute_baseline_q_otu(params_plus)
            
            params_minus = params.copy()
            params_minus[param] -= epsilon
            q_otu_minus = self._compute_baseline_q_otu(params_minus)
            
            partial = (q_otu_plus - q_otu_minus) / (2 * epsilon)
            partials[param] = partial
        
        # Compute variance using first-order approximation
        total_variance = 0.0
        contributions = {}
        for param in params.keys():
            var_contribution = (partials[param] ** 2) * (uncertainties[param] ** 2)
            total_variance += var_contribution
            contributions[param] = {
                'partial_derivative': float(partials[param]),
                'uncertainty': float(uncertainties[param]),
                'variance_contribution': float(var_contribution),
                'relative_contribution': float(var_contribution)  # will normalize later
            }
        
        # Normalize contributions
        if total_variance > 0:
            for param in contributions:
                contributions[param]['relative_contribution'] = contributions[param]['variance_contribution'] / total_variance
        
        results = {
            'baseline_q_otu': float(baseline_q_otu),
            'total_variance': float(total_variance),
            'total_std': float(np.sqrt(total_variance)),
            'coefficient_of_variation': float(np.sqrt(total_variance) / baseline_q_otu if baseline_q_otu > 0 else 0),
            'parameter_contributions': contributions,
            'method': 'First-order Taylor series propagation',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
