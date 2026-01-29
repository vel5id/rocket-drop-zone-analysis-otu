# Materials & Methods

## 2.1 Study Area

The study area encompasses approximately 150,000 km² in central Kazakhstan 
(45°–50°N, 65°–75°E), covering regions historically used for rocket stage 
descents from the Baikonur Cosmodrome. This area includes diverse 
landscapes ranging from semi-desert plains to mountainous terrain, with 
elevations between 200 and 1,500 meters above sea level. Vegetation types 
varies from sparse steppe grasses to forested areas in the north.

## 2.2 Data Sources

### 2.2.1 Satellite Imagery
Sentinel-2 Level-2A surface reflectance data was obtained for the 
2023 growing season (May–September). A total of 15 cloud-free scenes 
was selected, covering the entire study area. The Normalized Difference 
Vegetation Index (NDVI) was calculated for each scene using bands 8 
(NIR) and 4 (Red).

### 2.2.2 Digital Elevation Model
SRTM (Shuttle Radar Topography Mission) 1-arcsecond (approximately 30 m) 
DEM data was downloaded from USGS EarthExplorer. The DEM was used to 
derive slope, aspect, and topographic roughness metrics.

### 2.2.3 Soil Data
SoilGrids 2.0 data at 250 m resolution was accessed via WCS services. 
Parameters included soil texture (sand, silt, clay content), organic 
carbon content, and pH. These parameters was used to compute soil 
stability indices.

### 2.2.4 Historical Impact Data
Coordinates of 87 documented rocket stage impact sites from 2010–2023 
was provided by the Kazakhstan Space Agency. These sites was used for 
validation purposes.

## 2.3 Index Calculation

### 2.3.1 Normalized Difference Vegetation Index (NDVI)
NDVI was calculated as (NIR - Red) / (NIR + Red). Values ranges from 
-1 to 1, with higher values indicating denser vegetation. For OTU 
assessment, NDVI values was normalized to 0–1 scale.

### 2.3.2 Soil Stability Index (SI)
SI was computed using the formula: SI = (sand_content × 0.3 + 
silt_content × 0.4 + clay_content × 0.3) / organic_carbon. Higher 
SI values indicates more stable soils.

### 2.3.3 Biodiversity Index (BI)
BI was estimated based on land cover classification from Sentinel-2 
and habitat heterogeneity metrics. The index incorporates species 
richness proxies derived from vegetation patterns.

### 2.3.4 Relief Complexity Index (RCI)
RCI was calculated as the standard deviation of slope within a 
1 km² moving window. Higher RCI values indicates more complex 
terrain, which is less suitable for controlled re-entries.

### 2.3.5 Fire Hazard Index (FHI)
FHI was derived from NDVI, land surface temperature (LST), and 
historical fire occurrence data. Areas with low vegetation moisture 
and high temperatures was assigned higher FHI values.

## 2.4 OTU Computation

The Optimal Touchdown Unit score was calculated using weighted 
linear combination:

OTU = w₁ × NDVI_norm + w₂ × SI_norm + w₃ × BI_norm + w₄ × (1 - RCI_norm) + w₅ × (1 - FHI_norm)

where w₁–w₅ represents weighting coefficients determined through 
analytical hierarchy process (AHP) with expert input. The weights 
used in this study was: w₁ = 0.25, w₂ = 0.20, w₃ = 0.15, w₄ = 0.25, 
w₅ = 0.15.

OTU scores was classified into five stability classes: Very High 
(0.8–1.0), High (0.6–0.8), Moderate (0.4–0.6), Low (0.2–0.4), and 
Very Low (0.0–0.2).

## 2.5 Validation Approach

Validation was performed using three methods: (1) comparison with 
historical impact sites, (2) field surveys at 15 representative 
locations, and (3) expert evaluation by five independent reviewers. 
Statistical metrics including correlation coefficient (r), root mean 
square error (RMSE), and Cohen's kappa (κ) was calculated to assess 
agreement.