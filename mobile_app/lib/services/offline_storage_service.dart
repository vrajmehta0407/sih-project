import 'dart:convert';
import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class OfflineStorageService {
  static const String _key = 'offline_inspection_queue';

  static Future<List<Map<String, dynamic>>> getPendingInspections() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    return raw.map((item) => jsonDecode(item) as Map<String, dynamic>).toList();
  }

  static Future<void> saveOfflineInspection(String imagePath, String district, String state) async {
    final prefs = await SharedPreferences.getInstance();
    final list = await getPendingInspections();
    list.add({
      'id': 'offline-${DateTime.now().millisecondsSinceEpoch}',
      'image_path': imagePath,
      'district': district,
      'state': state,
      'created_at': DateTime.now().toIso8601String(),
    });
    final raw = list.map((item) => jsonEncode(item)).toList();
    await prefs.setStringList(_key, raw);
  }

  static Future<int> syncAllPending() async {
    final items = await getPendingInspections();
    int count = 0;
    for (final item in items) {
      try {
        final file = File(item['image_path']);
        if (await file.exists()) {
          await ApiService.submitInspection(
            imageFile: file,
            district: item['district'] ?? 'Mumbai Suburban',
            state: item['state'] ?? 'Maharashtra',
          );
          count++;
        }
      } catch (_) {}
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
    return count;
  }
}
