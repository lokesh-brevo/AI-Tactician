"""Mock API layer — reads from JSON files, returns data matching future Brevo API shapes."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from models import (
    AccountContext,
    AutomationDraftRequest,
    AutomationDraftResponse,
    AutomationsList,
    CampaignDraftRequest,
    CampaignDraftResponse,
    CampaignHistory,
    PerformanceReport,
    SegmentRequest,
    SegmentResponse,
)

DATA_DIR = Path(__file__).parent / "mock_data"


def _load(filename: str) -> dict:
    with open(DATA_DIR / filename) as f:
        return json.load(f)


# ── GET /api/account/context ────────────────────────────────────────────────

def get_account_context() -> dict:
    """Return full account snapshot."""
    data = _load("account_context.json")
    return data


# ── GET /api/campaigns/history ──────────────────────────────────────────────

def get_campaign_history(limit: int = 10) -> dict:
    """Return recent campaign performance data."""
    data = _load("campaign_history.json")
    data["campaigns"] = data["campaigns"][:limit]
    return data


# ── GET /api/automations/active ─────────────────────────────────────────────

def get_active_automations() -> dict:
    """Return currently active automation workflows."""
    return _load("automations.json")


# ── POST /api/contacts/segment ──────────────────────────────────────────────

def segment_contacts(base_filter: dict, segmentation_axis: str, **kwargs) -> dict:
    """Return pre-computed segmentation response.

    Uses the base_filter type to pick the right pre-computed data set.
    For the prototype we have two variants:
      - "all_customers" / "all_subscribers" / "list_members" → all_customers
      - "no_purchase" → no_purchase_90d
    """
    data = _load("segmentation.json")

    filter_type = base_filter.get("type", "all_subscribers")
    if filter_type == "no_purchase":
        return data["no_purchase_90d"]
    else:
        return data["all_customers"]


# ── POST /api/campaigns/draft ───────────────────────────────────────────────

def create_campaign_draft(
    name: str,
    channel: str,
    cohort: str,
    audience_size: int,
    content: dict,
    schedule: dict,
    **kwargs,
) -> dict:
    """Create a mock campaign draft and return a draft ID + preview URL."""
    draft_id = f"draft_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    return {
        "draft_id": draft_id,
        "status": "draft",
        "preview_url": f"https://app.brevo.com/campaigns/{draft_id}/preview",
        "created_at": now,
    }


# ── POST /api/automations/draft ─────────────────────────────────────────────

def create_automation_draft(
    name: str,
    cohort: str,
    trigger: dict,
    steps: list,
    exit_conditions: list,
    **kwargs,
) -> dict:
    """Create a mock automation workflow draft."""
    wf_id = f"wf_draft_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    # Estimate contacts entering from segment data if available
    estimated = kwargs.get("estimated_contacts_entering")
    if estimated is None:
        audience_filter = trigger.get("audience_filter", {})
        estimated = audience_filter.get("size")

    return {
        "workflow_id": wf_id,
        "status": "draft",
        "preview_url": f"https://app.brevo.com/automations/{wf_id}/preview",
        "created_at": now,
        "estimated_contacts_entering": estimated,
    }


# ── GET /api/campaigns/performance ──────────────────────────────────────────

def get_campaign_performance(period: str = "last_30d") -> dict:
    """Return aggregate performance metrics."""
    return _load("performance.json")
