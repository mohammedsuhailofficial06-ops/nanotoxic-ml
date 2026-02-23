import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(NanoToxApp());

class NanoToxApp extends StatelessWidget {
  const NanoToxApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
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
  const Dashboard({super.key});

  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  String _result = "Enter parameters and scan";
  Color _resultColor = Colors.white70;
  
  double _size = 50;
  double _zeta = 0;
  double _dosage = 50;
  String _material = 'Gold';

  Future<void> _runAnalysis() async {
    setState(() => _result = "Running ML Inference...");
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/predict'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "core_material": _material,
          "size_nm": _size,
          "zeta_potential_mv": _zeta,
          "dosage_ug_ml": _dosage
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _result = "SYSTEM ASSESSMENT: ${data['prediction'].toString().toUpperCase()}";
          _resultColor = data['prediction'] == "Toxic" ? Colors.redAccent : Colors.greenAccent;
        });
      }
    } catch (e) {
      setState(() {
        _result = "ERROR: Backend Offline";
        _resultColor = Colors.orange;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("🔬 NANOTOXIC-ML | PREDICTIVE PORTAL"), centerTitle: true),
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
                      initialValue: _material,
                      decoration: InputDecoration(labelText: "Nanoparticle Core"),
                      items: ['Gold', 'Silver', 'ZincOxide', 'Silica', 'IronOxide'].map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                      onChanged: (val) => setState(() => _material = val!),
                    ),
                    SizedBox(height: 25),
                    _buildSlider("Size: ${_size.toInt()} nm", _size, 1, 200, (v) => setState(() => _size = v)),
                    _buildSlider("Zeta Potential: ${_zeta.toInt()} mV", _zeta, -100, 100, (v) => setState(() => _zeta = v)),
                    _buildSlider("Dosage: ${_dosage.toInt()} µg/mL", _dosage, 0, 500, (v) => setState(() => _dosage = v)),
                    SizedBox(height: 30),
                    ElevatedButton(
                      onPressed: _runAnalysis,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                        minimumSize: Size(double.infinity, 55),
                      ),
                      child: Text("GENERATE PREDICTION", style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    ),
                    SizedBox(height: 40),
                    Container(
                      padding: EdgeInsets.all(15),
                      decoration: BoxDecoration(border: Border.all(color: _resultColor), borderRadius: BorderRadius.circular(10)),
                      child: Text(_result, textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _resultColor)),
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