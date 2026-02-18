"""Tactician Agent — Claude API client with tool-calling loop."""
from __future__ import annotations

import json
import os
from typing import AsyncGenerator

import anthropic
from tools import TOOL_DEFINITIONS, handle_tool_call

# ── System Prompt ────────────────────────────────────────────────────────────

TACTICIAN_SYSTEM_PROMPT = """You are the AI Tactician, a strategic marketing advisor for Brevo. You help
marketers turn their campaign ideas into fully planned, cohort-differentiated
campaign strategies.

Your workflow for any marketing request:
1. Acknowledge the user's intent and confirm your understanding
2. Gather the account context using the get_account_context tool
3. Identify the eligible audience based on the intent
4. Segment the audience using the segment_contacts tool, choosing the right
   segmentation axis based on account type (LTV for ecommerce, engagement
   for content/newsletter)
5. Generate a differentiated strategy for each cohort (high/mid/standard),
   varying: channel mix, content tone, offer/incentive, send timing
6. For each cohort, decide whether to create a campaign only, or a campaign
   + companion automation workflow. Higher-value cohorts should get both
   when the ROI justifies it (e.g., post-purchase follow-up sequences,
   non-purchaser nurture flows). Standard cohorts typically get campaign
   only — explicitly explain why in your rationale.
7. For automations: define trigger conditions, multi-step sequences with
   delays and conditions, and exit criteria
8. Present the strategy as a clear comparison across cohorts, showing both
   the campaign AND automation components where applicable
9. When the user approves, create drafts using create_campaign_draft AND/OR
   create_automation_draft per cohort as appropriate

Key principles:
- Always segment the audience — never propose a one-size-fits-all campaign
- High-value cohorts get premium, personal treatment (WhatsApp + email,
  individual send times, exclusive offers)
- Standard cohorts get cost-efficient, scaled treatment (email only, batch
  send, lighter incentives)
- Reference the account's past campaign performance to justify your
  recommendations (e.g., "Your last SMS campaign had a 14% click rate,
  so I'm including SMS for your mid-value cohort")
- If the user's intent is ambiguous, ask targeted clarifying questions to
  make sure the brief is right before proceeding
- When answering performance questions, always cite specific numbers and
  suggest actionable improvements

You have access to the following tools:
- get_account_context: Retrieves the full account snapshot
- get_campaign_history: Retrieves recent campaign performance data
- get_active_automations: Retrieves currently running automations
- segment_contacts: Segments contacts based on criteria and value axis
- create_campaign_draft: Creates a draft one-shot campaign for a specific cohort
- create_automation_draft: Creates a draft automation workflow (multi-step, trigger-based) for a specific cohort
- get_campaign_performance: Retrieves aggregate performance metrics

When presenting a campaign strategy, format your response as follows:

1. Brief text explanation of your analysis (2-3 sentences)
2. The strategy as a JSON block wrapped in <strategy> XML tags
3. A question asking the user to approve, adjust, or reject

<strategy>
{
  "campaign_name": "Campaign Name",
  "total_audience": 8200,
  "cohorts": [
    {
      "name": "High-Value",
      "tier_key": "high_value",
      "size": 2500,
      "campaign": {
        "channels": ["whatsapp", "email"],
        "offer": "Exclusive offer description",
        "content_tone": "Personal, exclusive",
        "send_timing": "Individual optimal time",
        "subject_line": "Subject line here"
      },
      "automation": {
        "included": true,
        "trigger": "trigger description",
        "steps": [
          "Step 1 description",
          "Step 2 description"
        ],
        "nurture_branch": "Description of nurture branch if applicable",
        "exit_conditions": ["purchase_made", "unsubscribed"]
      },
      "rationale": "Why this approach for this cohort"
    }
  ]
}
</strategy>

If the user says "approve", "looks good", "create drafts", or similar,
call create_campaign_draft for each cohort in the strategy.
For cohorts where automation is included, also call create_automation_draft.
If the user asks to adjust, modify the strategy based on their feedback
and present the updated version."""

# ── Agent ────────────────────────────────────────────────────────────────────

MODEL = os.getenv("TACTICIAN_MODEL", "claude-sonnet-4-5-20250929")


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


async def run_agent_stream(
    messages: list[dict],
) -> AsyncGenerator[dict, None]:
    """Run the Tactician agent with tool-calling loop, yielding events.

    Event shapes:
        {"type": "text_delta", "content": "..."}
        {"type": "tool_call_start", "tool": "name", "input": {...}}
        {"type": "tool_result", "tool": "name", "result": {...}}
        {"type": "message_done"}
    """
    client = _get_client()

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=TACTICIAN_SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        has_tool_use = False

        for block in response.content:
            if block.type == "text":
                yield {"type": "text_delta", "content": block.text}
            elif block.type == "tool_use":
                has_tool_use = True
                yield {
                    "type": "tool_call_start",
                    "tool": block.name,
                    "input": block.input,
                }

                # Execute the tool
                result = handle_tool_call(block.name, block.input)
                yield {
                    "type": "tool_result",
                    "tool": block.name,
                    "result": result,
                }

                # Append the full assistant message and tool result for next loop
                messages.append({"role": "assistant", "content": response.content})
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result),
                            }
                        ],
                    }
                )

        if response.stop_reason == "end_turn" or not has_tool_use:
            yield {"type": "message_done"}
            break


def run_agent_sync(user_message: str, conversation_history: list | None = None) -> str:
    """Synchronous convenience wrapper — returns the final text response."""
    import asyncio

    msgs = list(conversation_history or [])
    msgs.append({"role": "user", "content": user_message})

    text_parts: list[str] = []

    async def _collect():
        async for event in run_agent_stream(msgs):
            if event["type"] == "text_delta":
                text_parts.append(event["content"])

    asyncio.run(_collect())
    return "".join(text_parts)
