import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../services/offline_storage_service.dart';
import 'inspection_result_screen.dart';

class CameraScanScreen extends StatefulWidget {
  const CameraScanScreen({super.key});

  @override
  State<CameraScanScreen> createState() => _CameraScanScreenState();
}

class _CameraScanScreenState extends State<CameraScanScreen> {
  File? _imageFile;
  final _retailerController = TextEditingController(text: "City Supermarket Store #12");
  final _stateController = TextEditingController(text: "Maharashtra");
  final _districtController = TextEditingController(text: "Mumbai");
  final _shelfPriceController = TextEditingController(text: "150.0");
  bool _isProcessing = false;

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: source);
    if (picked != null) {
      setState(() {
        _imageFile = File(picked.path);
      });
    }
  }

  Future<void> _analyzeInspection() async {
    if (_imageFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please snap or select a packaging label photo")),
      );
      return;
    }

    setState(() {
      _isProcessing = true;
    });

    final shelfPrice = double.tryParse(_shelfPriceController.text);
    final result = await ApiService.uploadInspection(
      imageFile: _imageFile!,
      retailerName: _retailerController.text.trim(),
      state: _stateController.text.trim(),
      district: _districtController.text.trim(),
      shelfPrice: shelfPrice,
    );

    setState(() {
      _isProcessing = false;
    });

    if (result != null && mounted) {
      // Also cache to offline storage
      await OfflineStorageService.saveDocket(OfflineDocket(
        id: result['id'] ?? 'insp-${DateTime.now().millisecondsSinceEpoch}',
        retailerName: _retailerController.text.trim(),
        state: _stateController.text.trim(),
        district: _districtController.text.trim(),
        shelfPrice: shelfPrice ?? 0.0,
        imagePath: _imageFile!.path,
        createdAt: DateTime.now().toIso8601String(),
        isSynced: true,
      ));

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => InspectionResultScreen(
            inspectionData: result,
            imageFile: _imageFile!,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Rule 6 Label Scanner", style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Viewport Box
            Container(
              height: 240,
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF334155), width: 2),
              ),
              child: _imageFile != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(14),
                      child: Image.file(_imageFile!, fit: BoxFit.cover, width: double.infinity),
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.crop_free, size: 56, color: Color(0xFF10B981)),
                        const SizedBox(height: 10),
                        const Text(
                          "Position Packaging Label Inside Frame",
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          "Ensure MRP, Net Qty & Mfg Details are visible",
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            ElevatedButton.icon(
                              onPressed: () => _pickImage(ImageSource.camera),
                              icon: const Icon(Icons.camera_alt, size: 16),
                              label: const Text("Camera"),
                              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981)),
                            ),
                            const SizedBox(width: 12),
                            OutlinedButton.icon(
                              onPressed: () => _pickImage(ImageSource.gallery),
                              icon: const Icon(Icons.photo_library, size: 16, color: Colors.white),
                              label: const Text("Gallery", style: TextStyle(color: Colors.white)),
                            ),
                          ],
                        ),
                      ],
                    ),
            ),
            const SizedBox(height: 20),

            // Metadata Form
            const Text(
              "Field Audit Parameters",
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 10),

            TextField(
              controller: _retailerController,
              style: const TextStyle(color: Colors.white),
              decoration: _inputDeco("Retailer / Establishment Name", Icons.storefront),
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _stateController,
                    style: const TextStyle(color: Colors.white),
                    decoration: _inputDeco("State", Icons.map_outlined),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _districtController,
                    style: const TextStyle(color: Colors.white),
                    decoration: _inputDeco("District", Icons.location_city),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            TextField(
              controller: _shelfPriceController,
              keyboardType: TextInputType.number,
              style: const TextStyle(color: Colors.white),
              decoration: _inputDeco("Actual Shelf Price Charged (₹)", Icons.currency_rupee),
            ),
            const SizedBox(height: 24),

            ElevatedButton.icon(
              onPressed: _isProcessing ? null : _analyzeInspection,
              icon: _isProcessing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.analytics_outlined),
              label: Text(
                _isProcessing ? "RUNNING DUAL OCR & RULE 6 AUDIT..." : "ANALYZE COMPLIANCE NOW",
                style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: const Color(0xFF0F172A),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  InputDecoration _inputDeco(String label, IconData icon) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
      prefixIcon: Icon(icon, color: const Color(0xFF10B981), size: 20),
      filled: true,
      fillColor: const Color(0xFF1E293B),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: BorderSide.none,
      ),
    );
  }
}
