import 'package:flutter/material.dart';
import '../services/offline_storage_service.dart';

class OfflineQueueScreen extends StatefulWidget {
  const OfflineQueueScreen({super.key});

  @override
  State<OfflineQueueScreen> createState() => _OfflineQueueScreenState();
}

class _OfflineQueueScreenState extends State<OfflineQueueScreen> {
  List<OfflineDocket> _dockets = [];
  bool _isLoading = true;
  bool _isSyncing = false;

  @override
  void initState() {
    super.initState();
    _loadDockets();
  }

  Future<void> _loadDockets() async {
    setState(() {
      _isLoading = true;
    });
    final list = await OfflineStorageService.getQueuedDockets();
    setState(() {
      _dockets = list;
      _isLoading = false;
    });
  }

  Future<void> _syncAll() async {
    setState(() {
      _isSyncing = true;
    });

    // Simulate bulk network upload
    await Future.delayed(const Duration(seconds: 2));

    await OfflineStorageService.clearSyncedDockets();
    await _loadDockets();

    setState(() {
      _isSyncing = false;
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("All offline dockets synchronized with Central Legal Metrology Registry."),
          backgroundColor: Color(0xFF10B981),
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
        title: const Text("Offline Docket Queue", style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF10B981)))
          : _dockets.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.cloud_done_outlined, size: 64, color: Colors.green[400]),
                      const SizedBox(height: 14),
                      const Text(
                        "All Dockets Synchronized",
                        style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        "No pending offline inspections on this device.",
                        style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _dockets.length,
                  itemBuilder: (context, index) {
                    final docket = _dockets[index];
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0284C7).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.receipt_long, color: Color(0xFF38BDF8), size: 24),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  docket.retailerName,
                                  style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  "${docket.district}, ${docket.state} • ₹${docket.shelfPrice}",
                                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withOpacity(0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              "QUEUED",
                              style: TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
      bottomNavigationBar: _dockets.isNotEmpty
          ? Container(
              padding: const EdgeInsets.all(16),
              color: const Color(0xFF1E293B),
              child: ElevatedButton.icon(
                onPressed: _isSyncing ? null : _syncAll,
                icon: _isSyncing
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.cloud_upload),
                label: Text(_isSyncing ? "SYNCING TO HEADQUARTERS..." : "SYNC ALL DOCKETS NOW"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  foregroundColor: const Color(0xFF0F172A),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            )
          : null,
    );
  }
}
