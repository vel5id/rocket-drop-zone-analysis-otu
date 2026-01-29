"""
Script for creating comprehensive economic scenarios for different rocket types.

This script generates detailed scenarios for Tasks 5.4-5.5 including:
- Different rocket types (Proton-M, Soyuz, Falcon 9, etc.)
- Different regions with varying environmental conditions
- Seasonal variations
- Different compensation policies and restoration strategies
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from datetime import datetime

# Rocket type definitions
ROCKET_SCENARIOS = [
    {
        'name': 'Proton-M Impact in Kazakh Steppe',
        'rocket': 'Proton-M',
        'fuel': 'UDMH',
        'toxic_factor': 2.5,
        'impact_area_km2': 15.0,
        'region': 'steppe',
        'season': 'summer',
        'compensation': 'partial',
        'restoration': 'active',
        'risk_level': 'high'
    },
    {
        'name': 'Soyuz Impact in Siberian Forest',
        'rocket': 'Soyuz',
        'fuel': 'Kerosene',
        'toxic_factor': 1.2,
        'impact_area_km2': 8.0,
        'region': 'forest',
        'season': 'spring',
        'compensation': 'full',
        'restoration': 'hybrid',
        'risk_level': 'medium'
    },
    {
        'name': 'Falcon 9 Impact in Central Asian Desert',
        'rocket': 'Falcon 9',
        'fuel': 'LOX/RP-1',
        'toxic_factor': 1.0,
        'impact_area_km2': 5.0,
        'region': 'desert',
        'season': 'winter',
        'compensation': 'full',
        'restoration': 'natural',
        'risk_level': 'low'
    },
    {
        'name': 'Angara Impact in Agricultural Zone',
        'rocket': 'Angara',
        'fuel': 'Kerosene',
        'toxic_factor': 1.3,
        'impact_area_km2': 10.0,
        'region': 'agricultural',
        'season': 'summer',
        'compensation': 'full',
        'restoration': 'active',
        'risk_level': 'high'
    },
    {
        'name': 'Long March Impact in Coastal Area',
        'rocket': 'Long March',
        'fuel': 'UDMH',
        'toxic_factor': 2.0,
        'impact_area_km2': 12.0,
        'region': 'coastal',
        'season': 'fall',
        'compensation': 'partial',
        'restoration': 'hybrid',
        'risk_level': 'high'
    }
]

# Region characteristics
REGION_CHARACTERISTICS = {
    'steppe': {
        'name': 'Kazakh Steppe',
        'vegetation_density': 0.3,
        'soil_vulnerability': 0.6,
        'fire_risk': 0.7,
        'population_density': 0.1,
        'infrastructure_value': 0.3,
        'base_cost_multiplier': 1.0
    },
    'forest': {
        'name': 'Siberian Forest',
        'vegetation_density': 0.9,
        'soil_vulnerability': 0.4,
        'fire_risk': 0.8,
        'population_density': 0.2,
        'infrastructure_value': 0.4,
        'base_cost_multiplier': 1.2
    },
    'desert': {
        'name': 'Central Asian Desert',
        'vegetation_density': 0.1,
        'soil_vulnerability': 0.8,
        'fire_risk': 0.3,
        'population_density': 0.05,
        'infrastructure_value': 0.2,
        'base_cost_multiplier': 0.8
    },
    'agricultural': {
        'name': 'Agricultural Zone',
        'vegetation_density': 0.7,
        'soil_vulnerability': 0.9,
        'fire_risk': 0.5,
        'population_density': 0.4,
        'infrastructure_value': 0.7,
        'base_cost_multiplier': 1.5
    },
    'coastal': {
        'name': 'Coastal Area',
        'vegetation_density': 0.6,
        'soil_vulnerability': 0.7,
        'fire_risk': 0.4,
        'population_density': 0.5,
        'infrastructure_value': 0.8,
        'base_cost_multiplier': 1.3
    }
}

# Season multipliers
SEASON_MULTIPLIERS = {
    'summer': {'vegetation': 1.2, 'fire': 1.5, 'contamination': 1.1},
    'winter': {'vegetation': 0.8, 'fire': 0.5, 'contamination': 1.3},
    'spring': {'vegetation': 1.1, 'fire': 1.2, 'contamination': 1.0},
    'fall': {'vegetation': 1.0, 'fire': 1.1, 'contamination': 1.2},
    'dry': {'vegetation': 0.9, 'fire': 1.4, 'contamination': 1.1},
    'wet': {'vegetation': 1.1, 'fire': 0.7, 'contamination': 1.4}
}

# Compensation policy adjustments
COMPENSATION_ADJUSTMENTS = {
    'full': 1.0,    # 100% compensation
    'partial': 0.5, # 50% compensation
    'none': 0.0     # 0% compensation
}

# Restoration strategy efficiencies
RESTORATION_EFFICIENCIES = {
    'natural': {'cost_multiplier': 0.7, 'time_multiplier': 2.0},
    'active': {'cost_multiplier': 1.5, 'time_multiplier': 0.5},
    'hybrid': {'cost_multiplier': 1.0, 'time_multiplier': 1.0}
}


def calculate_scenario_costs(scenario):
    """Calculate estimated costs for a given scenario."""
    rocket = scenario['rocket']
    region = REGION_CHARACTERISTICS[scenario['region']]
    season = scenario['season']
    
    # Base costs (in million KZT)
    base_costs = {
        'vegetation': 50.0,
        'soil': 40.0,
        'fire': 30.0,
        'contamination': 60.0,
        'mechanical': 35.0
    }
    
    # Apply rocket-specific adjustments
    rocket_multipliers = {
        'Proton-M': 1.5,
        'Soyuz': 1.1,
        'Falcon 9': 1.0,
        'Angara': 1.2,
        'Long March': 1.4
    }
    
    rocket_mult = rocket_multipliers.get(rocket, 1.0)
    
    # Apply region adjustments
    region_mult = region['base_cost_multiplier']
    
    # Apply season adjustments
    season_adj = SEASON_MULTIPLIERS.get(season, {'vegetation': 1.0, 'fire': 1.0, 'contamination': 1.0})
    
    # Calculate component costs
    costs = {}
    for component, base in base_costs.items():
        multiplier = rocket_mult * region_mult
        
        # Apply season-specific adjustments
        if component == 'vegetation':
            multiplier *= season_adj['vegetation']
        elif component == 'fire':
            multiplier *= season_adj['fire']
        elif component == 'contamination':
            multiplier *= season_adj['contamination']
        
        # Apply toxic factor for contamination
        if component == 'contamination':
            multiplier *= scenario['toxic_factor']
        
        costs[component] = base * multiplier
    
    # Apply restoration strategy
    restoration = RESTORATION_EFFICIENCIES[scenario['restoration']]
    total_cost = sum(costs.values()) * restoration['cost_multiplier']
    
    # Apply compensation policy
    compensation = COMPENSATION_ADJUSTMENTS[scenario['compensation']]
    net_cost = total_cost * (1 - compensation)
    
    return {
        'scenario_name': scenario['name'],
        'rocket': rocket,
        'region': region['name'],
        'season': season,
        'compensation': scenario['compensation'],
        'restoration': scenario['restoration'],
        'risk_level': scenario['risk_level'],
        'component_costs': costs,
        'total_cost_million_kzt': total_cost,
        'net_cost_million_kzt': net_cost,
        'restoration_time_years': 5.0 * restoration['time_multiplier']
    }


def generate_scenario_report():
    """Generate comprehensive scenario analysis report."""
    print("Generating economic scenario analysis...")
    
    # Calculate costs for all scenarios
    scenario_results = []
    for scenario in ROCKET_SCENARIOS:
        result = calculate_scenario_costs(scenario)
        scenario_results.append(result)
    
    # Create DataFrame for analysis
    df_scenarios = pd.DataFrame([
        {
            'Scenario': r['scenario_name'],
            'Rocket': r['rocket'],
            'Region': r['region'],
            'Season': r['season'],
            'Risk Level': r['risk_level'],
            'Total Cost (M KZT)': r['total_cost_million_kzt'],
            'Net Cost (M KZT)': r['net_cost_million_kzt'],
            'Restoration Time (years)': r['restoration_time_years'],
            'Compensation': r['compensation'],
            'Restoration Strategy': r['restoration']
        }
        for r in scenario_results
    ])
    
    # Create output directory
    os.makedirs('outputs/economic/advanced', exist_ok=True)
    
    # Save to Excel
    excel_path = 'outputs/economic/advanced/Economic_Scenarios_Analysis.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_scenarios.to_excel(writer, sheet_name='Scenario_Summary', index=False)
        
        # Detailed cost breakdown
        detailed_data = []
        for r in scenario_results:
            for component, cost in r['component_costs'].items():
                detailed_data.append({
                    'Scenario': r['scenario_name'],
                    'Component': component,
                    'Cost (M KZT)': cost,
                    'Percentage': (cost / r['total_cost_million_kzt']) * 100
                })
        
        df_detailed = pd.DataFrame(detailed_data)
        df_detailed.to_excel(writer, sheet_name='Cost_Breakdown', index=False)
        
        # Risk analysis
        risk_data = []
        for r in scenario_results:
            risk_score = {'low': 1, 'medium': 2, 'high': 3}.get(r['risk_level'], 1)
            risk_data.append({
                'Scenario': r['scenario_name'],
                'Risk Level': r['risk_level'],
                'Risk Score': risk_score,
                'Cost per Risk Score': r['total_cost_million_kzt'] / risk_score
            })
        
        df_risk = pd.DataFrame(risk_data)
        df_risk.to_excel(writer, sheet_name='Risk_Analysis', index=False)
    
    print(f"✓ Scenario analysis saved to {excel_path}")
    
    # Create visualizations
    create_scenario_visualizations(scenario_results)
    
    # Generate markdown report
    generate_markdown_report(scenario_results, df_scenarios)
    
    return scenario_results


def create_scenario_visualizations(scenario_results):
    """Create visualizations for scenario analysis."""
    print("Creating scenario visualizations...")
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Total costs by scenario
    plt.subplot(2, 2, 1)
    scenarios = [r['scenario_name'] for r in scenario_results]
    total_costs = [r['total_cost_million_kzt'] for r in scenario_results]
    net_costs = [r['net_cost_million_kzt'] for r in scenario_results]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    plt.bar(x - width/2, total_costs, width, label='Total Cost', color='steelblue')
    plt.bar(x + width/2, net_costs, width, label='Net Cost (after compensation)', color='lightcoral')
    
    plt.xlabel('Scenario')
    plt.ylabel('Cost (Million KZT)')
    plt.title('Economic Impact by Scenario')
    plt.xticks(x, scenarios, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Cost components for worst-case scenario
    plt.subplot(2, 2, 2)
    worst_case = max(scenario_results, key=lambda x: x['total_cost_million_kzt'])
    components = list(worst_case['component_costs'].keys())
    component_costs = list(worst_case['component_costs'].values())
    
    colors = ['green', 'brown', 'red', 'purple', 'gray']
    plt.pie(component_costs, labels=components, colors=colors, autopct='%1.1f%%')
    plt.title(f'Cost Breakdown: {worst_case["scenario_name"]}')
    
    # Plot 3: Restoration time vs cost
    plt.subplot(2, 2, 3)
    times = [r['restoration_time_years'] for r in scenario_results]
    costs = [r['total_cost_million_kzt'] for r in scenario_results]
    
    # Color by risk level
    colors = {'low': 'green', 'medium': 'orange', 'high': 'red'}
    point_colors = [colors[r['risk_level']] for r in scenario_results]
    
    plt.scatter(times, costs, c=point_colors, s=100, alpha=0.7)
    
    # Add labels
    for i, r in enumerate(scenario_results):
        plt.annotate(r['rocket'], (times[i], costs[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.xlabel('Restoration Time (years)')
    plt.ylabel('Total Cost (Million KZT)')
    plt.title('Cost vs Time by Rocket Type')
    plt.grid(True, alpha=0.3)
    
    # Add legend for risk levels
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Low Risk'),
        Patch(facecolor='orange', label='Medium Risk'),
        Patch(facecolor='red', label='High Risk')
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    # Plot 4: Comparison of compensation policies
    plt.subplot(2, 2, 4)
    compensation_types = ['full', 'partial', 'none']
    avg_costs = []
    
    for comp in compensation_types:
        comp_scenarios = [r for r in scenario_results if r['compensation'] == comp]
        if comp_scenarios:
            avg_cost = np.mean([r['net_cost_million_kzt'] for r in comp_scenarios])
            avg_costs.append(avg_cost)
        else:
            avg_costs.append(0)
    
    plt.bar(compensation_types, avg_costs, color=['lightgreen', 'lightblue', 'lightcoral'])
    plt.xlabel('Compensation Policy')
    plt.ylabel('Average Net Cost (Million KZT)')
    plt.title('Impact of Compensation Policies')
    plt.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(avg_costs):
        plt.text(i, v + 5, f'{v:.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save figure
    viz_path = 'outputs/economic/advanced/Economic_Scenario_Visualizations.png'
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Visualizations saved to {viz_path}")


def generate_markdown_report(scenario_results, df_scenarios):
    """Generate markdown report for scenario analysis."""
    print("Generating markdown report...")
    
    report = f"""# Economic Scenario Analysis Report

## Tasks 5.4-5.5: Comprehensive Economic Analysis
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report analyzes economic impacts for different rocket impact scenarios, considering:
- **5 different rocket types** (Proton-M, Soyuz, Falcon 9, Angara, Long March)
- **5 different regions** with varying environmental characteristics  
- **Seasonal variations** affecting restoration costs
- **Different compensation policies** and restoration strategies

### Key Findings

1. **Worst-case scenario**: {max(scenario_results, key=lambda x: x['total_cost_million_kzt'])['scenario_name']}
   - Total cost: {max([r['total_cost_million_kzt'] for r in scenario_results]):.1f} million KZT
   - Primary cost driver: Contamination cleanup

2. **Best-case scenario**: {min(scenario_results, key=lambda x: x['total_cost_million_kzt'])['scenario_name']}
   - Total cost: {min([r['total_cost_million_kzt'] for r in scenario_results]):.1f} million KZT
   - Advantage: Lower toxic fuel and favorable environment

3. **Average restoration cost**: {np.mean([