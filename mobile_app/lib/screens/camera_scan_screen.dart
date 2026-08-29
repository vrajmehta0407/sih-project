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

class _CameraScanScreenState extends State<CameraScanScreen> with SingleTickerProviderStateMixin {
  File? _capturedImage;
  bool _isProcessing = false;
  final ImagePicker _picker = ImagePicker();
  late AnimationController _bracketController;

  @override
  void initState() {
    super.initState();
    _bracketController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _bracketController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? photo = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 90,
      );

      if (photo != null) {
        setState(() {
          _capturedImage = File(photo.path);
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error capturing image: $e")),
      );
    }
  }

  Future<void> _processImage() async {
    if (_capturedImage == null) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      final result = await ApiService.submitInspection(
        imageFile: _capturedImage!,
        district: "Mumbai Suburban",
        state: "Maharashtra",
      );

      setState(() {
        _isProcessing = false;
      });

      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => InspectionResultScreen(
              inspectionData: result,
              imageFile: _capturedImage,
            ),
          ),
        );
      }
    } catch (e) {
      await OfflineStorageService.saveOfflineInspection(
        _capturedImage!.path,
        "Mumbai Suburban",
        "Maharashtra",
      );

      setState(() {
        _isProcessing = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: Color(0xFFF59E0B),
            content: Text("Backend offline: Inspection saved to local SQLite queue!"),
          ),
        );
        Navigator.pop(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          "Rule 6 Label Scanner",
          style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF0F172A).withOpacity(0.06),
                    blurRadius: 20,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    if (_capturedImage != null)
                      Image.file(_capturedImage!, fit: BoxFit.contain, width: double.infinity, height: double.infinity)
                    else
                      Container(
                        color: const Color(0xFFF1F5F9),
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: const Color(0xFF2563EB).withOpacity(0.15),
                                      blurRadius: 16,
                                    ),
                                  ],
                                ),
                                child: const Icon(Icons.document_scanner, size: 48, color: Color(0xFF2563EB)),
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                "Align Package Label Inside Guide",
                                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              const Text(
                                "Auto-deskew ±45° • Anti-glare inpainting",
                                style: TextStyle(color: Color(0xFF64748B), fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ),

                    // Animated Reticle / Corner Brackets
                    AnimatedBuilder(
                      animation: _bracketController,
                      builder: (context, child) {
                        return Container(
                          margin: const EdgeInsets.all(32),
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: const Color(0xFF2563EB).withOpacity(0.4 + (_bracketController.value * 0.4)),
                              width: 2.5,
                            ),
                            borderRadius: BorderRadius.circular(20),
                          ),
                        );
                      },
                    ),

                    if (_isProcessing)
                      Container(
                        color: Colors.white.withOpacity(0.92),
                        child: const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              SizedBox(
                                width: 44,
                                height: 44,
                                child: CircularProgressIndicator(strokeWidth: 3, color: Color(0xFF2563EB)),
                              ),
                              SizedBox(height: 20),
                              Text(
                                "Dual-OCR Consensus Active...",
                                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, fontWeight: FontWeight.bold),
                              ),
                              SizedBox(height: 4),
                              Text(
                                "Extracting Rule 6 Declarations & Recidivism",
                                style: TextStyle(color: Color(0xFF64748B), fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),

          // Action Controls
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(24),
                topRight: Radius.circular(24),
              ),
              boxShadow: [
                BoxShadow(
                  color: Color(0x0A000000),
                  blurRadius: 10,
                  offset: Offset(0, -4),
                ),
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  icon: const Icon(Icons.photo_library_outlined, color: Color(0xFF64748B), size: 28),
                  onPressed: () => _pickImage(ImageSource.gallery),
                ),
                GestureDetector(
                  onTap: () => _pickImage(ImageSource.camera),
                  child: Container(
                    width: 68,
                    height: 68,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
                      ),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF2563EB).withOpacity(0.4),
                          blurRadius: 16,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: const Icon(Icons.camera_alt, color: Colors.white, size: 30),
                  ),
                ),
                if (_capturedImage != null && !_isProcessing)
                  IconButton(
                    icon: const Icon(Icons.send_rounded, color: Color(0xFF10B981), size: 30),
                    onPressed: _processImage,
                  )
                else
                  const SizedBox(width: 48),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
