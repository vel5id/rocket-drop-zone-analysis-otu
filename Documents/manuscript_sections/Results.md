# Results

## 3.1 OTU Distribution

The OTU analysis reveals significant spatial variation in terrain 
stability across the study area. Figure 1 shows the OTU classification 
map, with colors representing the five stability classes. Approximately 
32% of the area (48,000 km²) was classified as High or Very High 
stability, primarily located in the northern plains with gentle 
topography and moderate vegetation cover.

Areas with Very Low stability (18% of total) was concentrated in 
mountainous regions with steep slopes and in arid southern zones 
with sparse vegetation. These areas poses the highest environmental 
risk for rocket stage impacts.

## 3.2 Index Contributions

Analysis of individual index contributions to the OTU score shows 
that relief complexity (RCI) was the most influential factor, 
accounting for 35% of the variance in OTU scores. This indicates 
that topographic characteristics plays a crucial role in determining 
suitability for controlled re-entries.

Vegetation cover (NDVI) contributes 28% to the OTU score, while 
soil stability (SI) accounts for 22%. Biodiversity (BI) and fire 
hazard (FHI) contributes 10% and 5% respectively. These relative 
contributions reflects the weighting scheme established through 
the analytical hierarchy process.

## 3.3 Validation Results

Comparison with historical impact sites shows strong agreement 
between OTU predictions and actual impact outcomes. Of the 87 
documented impact sites, 73 (84%) was located in areas predicted 
as Low or Very Low stability by the OTU model. This represents 
significant improvement over random selection (p < 0.001).

Statistical validation metrics indicates good model performance:
- Correlation coefficient (r) between predicted and observed 
  stability: 0.78
- Root mean square error (RMSE): 0.15
- Cohen's kappa (κ) for classification agreement: 0.65

Field surveys at 15 representative locations confirms the OTU 
classifications in 13 cases (87% accuracy). The two discrepancies 
was attributed to local factors not captured by the satellite 
data, such as subsurface rock formations.

## 3.4 Economic Implications

Economic analysis based on the OTU classifications suggests 
substantial cost savings from targeted site selection. Using 
historical cost data from cleanup operations, we estimates that:

- Impacts in Very High stability areas results in average 
  cleanup costs of $12,000 per hectare
- Impacts in Very Low stability areas results in average 
  cleanup costs of $48,000 per hectare
- Implementing OTU-based site selection could reduce total 
  cleanup costs by 40% compared to current practices

For a typical rocket stage re-entry affecting 100 hectares, 
OTU-guided selection could save approximately $1.4 million 
per event. Extrapolated to annual launch rates from Baikonur 
(approximately 15 launches), potential annual savings exceeds 
$20 million.

## 3.5 Sensitivity Analysis

Sensitivity analysis reveals that the OTU model is most 
sensitive to changes in the relief complexity weight (w₄). 
A 10% increase in w₄ changes the classification of 8% of 
pixels, primarily shifting areas from Moderate to High 
stability classes.

The model shows moderate sensitivity to vegetation weight 
(w₁) and low sensitivity to fire hazard weight (w₅). These 
findings suggests that topographic data quality is critical 
for reliable OTU assessment.