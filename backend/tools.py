"""Maps Claude tool-call names to mock_api functions."""
from __future__ import annotations

import json
from mock_api import (
    get_account_context,
    get_campaign_history,
    get_active_automations,
    segment_contacts,
    create_campaign_draft,
    create_automation_draft,
    get_campaign_performance,
)


TOOL_DEFINITIONS = [
    {
        "name": "get_account_context",
        "description": "Retrieves the full account context snapshot including account info, channel configurations, ecommerce data, and engagement summary.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_campaign_history",
        "description": "Retrieves recent campaign performance data including open rates, click rates, conversion rates, and revenue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent campaigns to return (default 10)",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_active_automations",
        "description": "Retrieves all currently active automation workflows to check for potential conflicts.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "segment_contacts",
        "description": "Segments contacts based on a base filter and value-based tiers. Returns cohort breakdown with stats.",
        "input_schema": {
            "type": "object",
            "properties": {
                "base_filter": {
                    "type": "object",
                    "description": "Filter to identify eligible contacts",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "no_purchase",
                                "all_subscribers",
                                "list_members",
                                "event_registrants",
                            ],
                            "description": "Type of base filter",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days for recency-based filters",
                        },
                        "list_id": {
                            "type": "string",
                            "description": "List ID for list-based filters",
                        },
                    },
                    "required": ["type"],
                },
                "segmentation_axis": {
                    "type": "string",
                    "enum": ["ltv", "engagement", "lead_score", "blended"],
                    "description": "Which axis to segment on based on account type",
                },
            },
            "required": ["base_filter", "segmentation_axis"],
        },
    },
    {
        "name": "create_campaign_draft",
        "description": "Creates a draft campaign for a specific cohort. Returns a draft ID and preview URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Campaign name"},
                "channel": {
                    "type": "string",
                    "enum": ["email", "sms", "whatsapp"],
                    "description": "Delivery channel",
                },
                "cohort": {
                    "type": "string",
                    "enum": ["high_value", "mid_value", "standard"],
                    "description": "Target cohort",
                },
                "audience_size": {"type": "integer"},
                "content": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Email subject line (null for SMS/WhatsApp)",
                        },
                        "body": {"type": "string", "description": "Message body"},
                        "cta": {"type": "string", "description": "Call-to-action text"},
                        "offer": {
                            "type": "string",
                            "description": "Offer or incentive description",
                        },
                    },
                    "required": ["body", "cta"],
                },
                "schedule": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "individual_optimal",
                                "segment_optimal",
                                "batch",
                            ],
                            "description": "Send timing strategy",
                        }
                    },
                    "required": ["type"],
                },
            },
            "required": [
                "name",
                "channel",
                "cohort",
                "audience_size",
                "content",
                "schedule",
            ],
        },
    },
    {
        "name": "create_automation_draft",
        "description": "Creates a draft automation workflow for a specific cohort. Use this for ongoing, trigger-based flows (e.g., win-back automation, post-purchase sequence). Returns a workflow ID and preview URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Workflow name"},
                "cohort": {
                    "type": "string",
                    "enum": ["high_value", "mid_value", "standard"],
                    "description": "Target cohort",
                },
                "trigger": {
                    "type": "object",
                    "description": "What starts the automation",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "no_purchase_days",
                                "cart_abandoned",
                                "order_completed",
                                "contact_created",
                                "date_based",
                            ],
                            "description": "Trigger event type",
                        },
                        "value": {
                            "type": "integer",
                            "description": "Trigger threshold (e.g., days)",
                        },
                    },
                    "required": ["type"],
                },
                "steps": {
                    "type": "array",
                    "description": "Ordered sequence of automation steps",
                    "items": {
                        "type": "object",
                        "properties": {
                            "order": {"type": "integer"},
                            "channel": {
                                "type": "string",
                                "enum": ["email", "sms", "whatsapp"],
                            },
                            "delay": {
                                "type": "string",
                                "description": "Delay before this step (e.g., '0d', '3d')",
                            },
                            "condition": {
                                "type": "string",
                                "description": "Optional condition (e.g., 'not_converted')",
                            },
                            "content": {
                                "type": "object",
                                "properties": {
                                    "subject": {"type": "string"},
                                    "body": {"type": "string"},
                                    "cta": {"type": "string"},
                                },
                                "required": ["body", "cta"],
                            },
                        },
                        "required": ["order", "channel", "delay", "content"],
                    },
                },
                "exit_conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Conditions that remove a contact from the flow",
                },
            },
            "required": ["name", "cohort", "trigger", "steps", "exit_conditions"],
        },
    },
    {
        "name": "get_campaign_performance",
        "description": "Retrieves aggregate campaign performance metrics for a period.",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["last_7d", "last_30d", "last_90d"],
                    "description": "Time period for metrics",
                }
            },
            "required": ["period"],
        },
    },
]


# ── Tool dispatch ────────────────────────────────────────────────────────────

_HANDLERS = {
    "get_account_context": lambda _input: get_account_context(),
    "get_campaign_history": lambda _input: get_campaign_history(
        limit=_input.get("limit", 10)
    ),
    "get_active_automations": lambda _input: get_active_automations(),
    "segment_contacts": lambda _input: segment_contacts(
        base_filter=_input["base_filter"],
        segmentation_axis=_input["segmentation_axis"],
    ),
    "create_campaign_draft": lambda _input: create_campaign_draft(**_input),
    "create_automation_draft": lambda _input: create_automation_draft(**_input),
    "get_campaign_performance": lambda _input: get_campaign_performance(
        period=_input.get("period", "last_30d")
    ),
}


def handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Dispatch a tool call to the correct mock API function."""
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: {tool_name}"}
    return handler(tool_input)
