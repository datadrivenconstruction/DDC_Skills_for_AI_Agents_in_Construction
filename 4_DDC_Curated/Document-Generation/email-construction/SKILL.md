---
name: email-construction
description: "Email generation for construction workflows: RFI responses, submittal transmittals, meeting notices, change order notifications. Professional templates with context-aware content."
---

# Email Generation for Construction

## Overview

Generate professional construction emails with proper formatting, context, and attachments handling. Templates for common construction communication workflows.

## Construction Use Cases

### 1. RFI Response Email

Generate professional RFI response emails.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class RFIResponse:
    rfi_number: str
    project_name: str
    subject: str
    question: str
    response: str
    responder_name: str
    responder_title: str
    attachments: List[str] = None
    cc_list: List[str] = None

def generate_rfi_response_email(rfi: RFIResponse) -> dict:
    """Generate RFI response email."""

    subject = f"RE: RFI #{rfi.rfi_number} - {rfi.subject}"

    body = f"""Dear Project Team,

Please find below our response to RFI #{rfi.rfi_number}.

**Project:** {rfi.project_name}
**RFI Number:** {rfi.rfi_number}
**Subject:** {rfi.subject}
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

**QUESTION:**
{rfi.question}

---

**RESPONSE:**
{rfi.response}

---

Please proceed accordingly. If you have any questions regarding this response, please contact us.

{"**Attachments:**" + chr(10) + chr(10).join(f"- {a}" for a in rfi.attachments) if rfi.attachments else ""}

Best regards,

{rfi.responder_name}
{rfi.responder_title}
"""

    return {
        'subject': subject,
        'body': body,
        'cc': rfi.cc_list or [],
        'attachments': rfi.attachments or []
    }
```

### 2. Submittal Transmittal Email

Generate submittal transmittal emails.

```python
@dataclass
class SubmittalTransmittal:
    submittal_number: str
    project_name: str
    spec_section: str
    description: str
    items: List[dict]
    action_required: str
    due_date: str
    sender_name: str
    sender_company: str

def generate_submittal_email(submittal: SubmittalTransmittal) -> dict:
    """Generate submittal transmittal email."""

    subject = f"Submittal {submittal.submittal_number} - {submittal.spec_section} - {submittal.description}"

    items_list = "\n".join(
        f"   {i+1}. {item['description']} ({item.get('copies', 1)} copies)"
        for i, item in enumerate(submittal.items)
    )

    body = f"""Dear Design Team,

Please find attached Submittal {submittal.submittal_number} for your review.

**Project:** {submittal.project_name}
**Submittal No:** {submittal.submittal_number}
**Spec Section:** {submittal.spec_section}
**Description:** {submittal.description}

**Items Transmitted:**
{items_list}

**Action Required:** {submittal.action_required}
**Response Requested By:** {submittal.due_date}

Please review and return with your comments at your earliest convenience.
If you have any questions, please don't hesitate to contact us.

Best regards,

{submittal.sender_name}
{submittal.sender_company}
"""

    return {
        'subject': subject,
        'body': body,
        'priority': 'normal'
    }
```

### 3. Meeting Notice Email

Generate meeting invitation emails.

```python
@dataclass
class MeetingNotice:
    meeting_type: str  # 'OAC', 'Subcontractor', 'Safety', 'Coordination'
    project_name: str
    date: str
    time: str
    location: str
    virtual_link: Optional[str]
    agenda_items: List[str]
    attendees: List[str]
    organizer_name: str

def generate_meeting_notice(meeting: MeetingNotice) -> dict:
    """Generate meeting notice email."""

    subject = f"{meeting.meeting_type} Meeting - {meeting.project_name} - {meeting.date}"

    agenda = "\n".join(f"   {i+1}. {item}" for i, item in enumerate(meeting.agenda_items))

    location_info = meeting.location
    if meeting.virtual_link:
        location_info += f"\n   Virtual Option: {meeting.virtual_link}"

    body = f"""Dear Team,

You are invited to the {meeting.meeting_type} Meeting for {meeting.project_name}.

**Meeting Details:**
- **Date:** {meeting.date}
- **Time:** {meeting.time}
- **Location:** {location_info}

**Agenda:**
{agenda}

**Attendees:**
{', '.join(meeting.attendees)}

Please confirm your attendance by replying to this email.
If you cannot attend, please send a delegate and notify the organizer.

Regards,

{meeting.organizer_name}
Project Manager
"""

    return {
        'subject': subject,
        'body': body,
        'to': meeting.attendees,
        'calendar_invite': {
            'start': f"{meeting.date} {meeting.time}",
            'duration': 60,
            'location': meeting.location
        }
    }
```

### 4. Change Order Notification

Generate change order notification emails.

```python
@dataclass
class ChangeOrderNotification:
    co_number: str
    project_name: str
    description: str
    amount: float
    schedule_impact: str
    reason: str
    status: str  # 'Pending', 'Approved', 'Rejected'
    sender_name: str
    sender_title: str

def generate_change_order_email(co: ChangeOrderNotification) -> dict:
    """Generate change order notification email."""

    subject = f"Change Order #{co.co_number} - {co.status} - {co.project_name}"

    amount_str = f"${co.amount:,.2f}"
    if co.amount < 0:
        amount_str = f"(${abs(co.amount):,.2f}) Credit"

    body = f"""Dear Project Team,

This email is to notify you of Change Order #{co.co_number} for {co.project_name}.

**Change Order Details:**
- **CO Number:** {co.co_number}
- **Status:** {co.status}
- **Description:** {co.description}

**Financial Impact:**
- **Amount:** {amount_str}

**Schedule Impact:**
- {co.schedule_impact}

**Reason for Change:**
{co.reason}

{"Please review the attached documentation and provide your approval." if co.status == 'Pending' else ""}
{"This change order has been approved. Please proceed accordingly." if co.status == 'Approved' else ""}

If you have any questions, please contact the project team.

Best regards,

{co.sender_name}
{co.sender_title}
"""

    return {
        'subject': subject,
        'body': body,
        'priority': 'high' if co.status == 'Pending' else 'normal',
        'flag': co.status == 'Pending'
    }
```

### 5. Daily Report Email

Generate daily report distribution email.

```python
@dataclass
class DailyReportEmail:
    project_name: str
    report_date: str
    report_number: int
    weather: str
    workforce_total: int
    work_summary: List[str]
    issues: List[str]
    sender_name: str

def generate_daily_report_email(report: DailyReportEmail) -> dict:
    """Generate daily report distribution email."""

    subject = f"Daily Report #{report.report_number} - {report.project_name} - {report.report_date}"

    work_items = "\n".join(f"• {item}" for item in report.work_summary)
    issues_text = "\n".join(f"• {issue}" for issue in report.issues) if report.issues else "None"

    body = f"""Daily Construction Report

**Project:** {report.project_name}
**Date:** {report.report_date}
**Report #:** {report.report_number}

---

**Weather:** {report.weather}
**Total Workforce:** {report.workforce_total} workers on-site

---

**Work Completed:**
{work_items}

---

**Issues/Delays:**
{issues_text}

---

Full report attached. Please contact the site office with any questions.

{report.sender_name}
Site Superintendent
"""

    return {
        'subject': subject,
        'body': body,
        'attachments': [f'Daily_Report_{report.report_number}.pdf']
    }
```

### 6. Delay Notice Email

Generate formal delay notification.

```python
@dataclass
class DelayNotice:
    project_name: str
    contract_number: str
    delay_type: str  # 'Excusable', 'Non-Excusable', 'Compensable'
    cause: str
    affected_activities: List[str]
    original_completion: str
    revised_completion: str
    days_impacted: int
    mitigation_plan: str
    sender_name: str
    sender_title: str

def generate_delay_notice_email(delay: DelayNotice) -> dict:
    """Generate formal delay notice email."""

    subject = f"NOTICE OF DELAY - {delay.project_name} - {delay.days_impacted} Days"

    activities = "\n".join(f"   - {a}" for a in delay.affected_activities)

    body = f"""NOTICE OF DELAY

**Project:** {delay.project_name}
**Contract No:** {delay.contract_number}
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

Dear Owner/Owner's Representative,

In accordance with the contract requirements, this letter serves as formal notice of a delay to the project schedule.

**Delay Classification:** {delay.delay_type}

**Cause of Delay:**
{delay.cause}

**Affected Activities:**
{activities}

**Schedule Impact:**
- Original Completion Date: {delay.original_completion}
- Revised Completion Date: {delay.revised_completion}
- Calendar Days Impacted: {delay.days_impacted}

**Mitigation Plan:**
{delay.mitigation_plan}

We request a meeting to discuss this matter and coordinate recovery efforts. Please contact us at your earliest convenience.

This notice is provided without prejudice to any rights or remedies available under the contract.

Respectfully,

{delay.sender_name}
{delay.sender_title}
"""

    return {
        'subject': subject,
        'body': body,
        'priority': 'high',
        'read_receipt': True,
        'delivery_receipt': True
    }
```

## Email Sending Integration

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class ConstructionEmailSender:
    """Send construction emails via SMTP."""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send(self, to: List[str], email_data: dict, from_addr: str = None):
        """Send email with optional attachments."""
        msg = MIMEMultipart()
        msg['From'] = from_addr or self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = email_data['subject']

        if email_data.get('cc'):
            msg['Cc'] = ', '.join(email_data['cc'])

        if email_data.get('priority') == 'high':
            msg['X-Priority'] = '1'

        msg.attach(MIMEText(email_data['body'], 'plain'))

        # Add attachments
        for attachment_path in email_data.get('attachments', []):
            with open(attachment_path, 'rb') as f:
                part = MIMEApplication(f.read())
                part.add_header('Content-Disposition', 'attachment',
                               filename=attachment_path.split('/')[-1])
                msg.attach(part)

        # Send
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)

            recipients = to + email_data.get('cc', [])
            server.sendmail(msg['From'], recipients, msg.as_string())
```

## Integration with DDC Pipeline

```python
# Example: Auto-generate RFI response email from RFI log
import pandas as pd

# Load RFI log
rfi_log = pd.read_excel("RFI_Log.xlsx")

# Get pending RFI
pending_rfi = rfi_log[rfi_log['status'] == 'Response Ready'].iloc[0]

# Generate email
rfi = RFIResponse(
    rfi_number=pending_rfi['rfi_number'],
    project_name=pending_rfi['project'],
    subject=pending_rfi['subject'],
    question=pending_rfi['question'],
    response=pending_rfi['response'],
    responder_name='John Smith',
    responder_title='Project Architect',
    attachments=['SK-001.pdf']
)

email_data = generate_rfi_response_email(rfi)
print(f"Subject: {email_data['subject']}")
print(email_data['body'])
```

## Email Templates Library

Common email templates for construction:

| Template | Use Case |
|----------|----------|
| RFI Response | Responding to Requests for Information |
| Submittal Transmittal | Sending submittals for review |
| Meeting Notice | OAC, subcontractor, safety meetings |
| Change Order | CO notifications and approvals |
| Daily Report | Daily report distribution |
| Delay Notice | Formal delay notifications |
| Payment Application | Pay app submissions |
| Punch List | Punch list item notifications |
| Closeout | Warranty and closeout docs |

## Resources

- **Professional Email Writing**: Keep emails concise and action-oriented
- **Construction Email Best Practices**: Always include project name and reference numbers
- **Legal Considerations**: Delay notices may have contractual requirements
