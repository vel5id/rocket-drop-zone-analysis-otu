from api.models import SimulationRequest, ZonePreviewResponse, GeoJSONFeature
from config.zones import YU24_ZONES
from grid.polygon_grid import create_ellipse_polygon

def get_zone_preview(request: SimulationRequest) -> ZonePreviewResponse:
    """
    Generate zone preview polygons.
    """
    zone_id = request.zone_id
    
    if not zone_id:
        return ZonePreviewResponse(
            message="No zone_id provided. Preview available only for presets."
        )
        
    # Check YU-24 presets
    if zone_id in YU24_ZONES:
        try:
            zone_def = YU24_ZONES[zone_id]
            
            # Convert ZoneDefinition instance to dictionary for processing
            ellipse_params = {
                "center_lat": zone_def.center_lat,
                "center_lon": zone_def.center_lon,
                "semi_major_km": zone_def.semi_major_km,
                "semi_minor_km": zone_def.semi_minor_km,
                "angle_deg": zone_def.angle_deg
            }
            
            # --- Primary Ellipse ---
            primary_poly = create_ellipse_polygon(ellipse_params, scale=1.0)
            
            # Convert to [[lon, lat], ...] for GeoJSON
            primary_coords = [[lon, lat] for lat, lon in primary_poly]
            # Close loop
            if primary_coords[0] != primary_coords[-1]:
                primary_coords.append(primary_coords[0])
                
            primary_feature = GeoJSONFeature(
                properties={"type": "primary", "zone": zone_def.name},
                geometry={"type": "Polygon", "coordinates": [primary_coords]}
            )
            
            # In the current config/zones.py, YU24_ZONES entries are individual zones.
            # So we return just the primary polygon corresponding to the selected ID.
            
            return ZonePreviewResponse(
                zone_id=zone_id,
                primary_polygon=primary_feature,
                fragment_polygon=None,
                message=f"Preview generated for {zone_def.name}"
            )
            
        except Exception as e:
            return ZonePreviewResponse(message=f"Error generating preview: {str(e)}")
            
    return ZonePreviewResponse(message=f"Preview logic not implemented for zone type: {zone_id}")
