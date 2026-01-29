"""
Task 2.1: Sensitivity Analysis - One-At-a-Time (OAT)

Implements БЛОК 2, Task 2.1 from revision plan.
Performs OAT sensitivity analysis for Q_OTU calculation.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import sys
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'sensitivity_analysis_oat.log', encoding='utf-8'),
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

class OATSensitivityAnalyzer:
    """
    One-At-a-Time sensitivity analyzer for Q_OTU.
    """
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] OATSensitivityAnalyzer initialized")
        
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
        
        # Define variation ranges (±30% as per requirements)
        self.variation_range = 0.30  # ±30%
        
        logger.info(f"[INFO] Baseline parameters: Q_VI={self.baseline.q_vi}, Q_SI={self.baseline.q_si}, "
                   f"Q_BI={self.baseline.q_bi}, Q_Relief={self.baseline.q_relief}")
        logger.info(f"[INFO] Variation range: ±{self.variation_range*100:.0f}%")
    
    def vary_parameter(self, param_name: str, n_points: int = 21) -> List[float]:
        """Generate variation values for a parameter."""
        baseline_value = getattr(self.baseline, param_name)
        
        # For weights, vary around baseline (weights sum to 1, so careful)
        if param_name.startswith('k_'):
            # Vary weight while keeping others proportional
            min_val = max(0.0, baseline_value * (1 - self.variation_range))
            max_val = min(1.0, baseline_value * (1 + self.variation_range))
        else:
            # For Q values (0-1), vary within bounds
            min_val = max(0.0, baseline_value * (1 - self.variation_range))
            max_val = min(1.0, baseline_value * (1 + self.variation_range))
        
        return np.linspace(min_val, max_val, n_points).tolist()
    
    def compute_sensitivity(self, param_name: str) -> pd.DataFrame:
        """Compute sensitivity for a single parameter."""
        logger.info(f"[PROCESS] Computing sensitivity for {param_name}")
        
        # Generate variation values
        values = self.vary_parameter(param_name)
        
        records = []
        baseline_q_otu = compute_q_otu(self.baseline)
        
        for val in values:
            # Create modified parameters
            modified_params = OTUParameters(
                q_vi=self.baseline.q_vi,
                q_si=self.baseline.q_si,
                q_bi=self.baseline.q_bi,
                q_relief=self.baseline.q_relief,
                k_vi=self.baseline.k_vi,
                k_si=self.baseline.k_si,
                k_bi=self.baseline.k_bi
            )
            
            # Set the varied parameter
            setattr(modified_params, param_name, val)
            
            # Compute Q_OTU
            q_otu = compute_q_otu(modified_params)
            
            # Calculate change
            absolute_change = q_otu - baseline_q_otu
            relative_change = (absolute_change / baseline_q_otu * 100) if baseline_q_otu > 0 else 0
            
            records.append({
                'Parameter': param_name,
                'Value': val,
                'Q_OTU': q_otu,
                'Baseline_Q_OTU': baseline_q_otu,
                'Absolute_Change': absolute_change,
                'Relative_Change_%': relative_change,
                'Variation_%': ((val - getattr(self.baseline, param_name)) / 
                               getattr(self.baseline, param_name) * 100) if getattr(self.baseline, param_name) > 0 else 0
            })
        
        df = pd.DataFrame(records)
        logger.info(f"[OK] Sensitivity computed for {param_name}: {len(df)} points")
        return df
    
    def compute_all_sensitivities(self) -> Dict[str, pd.DataFrame]:
        """Compute sensitivity for all parameters."""
        logger.info("[PROCESS] Computing sensitivities for all parameters")
        
        parameters = ['q_vi', 'q_si', 'q_bi', 'q_relief', 'k_vi', 'k_si', 'k_bi']
        results = {}
        
        for param in parameters:
            results[param] = self.compute_sensitivity(param)
        
        logger.info(f"[OK] All sensitivities computed: {len(parameters)} parameters")
        return results
    
    def calculate_reclassification_rates(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate reclassification rates based on Q_OTU thresholds."""
        logger.info("[PROCESS] Calculating reclassification rates")
        
        # Define stability classes based on Q_OTU
        stability_classes = {
            'Very Low': (0.0, 0.2),
            'Low': (0.2, 0.4),
            'Moderate': (0.4, 0.6),
            'High': (0.6, 0.8),
            'Very High': (0.8, 1.0)
        }
        
        baseline_q_otu = compute_q_otu(self.baseline)
        
        # Determine baseline class
        baseline_class = None
        for class_name, (min_val, max_val) in stability_classes.items():
            if min_val <= baseline_q_otu < max_val:
                baseline_class = class_name
                break
        
        records = []
        for param_name, df in results.items():
            # Count reclassifications
            reclassifications = 0
            total_points = len(df)
            
            for _, row in df.iterrows():
                q_otu = row['Q_OTU']
                # Determine class for this Q_OTU
                current_class = None
                for class_name, (min_val, max_val) in stability_classes.items():
                    if min_val <= q_otu < max_val:
                        current_class = class_name
                        break
                
                if current_class != baseline_class:
                    reclassifications += 1
            
            reclassification_rate = (reclassifications / total_points) * 100
            
            # Calculate sensitivity index (absolute change per % variation)
            mean_abs_change = df['Absolute_Change'].abs().mean()
            mean_variation = df['Variation_%'].abs().mean()
            sensitivity_index = mean_abs_change / mean_variation if mean_variation > 0 else 0
            
            records.append({
                'Parameter': param_name,
                'Baseline_Class': baseline_class,
                'Reclassification_Rate_%': reclassification_rate,
                'Mean_Absolute_Change': mean_abs_change,
                'Sensitivity_Index': sensitivity_index,
                'Max_Absolute_Change': df['Absolute_Change'].abs().max(),
                'Parameter_Type': 'Weight' if param_name.startswith('k_') else 'Quality_Index'
            })
        
        result_df = pd.DataFrame(records)
        result_df = result_df.sort_values('Sensitivity_Index', ascending=False).reset_index(drop=True)
        
        logger.info(f"[OK] Reclassification rates calculated for {len(result_df)} parameters")
        return result_df
    
    def create_sensitivity_plots(self, results: Dict[str, pd.DataFrame], output_dir: Path):
        """Create sensitivity plots."""
        logger.info("[PROCESS] Creating sensitivity plots")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create individual parameter plots
        for param_name, df in results.items():
            plt.figure(figsize=(10, 6))
            
            # Plot Q_OTU vs parameter value
            plt.plot(df['Value'], df['Q_OTU'], 'b-', linewidth=2, label='Q_OTU')
            plt.axhline(y=df['Baseline_Q_OTU'].iloc[0], color='r', linestyle='--', 
                       label=f'Baseline Q_OTU = {df["Baseline_Q_OTU"].iloc[0]:.3f}')
            plt.axvline(x=getattr(self.baseline, param_name), color='g', linestyle='--',
                       label=f'Baseline {param_name} = {getattr(self.baseline, param_name):.3f}')
            
            plt.xlabel(f'{param_name} Value', fontsize=12)
            plt.ylabel('Q_OTU', fontsize=12)
            plt.title(f'Sensitivity Analysis: Q_OTU vs {param_name}', fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            plot_path = output_dir / f'sensitivity_{param_name}.png'
            plt.savefig(plot_path, dpi=300)
            plt.close()
            
            logger.info(f"[OK] Plot saved: {plot_path}")
        
        # Create summary plot (all parameters)
        plt.figure(figsize=(12, 8))
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(results)))
        
        for idx, (param_name, df) in enumerate(results.items()):
            # Normalize values for comparison
            normalized_values = (df['Value'] - df['Value'].min()) / (df['Value'].max() - df['Value'].min())
            plt.plot(normalized_values, df['Q_OTU'], color=colors[idx], linewidth=2, label=param_name)
        
        plt.xlabel('Normalized Parameter Value (0=min, 1=max)', fontsize=12)
        plt.ylabel('Q_OTU', fontsize=12)
        plt.title('Comparative Sensitivity Analysis: All Parameters', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        plt.tight_layout()
        
        summary_plot_path = output_dir / 'sensitivity_summary.png'
        plt.savefig(summary_plot_path, dpi=300)
        plt.close()
        
        logger.info(f"[OK] Summary plot saved: {summary_plot_path}")
    
    def save_results(self, results: Dict[str, pd.DataFrame], reclassification_df: pd.DataFrame, output_dir: Path):
        """Save all results to files."""
        logger.info(f"[SAVE] Saving sensitivity results to {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results for each parameter
        detailed_dir = output_dir / "detailed_results"
        detailed_dir.mkdir(exist_ok=True)
        
        for param_name, df in results.items():
            csv_path = detailed_dir / f"sensitivity_{param_name}.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"[OK] Detailed results saved: {csv_path}")
        
        # Save reclassification rates
        reclassification_path = output_dir / "reclassification_rates.csv"
        reclassification_df.to_csv(reclassification_path, index=False)
        logger.info(f"[OK] Reclassification rates saved: {reclassification_path}")
        
        # Save summary Excel file
        excel_path = output_dir / "sensitivity_analysis_results.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            reclassification_df.to_excel(writer, sheet_name='Reclassification_Rates', index=False)
            
            # Add parameter summaries
            summary_data = []
            for param_name, df in results.items():
                summary_data.append({
                    'Parameter': param_name,
                    'Min_Q_OTU': df['Q_OTU'].min(),
                    'Max_Q_OTU': df['Q_OTU'].max(),
                    'Range_Q_OTU': df['Q_OTU'].max() - df['Q_OTU'].min(),
                    'Mean_Absolute_Change': df['Absolute_Change'].abs().mean(),
                    'Max_Absolute_Change': df['Absolute_Change'].abs().max()
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Parameter_Summary', index=False)
            
            # Add baseline information
            baseline_df = pd.DataFrame([{
                'Parameter': 'Baseline',
                'Q_VI': self.baseline.q_vi,
                'Q_SI': self.baseline.q_si,
                'Q_BI': self.baseline.q_bi,
                'Q_Relief': self.baseline.q_relief,
                'k_VI': self.baseline.k_vi,
                'k_SI': self.baseline.k_si,
                'k_BI': self.baseline.k_bi,
                'Q_OTU': compute_q_otu(self.baseline)
            }])
            baseline_df.to_excel(writer, sheet_name='Baseline_Parameters', index=False)
        
        logger.info(f"[OK] Excel summary saved: {excel_path}")
        
        # Save LaTeX table
        latex_path = output_dir / "reclassification_rates.tex"
        latex_content = reclassification_df.to_latex(
            index=False,
            caption='Reclassification rates from OAT sensitivity analysis (±30% variation)',
            label='tab:sensitivity_oat_reclassification',
            column_format='lcccccc',
            float_format='%.3f'
        )
        
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        logger.info(f"[OK] LaTeX table saved: {latex_path}")
        
        # Save JSON metadata
        metadata = {
            'analysis_type': 'OAT (One-At-a-Time)',
            'variation_range': self.variation_range,
            'baseline_parameters': {
                'q_vi': float(self.baseline.q_vi),
                'q_si': float(self.baseline.q_si),
                'q_bi': float(self.baseline.q_bi),
                'q_relief': float(self.baseline.q_relief),
                'k_vi': float(self.baseline.k_vi),
                'k_si': float(self.baseline.k_si),
                'k_bi': float(self.baseline.k_bi),
                'q_otu': float(compute_q_otu(self.baseline))
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'processing_time_seconds': time.time() - self.start_time
        }
        
        metadata_path = output_dir / "analysis_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"[OK] Metadata saved: {metadata_path}")
    
    def generate_report(self) -> str:
        """Generate processing report."""
        elapsed_time = time.time() - self.start_time
        
        report = f"""
        ============================================
        OAT SENSITIVITY ANALYSIS PROCESSING REPORT
        ============================================
        Processing time: {elapsed_time:.2f} seconds
        Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}
        End time: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        ANALYSIS PARAMETERS:
        - Method: One-At-a-Time (OAT)
        - Variation range: ±{self.variation_range*100:.0f}%
        - Parameters analyzed: Q_VI, Q_SI, Q_BI, Q_Relief, k_VI, k_SI, k_BI
        - Baseline Q_OTU: {compute_q_otu(self.baseline):.3f}
        - Stability classes: Very Low (0-0.2), Low (0.2-0.4), Moderate (0.4-0.6),
          High (0.6-0.8), Very High (0.8-1.0)
        
        OUTPUT FILES GENERATED:
        - sensitivity_analysis_results.xlsx (Excel summary)
        - reclassification_rates.csv (main results)
        - reclassification_rates.tex (LaTeX table)
        - sensitivity_*.png (individual parameter plots)
        - sensitivity_summary.png (comparative plot)
        - detailed_results/ (CSV files for each parameter)
        - analysis_metadata.json (analysis parameters)
        
        KEY METRICS:
        - Reclassification rates calculated for all 7 parameters
        - Sensitivity indices computed (change in Q_OTU per % variation)
        - Maximum absolute changes recorded
        - Parameter ranking by sensitivity
        
        PROCESSING STEPS:
        1. Initialized analyzer with baseline OTU parameters
        2. Generated parameter variations (±30%)
        3. Computed Q_OTU for all variations
        4. Calculated reclassification rates across stability classes
        5. Generated sensitivity plots
        6. Saved results in multiple formats (Excel, CSV, LaTeX, PNG)
        
        STATUS: COMPLETED SUCCESSFULLY
        ============================================
        """
        
        logger.info("[REPORT] Processing report generated")
        return report

def main():
    """Main execution function."""
    print("=" * 60)
    print("Task 2.1: Sensitivity Analysis - OAT (One-At-a-Time)")
    print("=" * 60)
    print("Implements BLOCK 2, Task 2.1 from revision plan")
    print("Variation: ±30% for all parameters")
    print()
    
    # Create output directory
    output_dir = Path("outputs/sensitivity_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize analyzer
    logger.info("[MAIN] Starting OAT sensitivity analysis")
    analyzer = OATSensitivityAnalyzer()
    
    try:
        # Step 1: Compute all sensitivities
        logger.info("[MAIN] Step 1: Computing sensitivities for all parameters")
        results = analyzer.compute_all_sensitivities()
        
        # Step 2: Calculate reclassification rates
        logger.info("[MAIN] Step 2: Calculating reclassification rates")
        reclassification_df = analyzer.calculate_reclassification_rates(results)
        
        # Step 3: Create plots
        logger.info("[MAIN] Step 3: Creating sensitivity plots")
        plots_dir = output_dir / "plots"
        analyzer.create_sensitivity_plots(results, plots_dir)
        
        # Step 4: Save results
        logger.info("[MAIN] Step 4: Saving results to files")
        analyzer.save_results(results, reclassification_df, output_dir)
        
        # Step 5: Generate report
        logger.info("[MAIN] Step 5: Generating processing report")
        report = analyzer.generate_report()
        
        # Print report
        print(report)
        
        # Save report to file
        report_path = output_dir / "oat_sensitivity_analysis_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"[MAIN] Report saved to {report_path}")
        
        # Print summary of results
        print("\n" + "=" * 60)
        print("SENSITIVITY ANALYSIS SUMMARY")
        print("=" * 60)
        print("Parameter ranking by sensitivity (highest to lowest):")
        print()
        
        for idx, row in reclassification_df.iterrows():
            print(f"{idx+1}. {row['Parameter']}:")
            print(f"   Reclassification rate: {row['Reclassification_Rate_%']:.1f}%")
            print(f"   Sensitivity index: {row['Sensitivity_Index']:.4f}")
            print(f"   Max absolute change: {row['Max_Absolute_Change']:.3f}")
            print()
        
        print(f"Output files saved to: {output_dir}")
        print("Check logs/sensitivity_analysis_oat.log for detailed processing log")
        
    except Exception as e:
        logger.error(f"[ERROR] Processing failed: {e}")
        print(f"[ERROR] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)