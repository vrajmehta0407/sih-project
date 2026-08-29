"""Add preprocessing_metadata JSON column to inspections

Revision ID: 002_add_preprocessing_metadata
Revises: 001_initial
Create Date: 2026-08-25 22:00:00.000000

Adds the `preprocessing_metadata` JSON column to the `inspections` table.
This column stores per-image-side OpenCV pipeline results (skew angle,
quality score, processing time, glare count, perspective correction flag)
without requiring a separate table or schema churn.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# ── Revision identifiers ──────────────────────────────────────────────────
revision: str = "002_add_preprocessing_metadata"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add preprocessing_metadata column to inspections table."""
    op.add_column(
        "inspections",
        sa.Column(
            "preprocessing_metadata",
            sa.JSON(),
            nullable=True,
            comment=(
                "Per-image-side preprocessing pipeline results. "
                "Keyed by side name (front/back/left/right/top). "
                "Each value contains: skew_angle_degrees, perspective_corrected, "
                "glare_regions_detected, contrast_enhanced, quality_score, "
                "processing_time_ms, original_size, processed_size, pipeline_steps."
            ),
        ),
    )

    # Also fix the inspections.status default — Stage 1 defaulted to 'completed';
    # Stage 2 logic uses 'draft' → 'preprocessed' progression.
    # We update the server default for new rows only (existing rows unaffected).
    op.alter_column(
        "inspections",
        "status",
        existing_type=sa.String(length=50),
        server_default="draft",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Remove preprocessing_metadata column."""
    op.drop_column("inspections", "preprocessing_metadata")
    # Restore original default
    op.alter_column(
        "inspections",
        "status",
        existing_type=sa.String(length=50),
        server_default="completed",
        existing_nullable=False,
    )
