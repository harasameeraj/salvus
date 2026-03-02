import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix typical Leaflet invisible icon issues in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Create a custom red icon for SOS reports
const sosIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// Chennai default for testing
const DEFAULT_CENTER = [13.0827, 80.2707];

function MapController({ center }) {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.flyTo(center, 12);
        }
    }, [center, map]);
    return null;
}

export default function CivilianMap({ severity = 'low', incident = null }) {
    const [userLoc, setUserLoc] = useState(null);

    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                setUserLoc([position.coords.latitude, position.coords.longitude]);
            });
        }
    }, []);

    const getSeverityColor = () => {
        const typeStr = incident?.disaster_type?.toLowerCase() || '';

        // Use type-specific color if provided
        if (typeStr.includes('flood')) return '#3b82f6'; // blue-500
        if (typeStr.includes('earthquake') || typeStr.includes('seismic')) return '#a16207'; // yellow-700/brown
        if (typeStr.includes('fire') || typeStr.includes('wildfire')) return '#ef4444'; // red-500
        if (typeStr.includes('storm')) return '#0ea5e9'; // sky-500

        // Fallback to severity colors
        switch (severity) {
            case 'critical': return '#ef4444'; // red-500
            case 'high': return '#f97316'; // orange-500
            case 'moderate': return '#eab308'; // yellow-500
            default: return '#22c55e'; // green-500
        }
    };

    const mapCenter = incident ? [incident.location_lat, incident.location_lng] : DEFAULT_CENTER;

    return (
        <div className="w-full h-full relative z-0">
            <MapContainer
                center={mapCenter}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
            >
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; OSM contributors | CARTO'
                />
                <MapController center={mapCenter} />

                {/* Render User's SOS Location if active */}
                {userLoc && (
                    <Marker position={userLoc} icon={sosIcon}>
                        <Popup>Your Location</Popup>
                    </Marker>
                )}

                {/* Render the actual affected disaster zone */}
                {incident && (
                    <Circle
                        center={[incident.location_lat, incident.location_lng]}
                        radius={4000} // Dynamic 4km hazard circle
                        pathOptions={{
                            color: getSeverityColor(),
                            fillColor: getSeverityColor(),
                            fillOpacity: 0.3,
                            weight: 2
                        }}
                    >
                        <Popup>
                            <strong>{incident.disaster_type} Hazard Zone</strong>
                            <br />Evacuate immediately.
                        </Popup>
                    </Circle>
                )}
            </MapContainer>
        </div>
    );
}
