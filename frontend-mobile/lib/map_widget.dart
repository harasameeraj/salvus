import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';

class CivilianMap extends StatefulWidget {
  final Map<String, dynamic>? currentIncident;
  final String severity;

  const CivilianMap({super.key, this.currentIncident, required this.severity});

  @override
  State<CivilianMap> createState() => _CivilianMapState();
}

class _CivilianMapState extends State<CivilianMap> {
  final _mapController = MapController();
  LatLng _dynamicCenter = const LatLng(0, 0); // Temporary before GPS locks
  bool _hasInitialLocation = false;

  @override
  void initState() {
    super.initState();
    _determineCenter();
  }

  Future<void> _determineCenter() async {
    if (widget.currentIncident != null) {
      final lat = widget.currentIncident!['location_lat'] as double;
      final lng = widget.currentIncident!['location_lng'] as double;
      setState(() {
        _dynamicCenter = LatLng(lat, lng);
        _hasInitialLocation = true;
      });
      return;
    }

    // No incident? Get real GPS location instead of hardcoding a city
    try {
      Position position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium);
      if (mounted) {
        setState(() {
          _dynamicCenter = LatLng(position.latitude, position.longitude);
          _hasInitialLocation = true;
        });
        _mapController.move(_dynamicCenter, 13.0);
      }
    } catch (e) {
      // Fallback if permissions denied
      if (mounted) {
        setState(() {
          _dynamicCenter = const LatLng(13.0827, 80.2707); // Fallback to Chennai only if GPS fails
          _hasInitialLocation = true;
        });
      }
    }
  }

  Color _getSeverityColor(Map<String, dynamic>? incident, String severityLevel) {
    if (incident != null) {
      final type = incident['disaster_type'].toString().toLowerCase();
      if (type.contains('flood')) return Colors.blue.withValues(alpha: 0.5);
      if (type.contains('earthquake') || type.contains('seismic')) return Colors.brown.withValues(alpha: 0.5);
      if (type.contains('fire') || type.contains('wildfire')) return Colors.red.withValues(alpha: 0.5);
      if (type.contains('storm')) return Colors.lightBlue.withValues(alpha: 0.5);
    }
    // Fallback dictionary
    if (severityLevel == 'critical') return Colors.red.withValues(alpha: 0.5);
    if (severityLevel == 'high') return Colors.orange.withValues(alpha: 0.5);
    return Colors.yellow.withValues(alpha: 0.3);
  }

  @override
  void didUpdateWidget(covariant CivilianMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.currentIncident != null && widget.currentIncident != oldWidget.currentIncident) {
      final lat = widget.currentIncident!['location_lat'] as double;
      final lng = widget.currentIncident!['location_lng'] as double;
      _mapController.move(LatLng(lat, lng), 12.0);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_hasInitialLocation) {
      return const Center(child: CircularProgressIndicator());
    }

    final center = widget.currentIncident != null
        ? LatLng(widget.currentIncident!['location_lat'], widget.currentIncident!['location_lng'])
        : _dynamicCenter;

    final hazardColor = _getSeverityColor(widget.currentIncident, widget.severity);

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: center,
        initialZoom: 12.0,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.crisissync.mobile',
        ),
        if (widget.currentIncident != null)
          CircleLayer(
            circles: [
              CircleMarker(
                point: center,
                color: hazardColor,
                borderColor: hazardColor.withValues(alpha: 1.0),
                borderStrokeWidth: 2,
                useRadiusInMeter: true,
                radius: 4000, // 4km hazard zone
              ),
            ],
          ),
      ],
    );
  }
}
