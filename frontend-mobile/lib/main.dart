import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:lucide_icons/lucide_icons.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'map_widget.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(const CrisisSyncMobile());
}

class CrisisSyncMobile extends StatelessWidget {
  const CrisisSyncMobile({super.key});
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CrisisSync AI Mobile',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF111827), // gray-900
        primaryColor: const Color(0xFFEF4444), // red-500
      ),
      home: const CivilianHome(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class CivilianHome extends StatefulWidget {
  const CivilianHome({super.key});

  @override
  State<CivilianHome> createState() => _CivilianHomeState();
}

class _CivilianHomeState extends State<CivilianHome> {
  // Uses dynamic environment IP loaded globally via DotEnv injected config
  final String apiBase = dotenv.env['API_BASE_URL'] ?? 'http://127.0.0.1:8000/api'; 
  
  Map<String, dynamic>? _currentIncident;
  Map<String, dynamic>? _aiExplanation;
  List<dynamic> _reports = [];
  bool _sosSending = false;
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _fetchGlobalData();
    _pollingTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      _fetchGlobalData();
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchGlobalData() async {
    try {
      final incidentRes = await http.get(Uri.parse('\$apiBase/incidents'));
      if (incidentRes.statusCode == 200) {
        final incidents = jsonDecode(incidentRes.body) as List;
        if (incidents.isNotEmpty) {
          final topIncident = incidents.first;
          if (_currentIncident == null || topIncident['id'] != _currentIncident!['id']) {
            setState(() => _currentIncident = topIncident);
            _fetchAiAdvisory(topIncident['id']);
          }
        }
      }

      final reportsRes = await http.get(Uri.parse('\$apiBase/reports'));
      if (reportsRes.statusCode == 200) {
        setState(() {
          _reports = jsonDecode(reportsRes.body);
        });
      }
    } catch (e) {
      debugPrint("Data Fetch Error: \$e");
    }
  }

  Future<void> _fetchAiAdvisory(int incidentId) async {
    try {
      final res = await http.get(Uri.parse('\$apiBase/incidents/\$incidentId/explain'));
      if (res.statusCode == 200) {
        setState(() {
          _aiExplanation = jsonDecode(res.body);
        });
      }
    } catch (e) {
      debugPrint("AI Fetch Error: \$e");
    }
  }

  Future<void> _sendSos() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location services are disabled.')));
      return;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }
    
    setState(() => _sosSending = true);
    
    try {
      Position position = await Geolocator.getCurrentPosition();
      
      final res = await http.post(
        Uri.parse('\$apiBase/reports'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': 'civilian-mobile-\${DateTime.now().millisecondsSinceEpoch}',
          'description': 'Mobile SOS GPS Beacon Triggered',
          'location_lat': position.latitude,
          'location_lng': position.longitude,
          'type': 'gps_ping',
          'urgency': 'critical'
        }),
      );

      if (res.statusCode == 200) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
           const SnackBar(
             content: Text('SOS Signal Broadcast Received by Operations Center!'),
             backgroundColor: Colors.red,
           )
        );
      }
    } catch (e) {
      debugPrint("SOS Error: \$e");
    } finally {
      if (mounted) setState(() => _sosSending = false);
    }
  }

  Widget _buildTopBanner() {
    if (_currentIncident == null) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        color: const Color(0xFF1F2937),
        child: const SafeArea(
          bottom: false,
          child: Row(
            children: [
              Icon(LucideIcons.shieldCheck, color: Colors.green),
              SizedBox(width: 10),
              Text('System Online. No active threats nearby.', 
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)
              ),
            ],
          ),
        ),
      );
    }

    final String severity = _currentIncident!['severity'].toString().toLowerCase();
    Color bannerColor = const Color(0xFF1F2937);
    Color textColor = Colors.white;
    IconData icon = LucideIcons.alertTriangle;

    if (severity == 'critical') {
      bannerColor = Colors.red.shade900;
      icon = LucideIcons.siren;
    } else if (severity == 'high') {
      bannerColor = Colors.orange.shade800;
      icon = LucideIcons.alertCircle;
    }

    final explanationText = _aiExplanation != null 
        ? _aiExplanation!['explanation_simple'] 
        : "Analyzing local threat telemetry...";

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20).copyWith(top: 40),
      color: bannerColor,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.white, size: 28),
              const SizedBox(width: 10),
              Text(
                "\${_currentIncident!['disaster_type']} WARNING",
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            explanationText,
            style: const TextStyle(color: Colors.white70, fontSize: 14),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildTopBanner(),
          Expanded(
            child: Stack(
              children: [
                SizedBox(
                  width: double.infinity,
                  height: double.infinity,
                  child: CivilianMap(
                    currentIncident: _currentIncident,
                    severity: _currentIncident != null ? _currentIncident!['severity'] : 'low',
                  ),
                ),
                // Dark Gradient overlay at bottom
                Positioned(
                  bottom: 0, left: 0, right: 0,
                  height: 150,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [
                          Colors.black.withValues(alpha: 0.8),
                          Colors.transparent,
                        ],
                      )
                    ),
                  ),
                ),
                // SOS Button
                Positioned(
                  bottom: 40,
                  left: 20,
                  right: 20,
                  child: ElevatedButton(
                    onPressed: _sosSending ? null : _sendSos,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red.shade600,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 20),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      elevation: 10,
                    ),
                    child: _sosSending 
                      ? const SpinKitPulse(color: Colors.white, size: 30) // Loading spinner
                      : const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(LucideIcons.radio, size: 28),
                            SizedBox(width: 12),
                            Text("REPORT EMERGENCY", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                          ],
                        ),
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
