import React from 'react';
import LeafletMap from './LeafletMap';
import SvgMap from './SvgMap';
import { MapViewProps } from '../../types';

// In a real scenario, this might check for window.L or specific capabilities
const IS_LEAFLET_AVAILABLE = true;

const MapView: React.FC<MapViewProps> = (props) => {
    if (IS_LEAFLET_AVAILABLE) {
        return <LeafletMap {...props} />;
    }
    return <SvgMap {...props} />;
};

export default MapView;
