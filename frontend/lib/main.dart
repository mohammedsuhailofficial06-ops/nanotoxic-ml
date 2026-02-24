import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(NanoToxApp());

class NanoToxApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NanoToxic-ML',
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.tealAccent,
        useMaterial3: true,
      ),
      home: Dashboard(),
    );
  }
}

class Dashboard extends StatefulWidget {
  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  String _result = "Adjust parameters and scan";
  String _confidence = "";
  Color _resultColor = Colors.white70;
  bool _isLoading = false;
  
  double _size = 50;
  double _zeta = 0;
  double _dosage = 50;
  // Standardized naming to match backend Random Forest logic
  String _material = 'Gold';

  Future<void> _runAnalysis() async {
    setState(() {
      _isLoading = true;
      _result = "Running ML Inference...";
      _confidence = "";
    });
    
    try {
      final response = await http.post(
        Uri.parse('https://nanotoxic-api.onrender.com/predict'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "core_material": _material,
          "size_nm": _size,
          "zeta_potential_mv": _zeta,
          "dosage_ug_ml": _dosage
        }),
      ).timeout(const Duration(seconds: 15)); // Prevents infinite hanging

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _result = "SYSTEM ASSESSMENT: ${data['prediction'].toString().toUpperCase()}";
          _confidence = "Confidence Score: ${data['confidence']}";
          _resultColor = data['prediction'] == "Toxic" ? Colors.redAccent : Colors.greenAccent;
        });
      } else {
        setState(() {
          _result = "SERVER ERROR: ${response.statusCode}";
          _confidence = "API is awake but rejected the request.";
          _resultColor = Colors.orange;
        });
      }
    } catch (e) {
      setState(() {
        _result = "ERROR: Connection Timeout";
        _confidence = "Check if Render API is sleeping or URL is wrong.";
        _resultColor = Colors.orange;
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("🔬 NANOTOXIC-ML | RESEARCH PORTAL"), centerTitle: true),
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            width: 500,
            padding: EdgeInsets.all(24),
            child: Card(
              elevation: 12,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
              child: Padding(
                padding: EdgeInsets.all(30),
                child: Column(
                  children: [
                    DropdownButtonFormField<String>(
                      value: _material,
                      decoration: InputDecoration(labelText: "Nanoparticle Core"),
                      items: ['Gold', 'Silver', 'ZincOxide', 'Silica', 'IronOxide']
                          .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                          .toList(),
                      onChanged: (val) => setState(() => _material = val!),
                    ),
                    SizedBox(height: 25),
                    _buildSlider("Size: ${_size.toInt()} nm", _size, 1, 200, (v) => setState(() => _size = v)),
                    _buildSlider("Zeta Potential: ${_zeta.toInt()} mV", _zeta, -100, 100, (v) => setState(() => _zeta = v)),
                    _buildSlider("Dosage: ${_dosage.toInt()} µg/mL", _dosage, 0, 500, (v) => setState(() => _dosage = v)),
                    SizedBox(height: 30),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _runAnalysis,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                        minimumSize: Size(double.infinity, 55),
                      ),
                      child: _isLoading 
                        ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) 
                        : Text("GENERATE PREDICTION", style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    ),
                    SizedBox(height: 40),
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.all(15),
                      decoration: BoxDecoration(
                        border: Border.all(color: _resultColor), 
                        borderRadius: BorderRadius.circular(10)
                      ),
                      child: Column(
                        children: [
                          Text(_result, textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _resultColor)),
                          if (_confidence.isNotEmpty) Text(_confidence, style: TextStyle(fontSize: 14, color: Colors.white60)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSlider(String label, double val, double min, double max, Function(double) onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(color: Colors.tealAccent)),
        Slider(value: val, min: min, max: max, onChanged: onChanged),
      ],
    );
  }
}