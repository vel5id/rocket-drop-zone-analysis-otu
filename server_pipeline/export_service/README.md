# Report Export Service

This module is responsible for generating comprehensive ecological and economic assessment reports for the Rocket Drop Zone Analysis system.

## 📦 Features

- **Automated Data Retrieval**: Fetches Sentinel-2 imagery and JRC Global Surface Water data via Google Earth Engine (GEE).
- **Intelligent Classification**:
  - **Vegetation**: Uses Q_Vi (NDVI proxy) to classify 7 distinct vegetation types.
  - **Soil**: Classifies soil mechanics based on Q_Si (Mechanical Strength Index).
  - **Stability**: Automatically assesses landing safety (High/Moderate/Low/Unstable).
- **Economic Modeling**: Calculates restoration costs based on biomass, soil degradation, and fire risks.
- **Reporting**: Generates a ZIP archive containing 10 detailed CSV tables.

## 📂 Structure

- **`generator.py`**: Main orchestrator. Handles data aggregation, classification logic, and CSV generation.
- **`gee_fetcher.py`**: Interface for Google Earth Engine. Handles batching, Sentinel-2 metadata fetching, and water distance calculations.
- **`economics.py`**: Implements the cost estimation logic (V2.1 Methodology).
- **`models.py`**: Pydantic models for type safety and API request/response validation.

## 🚀 Usage

The service is exposed via the main API:

```http
POST /api/export/generate
Content-Type: application/json

{
    "job_id": "YOUR_JOB_ID"
}
```

## 🛠Dependencies

- `earthengine-api`
- `pandas`
- `numpy`
- `pydantic`

## 📊 Output Files

1. `1_otu_extended_analysis.csv` - Master table with all cell data.
2. `2_sentinel2_metadata.csv` - Source imagery details.
3. `3_otu_summary_stats.csv` - Aggregated stability/cost stats.
4. `4_weight_coefficients.csv` - Reference of model weights.
5. `5_economic_summary.csv` - Cost breakdown by category.
6. `6_sensitivity_analysis.csv` - Cost impact scenarios (±20%).
7. `7_vegetation_legend.csv` - Classification reference.
8. `8_soil_summary.csv` - Soil index stats.
9. `9_relief_summary.csv` - Elevation/Water distance stats.
10. `10_input_parameters.csv` - Job metadata.
