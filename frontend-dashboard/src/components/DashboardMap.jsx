import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Circle, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-routing-machine';

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

const getDisasterColor = (typeStr) => {
    if (!typeStr) return '#ef4444';
    const type = typeStr.toLowerCase();
    if (type.includes('flood')) return '#3b82f6'; // blue-500
    if (type.includes('earthquake') || type.includes('seismic')) return '#a16207'; // yellow-700/brown
    if (type.includes('fire') || type.includes('wildfire')) return '#ef4444'; // red-500
    if (type.includes('storm')) return '#0ea5e9'; // sky-500
    return '#ef4444'; // fallback red
};

function RoutingControl({ targetLoc }) {
    const map = useMap();
    useEffect(() => {
        if (!targetLoc) return;

        // Mock fire station 3km inland from victim (minus longitude moves it West)
        const fireStation = L.latLng(targetLoc.lat + 0.02, targetLoc.lng - 0.04);
        const victim = L.latLng(targetLoc.lat, targetLoc.lng);

        const routingControl = L.Routing.control({
            waypoints: [
                fireStation,
                victim
            ],
            lineOptions: {
                styles: [{ color: '#3b82f6', weight: 6, opacity: 0.8 }] // Blue line for responders
            },
            show: false, // Don't show the text itinerary by default to save screen space
            addWaypoints: false,
            routeWhileDragging: false,
            fitSelectedRoutes: false,
            createMarker: function (i, wp, nWps) {
                if (i === 0) {
                    // Fire Station marker
                    return L.marker(wp.latLng, {
                        icon: L.icon({
                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                            iconSize: [25, 41],
                            iconAnchor: [12, 41],
                            popupAnchor: [1, -34],
                        })
                    }).bindPopup("<div class='font-bold text-blue-600'>Primary Rescue Station</div><div class='text-xs'>Units Deploying</div>");
                }
                return null; // Victim marker is already drawn by SOS
            }
        }).addTo(map);

        return () => {
            if (routingControl && map) {
                try { map.removeControl(routingControl); } catch (e) { }
            }
        };
    }, [map, targetLoc?.lat, targetLoc?.lng]); // re-run only if coordinates actually change

    return null;
}

function MapController({ center }) {
    const map = useMap();
    useEffect(() => {
        if (center) {
            map.flyTo(center, 11);
        }
    }, [center, map]);
    return null;
}

export default function DashboardMap({ incidents = [], reports = [] }) {
    const mapCenter = incidents.length > 0 ? [incidents[0].location_lat, incidents[0].location_lng] : DEFAULT_CENTER;

    // Find the latest target location for routing
    const targetLoc = reports.length > 0
        ? { lat: reports[0].location_lat, lng: reports[0].location_lng }
        : (incidents.length > 0 ? { lat: incidents[0].location_lat, lng: incidents[0].location_lng } : null);

    return (
        <div className="w-full h-full rounded-xl overflow-hidden shadow-lg border border-gray-800 relative z-0">
            <MapContainer
                center={mapCenter}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
            >
                <MapController center={mapCenter} />
                <RoutingControl targetLoc={targetLoc} />
                {/* Dark mode tiles suitable for Operations centers */}
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
                />

                {/* Render Incident Hazard Zones */}
                {incidents.map((incident) => {
                    const color = getDisasterColor(incident.disaster_type);
                    return (
                        <Circle
                            key={`inc-${incident.id}`}
                            center={[incident.location_lat, incident.location_lng]}
                            radius={4000} // 4km hazard radius for visual mapping
                            pathOptions={{ color: color, fillColor: color, fillOpacity: 0.2, weight: 2 }}
                        >
                            <Popup>
                                <div className="font-bold">{incident.disaster_type} • {incident.location_name}</div>
                                <div className={`font-semibold ${incident.severity === 'critical' ? 'text-red-500' : 'text-orange-500'}`}>
                                    Severity: {incident.severity.toUpperCase()}
                                </div>
                                <div className="text-xs text-gray-500 mt-1">Pop Affected: {incident.population_affected}</div>
                            </Popup>
                        </Circle>
                    );
                })}

                {/* Render SOS Emergency Reports */}
                {reports.map((report) => (
                    <Marker
                        key={`rep-${report.id}`}
                        position={[report.location_lat, report.location_lng]}
                        icon={sosIcon}
                    >
                        <Popup>
                            <div className="font-bold text-red-600">SOS Distress Signal</div>
                            <div className="text-xs text-gray-700 mt-1">{report.description || 'Emergency declared from civilian device.'}</div>
                            <div className="text-[10px] text-gray-400 mt-2">User: {report.user_id}</div>
                            <div className="text-[10px] text-gray-400">Time: {new Date(report.timestamp).toLocaleTimeString()}</div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}
