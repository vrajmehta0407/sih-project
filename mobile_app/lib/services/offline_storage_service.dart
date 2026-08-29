import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class OfflineDocket {
  final String id;
  final String retailerName;
  final String state;
  final String district;
  final double shelfPrice;
  final String imagePath;
  final String createdAt;
  final bool isSynced;

  OfflineDocket({
    required this.id,
    required this.retailerName,
    required this.state,
    required this.district,
    required this.shelfPrice,
    required this.imagePath,
    required this.createdAt,
    this.isSynced = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'retailer_name': retailerName,
      'state': state,
      'district': district,
      'shelf_price': shelfPrice,
      'image_path': imagePath,
      'created_at': createdAt,
      'is_synced': isSynced,
    };
  }

  factory OfflineDocket.fromMap(Map<String, dynamic> map) {
    return OfflineDocket(
      id: map['id'],
      retailerName: map['retailer_name'],
      state: map['state'],
      district: map['district'],
      shelfPrice: (map['shelf_price'] as num).toDouble(),
      imagePath: map['image_path'],
      createdAt: map['created_at'],
      isSynced: map['is_synced'] ?? false,
    );
  }
}

class OfflineStorageService {
  static const String _key = 'offline_inspection_dockets';

  static Future<List<OfflineDocket>> getQueuedDockets() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    return raw.map((item) => OfflineDocket.fromMap(jsonDecode(item))).toList();
  }

  static Future<void> saveDocket(OfflineDocket docket) async {
    final prefs = await SharedPreferences.getInstance();
    final dockets = await getQueuedDockets();
    dockets.add(docket);
    final raw = dockets.map((d) => jsonEncode(d.toMap())).toList();
    await prefs.setStringList(_key, raw);
  }

  static Future<void> clearSyncedDockets() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
