"""Transactional email via Resend.

Sending is best-effort: if RESEND_API_KEY isn't configured, or the API call
fails, callers should treat it as "not sent" and carry on rather than fail
the surrounding request — a provider brief is still fully usable as a link
even if the email notification didn't go out.
"""
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("email")

RESEND_API_URL = "https://api.resend.com/emails"

URGENCY_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#ca8a04",
    "low": "#6b7280",
}


def is_configured() -> bool:
    return bool(settings.RESEND_API_KEY)


async def send_brief_email(
    to_email: str,
    brief_url: str,
    opportunity_title: str,
    opportunity_category: str,
    opportunity_urgency: str,
    intent_score: float,
    why_now: Optional[str] = None,
    provider_name: Optional[str] = None,
    expires_at_label: Optional[str] = None,
) -> bool:
    """Send the brief-link notification email. Returns True if Resend accepted it.

    Never raises — a failure here should not block brief generation or any
    other caller's flow. Logs the failure and returns False instead.
    """
    if not is_configured():
        logger.info("RESEND_API_KEY not set — skipping brief email to %s", to_email)
        return False

    html = _render_brief_email_html(
        brief_url=brief_url,
        opportunity_title=opportunity_title,
        opportunity_category=opportunity_category,
        opportunity_urgency=opportunity_urgency,
        intent_score=intent_score,
        why_now=why_now,
        provider_name=provider_name,
        expires_at_label=expires_at_label,
    )
    text = _render_brief_email_text(
        brief_url=brief_url,
        opportunity_title=opportunity_title,
        opportunity_category=opportunity_category,
        opportunity_urgency=opportunity_urgency,
        intent_score=intent_score,
        why_now=why_now,
        provider_name=provider_name,
        expires_at_label=expires_at_label,
    )

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": f"New opportunity match: {opportunity_title}",
        "html": html,
        # A plain-text alternative alongside HTML is a well-known spam-score
        # signal — HTML-only mail from a new sending domain gets scrutinized
        # harder by Gmail/Yahoo spam filters than genuine multipart mail.
        "text": text,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if response.status_code >= 400:
            logger.warning(
                "Resend rejected brief email to %s: %s %s",
                to_email, response.status_code, response.text[:500],
            )
            return False
        return True
    except httpx.HTTPError as e:
        logger.warning("Resend request failed for %s: %s", to_email, e)
        return False


def _render_brief_email_html(
    *,
    brief_url: str,
    opportunity_title: str,
    opportunity_category: str,
    opportunity_urgency: str,
    intent_score: float,
    why_now: Optional[str],
    provider_name: Optional[str],
    expires_at_label: Optional[str],
) -> str:
    """Table-based layout with inline styles — the two things that survive
    every major email client (Gmail, Outlook, Apple Mail), unlike flexbox/grid
    or a <style> block, which Outlook in particular strips or mishandles."""
    greeting = f"Hi {_escape(provider_name)}," if provider_name else "Hi,"
    urgency_color = URGENCY_COLORS.get(opportunity_urgency, URGENCY_COLORS["medium"])
    score_pct = round(intent_score * 100)

    why_now_block = ""
    if why_now:
        why_now_block = f"""
        <tr>
          <td style="padding:0 32px 24px 32px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f0fdfa;border:1px solid #99f6e4;border-radius:12px;">
              <tr>
                <td style="padding:16px 20px;">
                  <p style="margin:0 0 4px 0;font-size:12px;font-weight:600;color:#0f766e;text-transform:uppercase;letter-spacing:0.05em;">Why This Matters Now</p>
                  <p style="margin:0;font-size:14px;line-height:1.5;color:#134e4a;">{_escape(why_now)}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    expiry_line = (
        f'<p style="margin:12px 0 0 0;font-size:12px;color:#9ca3af;">This link expires {_escape(expires_at_label)}.</p>'
        if expires_at_label else ""
    )

    return f"""\
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;">

          <!-- Header -->
          <tr>
            <td style="background:#0f172a;padding:24px 32px;">
              <p style="margin:0;font-size:15px;font-weight:700;color:#ffffff;">Intent Radar</p>
              <p style="margin:2px 0 0 0;font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;">Commercial Intelligence Platform</p>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:32px 32px 8px 32px;">
              <p style="margin:0 0 16px 0;font-size:15px;color:#374151;">{greeting}</p>
              <p style="margin:0 0 24px 0;font-size:15px;line-height:1.5;color:#374151;">
                You've been matched to a new commercial opportunity based on your profile. Here's a quick summary:
              </p>
            </td>
          </tr>

          <!-- Opportunity card -->
          <tr>
            <td style="padding:0 32px 24px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;">
                <tr>
                  <td style="padding:20px;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td>
                          <span style="display:inline-block;font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;background:#e5e7eb;border-radius:4px;padding:2px 8px;">{_escape(opportunity_category)}</span>
                          <span style="display:inline-block;font-size:11px;font-weight:600;color:#ffffff;text-transform:uppercase;background:{urgency_color};border-radius:9999px;padding:2px 10px;margin-left:6px;">{_escape(opportunity_urgency)} urgency</span>
                        </td>
                        <td align="right">
                          <span style="font-size:20px;font-weight:700;color:#111827;">{score_pct}%</span>
                          <span style="display:block;font-size:10px;color:#9ca3af;">Intent Score</span>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:14px 0 0 0;font-size:16px;font-weight:700;color:#111827;">{_escape(opportunity_title)}</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {why_now_block}

          <!-- CTA -->
          <tr>
            <td style="padding:0 32px 32px 32px;" align="center">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-radius:12px;background:#0d9488;">
                    <a href="{brief_url}" target="_blank" style="display:inline-block;padding:14px 32px;font-size:14px;font-weight:600;color:#ffffff;text-decoration:none;">
                      View Full Opportunity &amp; Respond
                    </a>
                  </td>
                </tr>
              </table>
              {expiry_line}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;font-size:11px;color:#9ca3af;text-align:center;">
                Sent by Intent Radar. If the button above doesn't work, copy and paste this link:<br>
                <a href="{brief_url}" style="color:#0d9488;">{brief_url}</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _render_brief_email_text(
    *,
    brief_url: str,
    opportunity_title: str,
    opportunity_category: str,
    opportunity_urgency: str,
    intent_score: float,
    why_now: Optional[str],
    provider_name: Optional[str],
    expires_at_label: Optional[str],
) -> str:
    """Plain-text alternative to the HTML email — not just a deliverability
    signal, also what actually renders for text-only mail clients/readers."""
    greeting = f"Hi {provider_name}," if provider_name else "Hi,"
    score_pct = round(intent_score * 100)

    lines = [
        greeting,
        "",
        "You've been matched to a new commercial opportunity based on your profile.",
        "",
        f"{opportunity_title}",
        f"Category: {opportunity_category} | Urgency: {opportunity_urgency} | Intent Score: {score_pct}%",
    ]
    if why_now:
        lines += ["", "Why This Matters Now:", why_now]
    lines += ["", f"View the full opportunity and respond: {brief_url}"]
    if expires_at_label:
        lines += ["", f"This link expires {expires_at_label}."]
    lines += ["", "-- Intent Radar, Commercial Intelligence Platform"]

    return "\n".join(lines)


def _escape(text: Optional[str]) -> str:
    """Minimal HTML escaping for values interpolated into the template."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
