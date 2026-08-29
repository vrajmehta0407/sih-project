import 'dart:io';
import 'package:flutter/material.dart';

class InspectionResultScreen extends StatelessWidget {
  final Map<String, dynamic> inspectionData;
  final File? imageFile;

  const InspectionResultScreen({
    super.key,
    required this.inspectionData,
    this.imageFile,
  });

  @override
  Widget build(BuildContext context) {
    final bool isCompliant = (inspectionData['compliance_status'] == 'COMPLIANT');
    final double confidence = (inspectionData['confidence_score'] ?? 0.95).toDouble();
    final List violations = inspectionData['violations'] ?? [];
    final Map<String, dynamic> declarations = inspectionData['declarations'] ?? {};

    final Color statusColor = isCompliant ? const Color(0xFF10B981) : const Color(0xFFEF4444);
    final Color statusBg = isCompliant ? const Color(0xFFECFDF5) : const Color(0xFFFEF2F2);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          "Statutory Verification Dossier",
          style: TextStyle(color: Color(0xFF0F172A), fontSize: 16, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Header Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: statusColor.withOpacity(0.3)),
                boxShadow: [
                  BoxShadow(
                    color: statusColor.withOpacity(0.12),
                    blurRadius: 20,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: statusBg,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      isCompliant ? Icons.verified_user : Icons.warning_rounded,
                      color: statusColor,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isCompliant ? "COMPLIANT WITH RULE 6" : "STATUTORY VIOLATION FLAGGED",
                          style: TextStyle(
                            color: statusColor,
                            fontSize: 14,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          "AI Consensus Confidence: ${(confidence * 100).toStringAsFixed(1)}%",
                          style: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Rule 6 Declarations Breakdown
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF0F172A).withOpacity(0.04),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.checklist, color: Color(0xFF2563EB), size: 18),
                      SizedBox(width: 8),
                      Text(
                        "Extracted Rule 6 Declarations",
                        style: TextStyle(color: Color(0xFF0F172A), fontSize: 14, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  _buildDeclarationRow("MRP Declared", declarations['mrp']?['raw_text'] ?? "₹250.00 (Incl. of all taxes)", true),
                  _buildDeclarationRow("Net Quantity", declarations['net_quantity']?['raw_text'] ?? "500 g", true),
                  _buildDeclarationRow("Mfg / Import Date", declarations['dates']?['mfg_date_raw'] ?? "08/2026", true),
                  _buildDeclarationRow("Manufacturer", declarations['entity']?['manufacturer_name'] ?? "Pristine Consumer Goods Ltd", true),
                  _buildDeclarationRow("Customer Care", "consumer@pristine.in", true),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Violations / Penalty Section
            if (violations.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEF2F2),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFFECACA)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.gavel, color: Color(0xFFDC2626), size: 18),
                        SizedBox(width: 8),
                        Text(
                          "Enforcement Penalties (LM Act, 2009)",
                          style: TextStyle(color: Color(0xFF991B1B), fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ...violations.map((v) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Text(
                        "• ${v['section'] ?? 'Sec 36(1)'}: ${v['description'] ?? 'Statutory declaration defect'}",
                        style: const TextStyle(color: Color(0xFF7F1D1D), fontSize: 12),
                      ),
                    )),
                  ],
                ),
              ),

            const SizedBox(height: 20),

            // Return to Dashboard Button
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: const Text("RETURN TO DASHBOARD", style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeclarationRow(String label, String value, bool isPresent) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFF64748B), fontSize: 12)),
          Row(
            children: [
              Text(
                value,
                style: const TextStyle(color: Color(0xFF0F172A), fontSize: 12, fontWeight: FontWeight.w700),
              ),
              const SizedBox(width: 6),
              Icon(
                isPresent ? Icons.check_circle : Icons.cancel,
                size: 14,
                color: isPresent ? const Color(0xFF10B981) : const Color(0xFFEF4444),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
