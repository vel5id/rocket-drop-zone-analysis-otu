"""
Advanced Economic Analysis Module for Tasks 5.4-5.5.

This module extends the basic economic damage calculator with advanced analysis:
- Sensitivity analysis of economic parameters
- What-if scenarios for different rocket types and impact scenarios
- Long-term forecasts with inflation and exchange rate changes
- Risk assessment with probability distributions
- Cost-benefit analysis

References:
- Task 5.4-5.5 from IMPLEMENTATION_ROADMAP.md
- EconomicDamageCalculator from otu/economic_damage.py
- Results from Tasks 5.1-5.3 (calculator, examples, comparison)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
import json
import warnings
from scipy import stats
from datetime import datetime, timedelta

# Import existing economic calculator
try:
    from otu.economic_damage import EconomicDamageCalculator, calculate_comprehensive_damage
except ImportError:
    warnings.warn("Could not import EconomicDamageCalculator. Using stub implementation.")
    # Create stub for development
    class EconomicDamageCalculator:
        def __init__(self, usd_to_kzt=450.0):
            self.usd_to_kzt = usd_to_kzt
            self.costs_kzt = {
                'vegetation_loss': 50000,
                'soil_degradation': 30000,
                'fire_risk': 20000,
                'contamination': 40000,
                'mechanical_damage': 25000,
            }
        
        def calculate_total_damage(self, otu_results, cell_size_km=1.0):
            return {'grand_total_kzt': 1000000, 'grand_total_usd': 2222.22}


@dataclass
class RocketType:
    """Data class for different rocket types and their characteristics."""
    name: str
    fuel_type: str  # "Kerosene", "Hydrazine", "UDMH", "LOX/LH2"
    toxic_factor: float  # 1.0 = standard, >1.0 = more toxic
    impact_area_km2: float  # Typical impact area in km²
    debris_count: int  # Estimated number of debris pieces
    cleanup_complexity: float  # 1.0 = standard, >1.0 = more complex
    base_cost_multiplier: float  # Multiplier for base restoration costs


@dataclass
class EconomicScenario:
    """Data class for economic analysis scenarios."""
    name: str
    description: str
    rocket_type: RocketType
    region: str
    season: str  # "summer", "winter", "dry", "wet"
    compensation_policy: str  # "full", "partial", "none"
    restoration_strategy: str  # "natural", "active", "hybrid"
    inflation_rate: float  # Annual inflation rate (decimal)
    exchange_rate_volatility: float  # Exchange rate volatility (std dev)
    risk_level: str  # "low", "medium", "high"


class AdvancedEconomicAnalyzer:
    """
    Advanced economic analyzer for comprehensive damage assessment.
    
    Implements Tasks 5.4-5.5: Additional economic analysis with:
    - Sensitivity analysis of unit costs and exchange rates
    - What-if scenarios for different rocket types and impact scenarios
    - Long-term forecasts with inflation and currency changes
    - Risk assessment with probability distributions
    - Cost-benefit analysis
    
    References:
    - Task 5.4: Sensitivity analysis and what-if scenarios
    - Task 5.5: Long-term forecasts and risk assessment
    """
    
    # Default rocket types based on real-world data
    ROCKET_TYPES = {
        "proton_m": RocketType(
            name="Proton-M",
            fuel_type="UDMH",
            toxic_factor=2.5,
            impact_area_km2=15.0,
            debris_count=150,
            cleanup_complexity=1.8,
            base_cost_multiplier=1.5
        ),
        "soyuz": RocketType(
            name="Soyuz",
            fuel_type="Kerosene",
            toxic_factor=1.2,
            impact_area_km2=8.0,
            debris_count=80,
            cleanup_complexity=1.2,
            base_cost_multiplier=1.1
        ),
        "falcon_9": RocketType(
            name="Falcon 9",
            fuel_type="LOX/RP-1",
            toxic_factor=1.0,
            impact_area_km2=5.0,
            debris_count=50,
            cleanup_complexity=1.0,
            base_cost_multiplier=1.0
        ),
        "angara": RocketType(
            name="Angara",
            fuel_type="Kerosene",
            toxic_factor=1.3,
            impact_area_km2=10.0,
            debris_count=100,
            cleanup_complexity=1.3,
            base_cost_multiplier=1.2
        ),
        "long_march": RocketType(
            name="Long March",
            fuel_type="UDMH",
            toxic_factor=2.0,
            impact_area_km2=12.0,
            debris_count=120,
            cleanup_complexity=1.5,
            base_cost_multiplier=1.4
        )
    }
    
    # Default regions with environmental characteristics
    REGIONS = {
        "steppe": {
            "name": "Kazakh Steppe",
            "vegetation_density": 0.3,
            "soil_vulnerability": 0.6,
            "fire_risk": 0.7,
            "population_density": 0.1,
            "infrastructure_value": 0.3
        },
        "forest": {
            "name": "Siberian Forest",
            "vegetation_density": 0.9,
            "soil_vulnerability": 0.4,
            "fire_risk": 0.8,
            "population_density": 0.2,
            "infrastructure_value": 0.4
        },
        "desert": {
            "name": "Central Asian Desert",
            "vegetation_density": 0.1,
            "soil_vulnerability": 0.8,
            "fire_risk": 0.3,
            "population_density": 0.05,
            "infrastructure_value": 0.2
        },
        "agricultural": {
            "name": "Agricultural Zone",
            "vegetation_density": 0.7,
            "soil_vulnerability": 0.9,
            "fire_risk": 0.5,
            "population_density": 0.4,
            "infrastructure_value": 0.7
        },
        "coastal": {
            "name": "Coastal Area",
            "vegetation_density": 0.6,
            "soil_vulnerability": 0.7,
            "fire_risk": 0.4,
            "population_density": 0.5,
            "infrastructure_value": 0.8
        }
    }
    
    def __init__(self, base_calculator: Optional[EconomicDamageCalculator] = None):
        """
        Initialize advanced economic analyzer.
        
        Args:
            base_calculator: Existing EconomicDamageCalculator instance.
                             If None, creates a new one with default parameters.
        """
        self.base_calculator = base_calculator or EconomicDamageCalculator()
        self.scenarios = []
        self.results = {}
        
    def sensitivity_analysis(
        self,
        otu_results: np.ndarray,
        cell_size_km: float = 1.0,
        parameters: List[str] = None,
        variations: List[float] = None
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on economic parameters.
        
        Analyzes how changes in unit costs and exchange rates affect total damage cost.
        Uses one-at-a-time (OAT) sensitivity analysis.
        
        Args:
            otu_results: OTU stability indices array
            cell_size_km: Cell size in kilometers
            parameters: List of parameters to vary (default: all cost components)
            variations: Percentage variations to apply (-50%, -25%, 0%, +25%, +50%)
            
        Returns:
            Dictionary with sensitivity indices and results
        """
        if parameters is None:
            parameters = list(self.base_calculator.costs_kzt.keys()) + ['exchange_rate']
        
        if variations is None:
            variations = [-0.5, -0.25, 0.0, 0.25, 0.5]  # -50% to +50%
        
        # Baseline calculation
        baseline = self.base_calculator.calculate_total_damage(otu_results, cell_size_km)
        baseline_cost = baseline['grand_total_kzt']
        
        sensitivity_results = {
            'baseline': baseline_cost,
            'parameters': {},
            'elasticity': {},  # Percentage change in cost per 1% change in parameter
            'tornado_data': []  # For tornado chart
        }
        
        for param in parameters:
            param_results = []
            
            for var in variations:
                # Create modified calculator
                if param == 'exchange_rate':
                    modified_rate = self.base_calculator.usd_to_kzt * (1 + var)
                    modified_calc = EconomicDamageCalculator(usd_to_kzt=modified_rate)
                else:
                    # Modify specific cost parameter
                    modified_costs = self.base_calculator.costs_kzt.copy()
                    modified_costs[param] = modified_costs[param] * (1 + var)
                    # Create new calculator with modified costs
                    modified_calc = EconomicDamageCalculator(
                        usd_to_kzt=self.base_calculator.usd_to_kzt
                    )
                    modified_calc.costs_kzt = modified_costs
                
                # Calculate damage with modified parameters
                modified_result = modified_calc.calculate_total_damage(otu_results, cell_size_km)
                modified_cost = modified_result['grand_total_kzt']
                
                param_results.append({
                    'variation': var,
                    'cost_kzt': modified_cost,
                    'cost_change_percent': ((modified_cost - baseline_cost) / baseline_cost) * 100
                })
            
            # Calculate elasticity (average sensitivity)
            cost_changes = [r['cost_change_percent'] for r in param_results]
            param_changes = [v * 100 for v in variations]  # Convert to percentage
            elasticity = np.polyfit(param_changes, cost_changes, 1)[0] / 100  # Slope
            
            sensitivity_results['parameters'][param] = {
                'results': param_results,
                'elasticity': elasticity,
                'max_impact': max([abs(r['cost_change_percent']) for r in param_results])
            }
            
            # Add to tornado data
            max_negative = min([r['cost_change_percent'] for r in param_results])
            max_positive = max([r['cost_change_percent'] for r in param_results])
            sensitivity_results['tornado_data'].append({
                'parameter': param,
                'negative_impact': abs(max_negative),
                'positive_impact': max_positive
            })
        
        # Sort tornado data by impact magnitude
        sensitivity_results['tornado_data'].sort(
            key=lambda x: max(x['negative_impact'], x['positive_impact']),
            reverse=True
        )
        
        # Identify most sensitive parameters
        sensitivities = [(p, data['elasticity']) for p, data in sensitivity_results['parameters'].items()]
        sensitivities.sort(key=lambda x: abs(x[1]), reverse=True)
        sensitivity_results['most_sensitive'] = sensitivities[:3]
        
        return sensitivity_results
    
    def what_if_scenarios(
        self,
        otu_results: np.ndarray,
        cell_size_km: float = 1.0,
        scenario_configs: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate and analyze "what-if" scenarios for different conditions.
        
        Scenarios include different rocket types, regions, seasons, and policies.
        
        Args:
            otu_results: OTU stability indices array
            cell_size_km: Cell size in kilometers
            scenario_configs: List of scenario configurations. If None, uses default scenarios.
            
        Returns:
            Dictionary with scenario analysis results
        """
        if scenario_configs is None:
            # Generate default scenarios
            scenario_configs = self._generate_default_scenarios()
        
        scenario_results = {
            'scenarios': [],
            'comparison_table': [],
            'summary_stats': {}
        }
        
        total_costs = []
        
        for i, config in enumerate(scenario_configs):
            scenario_name = config.get('name', f'Scenario_{i+1}')
            
            # Apply scenario modifications to calculator
            modified_calc = self._apply_scenario_modifications(config)
            
            # Calculate damage
            damage_result = modified_calc.calculate_total_damage(otu_results, cell_size_km)
            
            # Adjust for scenario-specific factors
            adjusted_result = self._adjust_for_scenario_factors(damage_result, config)
            
            # Store results
            scenario_result = {
                'name': scenario_name,
                'config': config,
                'damage_result': damage_result,
                'adjusted_result': adjusted_result,
                'total_cost_kzt': adjusted_result['grand_total_kzt'],
                'total_cost_usd': adjusted_result['grand_total_usd'],
                'cost_components': {
                    'vegetation': adjusted_result['vegetation_cost_kzt'],
                    'soil': adjusted_result['soil_cost_kzt'],
                    'fire': adjusted_result['fire_cost_kzt'],
                    'contamination': adjusted_result['contamination_cost_kzt'],
                    'mechanical': adjusted_result['mechanical_cost_kzt']
                }
            }
            
            scenario_results['scenarios'].append(scenario_result)
            scenario_results['comparison_table'].append({
                'Scenario': scenario_name,
                'Total Cost (KZT)': adjusted_result['grand_total_kzt'],
                'Total Cost (USD)': adjusted_result['grand_total_usd'],
                'Cost per ha (KZT)': adjusted_result['grand_total_kzt'] / damage_result['total_area_ha'],
                'Dominant Component': max(
                    adjusted_result['percentages'].items(),
                    key=lambda x: x[1]
                )[0].replace('_pct', '')
            })
            
            total_costs.append(adjusted_result['grand_total_kzt'])
        
        # Calculate summary statistics
        if total_costs:
            scenario_results['summary_stats'] = {
                'min_cost': min(total_costs),
                'max_cost': max(total_costs),
                'mean_cost': np.mean(total_costs),
                'median_cost': np.median(total_costs),
                'std_cost': np.std(total_costs),
                'range': max(total_costs) - min(total_costs),
                'cost_ratio_max_min': max(total_costs) / min(total_costs) if min(total_costs) > 0 else float('inf')
            }
        
        return scenario_results
    
    def long_term_forecasts(
        self,
        base_damage_kzt: float,
        years: int = 10,
        inflation_rate: float = 0.05,
        exchange_rate_change: float = 0.02,
        growth_rate: float = 0.03
    ) -> Dict[str, Any]:
        """
        Generate long-term economic forecasts for damage costs.
        
        Accounts for inflation, currency exchange changes, and economic growth.
        
        Args:
            base_damage_kzt: Base damage cost in KZT (current year)
            years: Number of years to forecast
            inflation_rate: Annual inflation rate (decimal)
            exchange_rate_change: Annual change in USD/KZT exchange rate (decimal)
            growth_rate: Annual economic growth rate affecting restoration costs
            
        Returns:
            Dictionary with forecasted costs over time
        """
        forecast_data = []
        current_year = datetime.now().year
        
        # Initial values
        current_cost_kzt = base_damage_kzt
        current_exchange = self.base_calculator.usd_to_kzt
        
        for year in range(years + 1):
            year_label = current_year + year
            
            # Calculate inflation-adjusted cost
            inflation_factor = (1 + inflation_rate) ** year
            growth_factor = (1 + growth_rate) ** year
            exchange_factor = (1 + exchange_rate_change) ** year
            
            # Forecasted costs
            nominal_cost_kzt = base_damage_kzt * inflation_factor * growth_factor
            real_cost_kzt = base_damage_kzt * growth_factor  # Adjusted for real growth
            forecast_exchange = current_exchange * exchange_factor
            cost_usd = nominal_cost_kzt / forecast_exchange
            
            # Calculate present value (discounted)
            discount_rate = 0.07  # Standard discount rate for public projects
            present_value = nominal_cost_kzt / ((1 + discount_rate) ** year)
            
            forecast_data.append({
                'year': year_label,
                'year_index': year,
                'nominal_cost_kzt': nominal_cost_kzt,
                'real_cost_kzt': real_cost_kzt,
                'cost_usd': cost_usd,
                'exchange_rate': forecast_exchange,
                'inflation_factor': inflation_factor,
                'growth_factor': growth_factor,
                'present_value_kzt': present_value,
                'cumulative_nominal': sum([d['nominal_cost_kzt'] for d in forecast_data]),
                'cumulative_present_value': sum([d['present_value_kzt'] for d in forecast_data])
            })
        
        # Calculate summary metrics
        total_nominal = sum(d['nominal_cost_kzt'] for d in forecast_data[1:])  # Exclude year 0
        total_present_value = sum(d['present_value_kzt'] for d in forecast_data[1:])
        avg_annual_growth = (forecast_data[-1]['nominal_cost_kzt'] / base_damage_kzt) ** (1/years) - 1
        
        forecast_results = {
            'base_year': current_year,
            'base_damage_kzt': base_damage_kzt,
            'forecast_horizon_years': years,
            'assumptions': {
                'inflation_rate': inflation_rate,
                'exchange_rate_change': exchange