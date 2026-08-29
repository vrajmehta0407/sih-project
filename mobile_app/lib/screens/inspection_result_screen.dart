import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_dashboard_screen.dart';

class InspectionResultScreen extends StatefulWidget {
  final Map<String, dynamic> inspectionData;
  final File imageFile;

  const InspectionResultScreen({
    super.key,
    required this.inspectionData,
    required this.imageFile,
  });

  @override
  State<InspectionResultScreen> createState() => _InspectionResultScreenState();
}

class _InspectionResultScreenState extends State<InspectionResultScreen> {
  final _voiceNoteController = TextEditingController();
  bool _isSavingVoice = false;
  String? _voiceSuccessMessage;

  Future<void> _submitVoiceNote() async {
    final transcript = _voiceNoteController.text.trim();
    if (transcript.isEmpty) return;

    setState(() {
      _isSavingVoice = true;
    });

    final id = widget.inspectionData['id'] ?? '';
    final res = await ApiService.submitVoiceNote(id, transcript);

    setState(() {
      _isSavingVoice = false;
      if (res != null) {
        _voiceSuccessMessage = "Voice memo parsed & attached to official docket.";
        _voiceNoteController.clear();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final status = widget.inspectionData['compliance_status'] ?? 'NON_COMPLIANT';
    final isCompliant = status == 'COMPLIANT';
    final detectedMrp = widget.inspectionData['detected_mrp'] ?? 150.0;
    final shelfPrice = widget.inspectionData['shelf_price'] ?? 180.0;
    final isOvercharging = (shelfPrice as num) > (detectedMrp as num);

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Inspection Result", style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Hero Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isCompliant ? const Color(0xFF065F46) : const Color(0xFF881337),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isCompliant ? const Color(0xFF10B981) : const Color(0xFFF43F5E),
                  width: 1.5,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    isCompliant ? Icons.check_circle_outline : Icons.warning_amber_rounded,
                    color: Colors.white,
                    size: 40,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isCompliant ? "COMPLIANT WITH RULE 6" : "NON-COMPLIANT INFRACTION",
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          isCompliant
                              ? "All mandatory statutory declarations verified."
                              : "Statutory deficiencies detected under Legal Metrology Rules, 2011.",
                          style: const TextStyle(color: Colors.white70, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Overcharging Box
            if (isOvercharging)
              Container(
                padding: const EdgeInsets.all(14),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.amber.withOpacity(0.4)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.price_change_outlined, color: Colors.amberAccent, size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        "Section 18 Overcharging Detected!\nPrinted MRP: ₹$detectedMrp • Charged: ₹$shelfPrice (Delta +₹${(shelfPrice - detectedMrp).toStringAsFixed(1)})",
                        style: const TextStyle(color: Colors.amberAccent, fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),

            // Captured Evidence Preview
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Seized Evidence Image",
                    style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.file(widget.imageFile, height: 160, width: double.infinity, fit: BoxFit.cover),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Voice Dictation Assistant
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.mic, color: Color(0xFF10B981), size: 18),
                      SizedBox(width: 8),
                      Text(
                        "Field Voice Memo (English / Hindi)",
                        style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _voiceNoteController,
                    maxLines: 2,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    decoration: InputDecoration(
                      hintText: "e.g. 'दुकानदार ने एमआरपी से ज्यादा रुपया लिया...'",
                      hintStyle: const TextStyle(color: Color(0xFF64748B)),
                      filled: true,
                      fillColor: const Color(0xFF0F172A),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (_voiceSuccessMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Text(
                        _voiceSuccessMessage!,
                        style: const TextStyle(color: Color(0xFF10B981), fontSize: 11),
                      ),
                    ),
                  Align(
                    alignment: Alignment.centerRight,
                    child: ElevatedButton(
                      onPressed: _isSavingVoice ? null : _submitVoiceNote,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      ),
                      child: const Text("Save Voice Note", style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Finish button
            ElevatedButton(
              onPressed: () {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const HomeDashboardScreen()),
                  (route) => false,
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF334155),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: const Text("RETURN TO DASHBOARD", style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}
