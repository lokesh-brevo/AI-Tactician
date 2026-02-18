"""Pydantic models for all request/response types."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


# ── Account Context ──────────────────────────────────────────────────────────

class ChannelConfig(BaseModel):
    enabled: bool
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subscribers: Optional[int] = None
    avg_deliverability: Optional[float] = None
    template_approved: Optional[bool] = None

class Product(BaseModel):
    name: str
    price: float
    category: str
    launched: str

class EcommerceData(BaseModel):
    total_customers: int
    avg_order_value: float
    avg_ltv: float
    top_categories: list[str]
    recent_products: list[Product]

class EngagementSummary(BaseModel):
    avg_open_rate: float
    avg_click_rate: float
    avg_sms_click_rate: float
    best_send_day: str
    best_send_hour: int
    last_30d_campaigns_sent: int

class AccountInfo(BaseModel):
    id: str
    name: str
    type: str
    platform: str
    created_at: str
    plan: str

class AccountContext(BaseModel):
    account: AccountInfo
    channels: dict[str, ChannelConfig]
    ecommerce: EcommerceData
    engagement_summary: EngagementSummary


# ── Segmentation ─────────────────────────────────────────────────────────────

class BaseFilter(BaseModel):
    type: str
    days: Optional[int] = None
    list_id: Optional[str] = None

class SegmentRequest(BaseModel):
    base_filter: BaseFilter
    segmentation_axis: str
    tiers: Optional[dict] = None

class TierStats(BaseModel):
    count: int
    pct: float
    avg_ltv: float
    avg_orders: float
    avg_aov: float
    top_categories: list[str]
    channels_opted_in: dict[str, int]
    avg_engagement_score: float

class SegmentResponse(BaseModel):
    total_eligible: int
    tiers: dict[str, TierStats]


# ── Campaign History ─────────────────────────────────────────────────────────

class Campaign(BaseModel):
    id: str
    name: str
    type: str
    sent_at: str
    audience_size: int
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    revenue: Optional[float] = None
    subject_line: Optional[str] = None
    message_preview: Optional[str] = None

class CampaignHistory(BaseModel):
    campaigns: list[Campaign]


# ── Automations ──────────────────────────────────────────────────────────────

class Automation(BaseModel):
    id: str
    name: str
    trigger: str
    status: str
    steps: int
    contacts_in_flow: int
    avg_completion_rate: float

class AutomationsList(BaseModel):
    automations: list[Automation]


# ── Draft Campaign ───────────────────────────────────────────────────────────

class CampaignContent(BaseModel):
    subject: Optional[str] = None
    body: str
    cta: str
    offer: Optional[str] = None

class CampaignSchedule(BaseModel):
    type: str  # individual_optimal | segment_optimal | batch

class CampaignDraftRequest(BaseModel):
    name: str
    channel: str
    cohort: str
    audience_size: int
    content: CampaignContent
    schedule: CampaignSchedule

class CampaignDraftResponse(BaseModel):
    draft_id: str
    status: str = "draft"
    preview_url: str
    created_at: str


# ── Draft Automation ─────────────────────────────────────────────────────────

class AutomationTrigger(BaseModel):
    type: str
    value: Optional[int] = None

class AutomationStepContent(BaseModel):
    subject: Optional[str] = None
    body: str
    cta: str

class AutomationStep(BaseModel):
    order: int
    channel: str
    delay: str
    condition: Optional[str] = None
    content: AutomationStepContent

class AutomationDraftRequest(BaseModel):
    name: str
    cohort: str
    trigger: AutomationTrigger
    steps: list[AutomationStep]
    exit_conditions: list[str]

class AutomationDraftResponse(BaseModel):
    workflow_id: str
    status: str = "draft"
    preview_url: str
    created_at: str
    estimated_contacts_entering: Optional[int] = None


# ── Performance ──────────────────────────────────────────────────────────────

class PerformerInfo(BaseModel):
    name: str
    open_rate: float
    revenue: float

class PerformanceSummary(BaseModel):
    campaigns_sent: int
    total_recipients: int
    avg_open_rate: float
    avg_click_rate: float
    total_revenue: float
    best_performer: PerformerInfo
    worst_performer: PerformerInfo

class PerformanceTrends(BaseModel):
    open_rate_trend: str
    click_rate_trend: str
    revenue_trend: str

class PerformanceReport(BaseModel):
    period: str
    summary: PerformanceSummary
    trends: PerformanceTrends


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
