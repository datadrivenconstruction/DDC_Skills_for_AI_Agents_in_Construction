---
name: toolbox-talk-generator
description: "Generate safety toolbox talks for construction crews. Create contextual safety briefings based on weather, work activities, and recent incidents. Support multiple languages."
---

# Toolbox Talk Generator

## Overview

Automatically generate relevant safety toolbox talks based on daily work activities, weather conditions, recent incidents, and seasonal hazards. Support multiple languages for diverse crews.

> "Daily toolbox talks reduce incidents by 30% when relevant to actual work" — DDC Community

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                  TOOLBOX TALK GENERATOR                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Inputs              Generator           Output                  │
│  ──────              ─────────           ──────                  │
│  📅 Today's work  →                  →  📋 Talk script          │
│  🌤️ Weather       →   🤖 AI Engine   →  📸 Visual aids          │
│  ⚠️ Recent incidents →               →  ✅ Sign-in sheet        │
│  📆 Season/holiday →                 →  🌐 Translations          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, date
import random

class HazardCategory(Enum):
    FALL_PROTECTION = "fall_protection"
    ELECTRICAL = "electrical"
    EXCAVATION = "excavation"
    SCAFFOLDING = "scaffolding"
    CRANE_RIGGING = "crane_rigging"
    CONFINED_SPACE = "confined_space"
    HOT_WORK = "hot_work"
    HAZMAT = "hazmat"
    HEAT_STRESS = "heat_stress"
    COLD_STRESS = "cold_stress"
    HOUSEKEEPING = "housekeeping"
    PPE = "ppe"
    HAND_TOOLS = "hand_tools"
    POWER_TOOLS = "power_tools"
    MATERIAL_HANDLING = "material_handling"
    TRAFFIC = "traffic"
    SILICA = "silica"
    NOISE = "noise"

@dataclass
class ToolboxTalk:
    id: str
    title: str
    category: HazardCategory
    duration_minutes: int
    content: Dict[str, str]  # sections: intro, hazards, controls, discussion, summary
    key_points: List[str]
    discussion_questions: List[str]
    date_generated: datetime = field(default_factory=datetime.now)
    language: str = "en"

@dataclass
class TalkRecord:
    talk_id: str
    date: datetime
    project: str
    location: str
    presenter: str
    attendees: List[str]
    topics_covered: List[str]
    questions_raised: List[str]
    follow_up_actions: List[str]

class ToolboxTalkGenerator:
    """Generate contextual safety toolbox talks."""

    # Talk templates by category
    TALK_TEMPLATES = {
        HazardCategory.FALL_PROTECTION: {
            "title": "Fall Protection - Stay Safe at Heights",
            "intro": "Falls are the leading cause of death in construction. Today we'll review how to protect ourselves when working at heights.",
            "hazards": [
                "Unprotected edges and openings",
                "Improper ladder use",
                "Damaged or missing guardrails",
                "Incorrect harness use",
                "Unsecured tools and materials"
            ],
            "controls": [
                "Always use guardrails at 6 feet or above",
                "Inspect harness and lanyards before each use",
                "Maintain 3 points of contact on ladders",
                "Cover all floor openings",
                "Tether tools when working at height"
            ],
            "key_points": [
                "100% tie-off required above 6 feet",
                "Inspect fall protection daily",
                "Know your anchor points",
                "Report damaged equipment immediately"
            ],
            "discussion": [
                "Where are the fall hazards on our site today?",
                "What fall protection will you use?",
                "Have you inspected your equipment?"
            ]
        },
        HazardCategory.HEAT_STRESS: {
            "title": "Heat Stress Prevention",
            "intro": "Working in hot conditions can lead to serious illness. Today we'll discuss how to recognize and prevent heat-related illness.",
            "hazards": [
                "High temperatures and humidity",
                "Direct sun exposure",
                "Physical exertion",
                "Inadequate hydration",
                "Lack of acclimatization"
            ],
            "controls": [
                "Drink water every 15-20 minutes",
                "Take breaks in shade or cool areas",
                "Wear light, breathable clothing",
                "Know the signs of heat illness",
                "Use buddy system to watch each other"
            ],
            "key_points": [
                "Water, rest, shade - the three keys",
                "Don't wait until you're thirsty to drink",
                "Stop work if you feel dizzy or nauseous",
                "Acclimatize over 7-14 days"
            ],
            "discussion": [
                "Where are the water stations today?",
                "Where can you take a cool break?",
                "What are the symptoms of heat exhaustion?"
            ]
        },
        HazardCategory.ELECTRICAL: {
            "title": "Electrical Safety",
            "intro": "Electricity can kill instantly. Today we'll review how to work safely around electrical hazards.",
            "hazards": [
                "Overhead power lines",
                "Damaged cords and equipment",
                "Wet conditions",
                "Missing GFCIs",
                "Overloaded circuits"
            ],
            "controls": [
                "Maintain 10+ feet from power lines",
                "Inspect cords before use",
                "Use GFCIs for all power tools",
                "Never use damaged equipment",
                "Keep electrical away from water"
            ],
            "key_points": [
                "Assume all wires are energized",
                "Lock out/tag out before work",
                "Only qualified personnel do electrical work",
                "Report damaged equipment immediately"
            ],
            "discussion": [
                "Where are electrical hazards on site today?",
                "Are all your tools inspected?",
                "Where are the GFCIs located?"
            ]
        },
        HazardCategory.HOUSEKEEPING: {
            "title": "Good Housekeeping = Safe Workplace",
            "intro": "A clean site is a safe site. Poor housekeeping leads to trips, falls, and fires. Let's discuss keeping our work area organized.",
            "hazards": [
                "Debris and clutter in walkways",
                "Improper material storage",
                "Tangled cords and hoses",
                "Accumulated combustibles",
                "Blocked exits and access"
            ],
            "controls": [
                "Clean as you go throughout the day",
                "Store materials properly",
                "Route cords away from walkways",
                "Dispose of waste in proper containers",
                "Keep exits and aisles clear"
            ],
            "key_points": [
                "Clean up immediately after each task",
                "Everyone is responsible for housekeeping",
                "If you see it, fix it",
                "End each day with a clean work area"
            ],
            "discussion": [
                "What areas need attention today?",
                "Where should materials be stored?",
                "Who is responsible for end-of-day cleanup?"
            ]
        },
        HazardCategory.SCAFFOLDING: {
            "title": "Scaffold Safety",
            "intro": "Scaffolds provide safe access for work at height - but only when properly erected and used. Let's review scaffold safety.",
            "hazards": [
                "Incomplete or damaged scaffolds",
                "Missing guardrails or toeboards",
                "Overloading",
                "Improper access",
                "Unstable base"
            ],
            "controls": [
                "Only use tagged scaffolds (green tag)",
                "Check for complete guardrails",
                "Use proper access (ladder, stairs)",
                "Don't overload - check capacity",
                "Never modify scaffold yourself"
            ],
            "key_points": [
                "Green tag = safe to use",
                "Red/yellow tag = do not use",
                "Inspect before each use",
                "Report problems to supervisor"
            ],
            "discussion": [
                "Is the scaffold inspected and tagged?",
                "What is the load capacity?",
                "Where is the proper access point?"
            ]
        }
    }

    # Weather-related topic mapping
    WEATHER_TOPICS = {
        "hot": [HazardCategory.HEAT_STRESS],
        "cold": [HazardCategory.COLD_STRESS],
        "rain": [HazardCategory.ELECTRICAL, HazardCategory.HOUSEKEEPING],
        "wind": [HazardCategory.CRANE_RIGGING, HazardCategory.SCAFFOLDING],
        "snow": [HazardCategory.COLD_STRESS, HazardCategory.HOUSEKEEPING]
    }

    # Activity-related topic mapping
    ACTIVITY_TOPICS = {
        "concrete": [HazardCategory.SILICA, HazardCategory.MATERIAL_HANDLING],
        "steel": [HazardCategory.CRANE_RIGGING, HazardCategory.FALL_PROTECTION],
        "electrical": [HazardCategory.ELECTRICAL],
        "excavation": [HazardCategory.EXCAVATION],
        "roofing": [HazardCategory.FALL_PROTECTION, HazardCategory.HEAT_STRESS],
        "welding": [HazardCategory.HOT_WORK, HazardCategory.PPE],
        "demolition": [HazardCategory.SILICA, HazardCategory.HOUSEKEEPING],
        "painting": [HazardCategory.HAZMAT, HazardCategory.PPE]
    }

    def __init__(self):
        self.generated_talks: Dict[str, ToolboxTalk] = {}
        self.talk_records: List[TalkRecord] = []

    def generate_talk(self, category: HazardCategory,
                     language: str = "en",
                     custom_points: List[str] = None) -> ToolboxTalk:
        """Generate toolbox talk for category."""
        template = self.TALK_TEMPLATES.get(category)

        if not template:
            # Generate generic talk
            template = self._generate_generic_template(category)

        talk_id = f"TBT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        content = {
            "intro": template["intro"],
            "hazards": "\n".join(f"• {h}" for h in template["hazards"]),
            "controls": "\n".join(f"• {c}" for c in template["controls"]),
            "summary": f"Remember: {template['key_points'][0]}"
        }

        key_points = template["key_points"].copy()
        if custom_points:
            key_points.extend(custom_points)

        talk = ToolboxTalk(
            id=talk_id,
            title=template["title"],
            category=category,
            duration_minutes=10,
            content=content,
            key_points=key_points,
            discussion_questions=template.get("discussion", []),
            language=language
        )

        self.generated_talks[talk_id] = talk
        return talk

    def _generate_generic_template(self, category: HazardCategory) -> Dict:
        """Generate generic template for unmapped categories."""
        name = category.value.replace("_", " ").title()
        return {
            "title": f"{name} Safety",
            "intro": f"Today we'll discuss {name.lower()} safety and how to protect ourselves.",
            "hazards": [
                f"Common {name.lower()} hazards on site",
                "Lack of awareness",
                "Rushing or taking shortcuts",
                "Not following procedures"
            ],
            "controls": [
                "Follow all safety procedures",
                "Use required PPE",
                "Report hazards immediately",
                "Ask if unsure"
            ],
            "key_points": [
                "Safety first - always",
                "If unsure, ask your supervisor",
                "Report all hazards"
            ],
            "discussion": [
                f"What {name.lower()} hazards exist on site today?",
                "What controls will you use?",
                "Any questions or concerns?"
            ]
        }

    def suggest_topics(self, weather: str = None,
                      activities: List[str] = None,
                      recent_incidents: List[str] = None) -> List[HazardCategory]:
        """Suggest relevant topics based on context."""
        suggestions = set()

        # Weather-based suggestions
        if weather:
            weather_lower = weather.lower()
            for condition, topics in self.WEATHER_TOPICS.items():
                if condition in weather_lower:
                    suggestions.update(topics)

        # Activity-based suggestions
        if activities:
            for activity in activities:
                activity_lower = activity.lower()
                for key, topics in self.ACTIVITY_TOPICS.items():
                    if key in activity_lower:
                        suggestions.update(topics)

        # Incident-based suggestions
        if recent_incidents:
            for incident in recent_incidents:
                incident_lower = incident.lower()
                if "fall" in incident_lower:
                    suggestions.add(HazardCategory.FALL_PROTECTION)
                if "electric" in incident_lower:
                    suggestions.add(HazardCategory.ELECTRICAL)
                if "struck" in incident_lower:
                    suggestions.add(HazardCategory.MATERIAL_HANDLING)

        # Default suggestion if none
        if not suggestions:
            suggestions.add(HazardCategory.HOUSEKEEPING)

        return list(suggestions)

    def generate_daily_talk(self, project: str,
                           weather: str,
                           activities: List[str],
                           recent_incidents: List[str] = None) -> ToolboxTalk:
        """Generate contextual daily toolbox talk."""
        topics = self.suggest_topics(weather, activities, recent_incidents)

        # Pick most relevant topic
        primary_topic = topics[0] if topics else HazardCategory.HOUSEKEEPING

        # Add context-specific points
        custom_points = []
        if weather:
            custom_points.append(f"Today's weather: {weather} - plan accordingly")
        if activities:
            custom_points.append(f"Today's focus: {', '.join(activities)}")

        talk = self.generate_talk(primary_topic, custom_points=custom_points)
        return talk

    def format_talk_script(self, talk: ToolboxTalk) -> str:
        """Format talk as presenter script."""
        lines = [
            f"# {talk.title}",
            f"",
            f"**Duration:** {talk.duration_minutes} minutes",
            f"**Category:** {talk.category.value}",
            f"**Date:** {talk.date_generated.strftime('%Y-%m-%d')}",
            f"",
            f"---",
            f"",
            f"## Introduction",
            f"",
            talk.content["intro"],
            f"",
            f"## Hazards to Watch For",
            f"",
            talk.content["hazards"],
            f"",
            f"## How to Protect Yourself",
            f"",
            talk.content["controls"],
            f"",
            f"## Key Points to Remember",
            f"",
        ]

        for point in talk.key_points:
            lines.append(f"✓ {point}")

        lines.extend([
            f"",
            f"## Discussion Questions",
            f""
        ])

        for q in talk.discussion_questions:
            lines.append(f"❓ {q}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"**Closing:** Work safe today. If you see something, say something. Any questions?"
        ])

        return "\n".join(lines)

    def record_talk(self, talk_id: str, project: str, location: str,
                   presenter: str, attendees: List[str],
                   questions: List[str] = None,
                   follow_ups: List[str] = None) -> TalkRecord:
        """Record completed toolbox talk."""
        if talk_id not in self.generated_talks:
            raise ValueError(f"Talk {talk_id} not found")

        talk = self.generated_talks[talk_id]

        record = TalkRecord(
            talk_id=talk_id,
            date=datetime.now(),
            project=project,
            location=location,
            presenter=presenter,
            attendees=attendees,
            topics_covered=[talk.category.value],
            questions_raised=questions or [],
            follow_up_actions=follow_ups or []
        )

        self.talk_records.append(record)
        return record

    def get_attendance_summary(self, project: str = None,
                              start_date: datetime = None) -> Dict:
        """Get toolbox talk attendance summary."""
        records = self.talk_records

        if project:
            records = [r for r in records if r.project == project]
        if start_date:
            records = [r for r in records if r.date >= start_date]

        total_talks = len(records)
        total_attendees = sum(len(r.attendees) for r in records)
        unique_attendees = len(set(a for r in records for a in r.attendees))

        topics_covered = {}
        for r in records:
            for topic in r.topics_covered:
                topics_covered[topic] = topics_covered.get(topic, 0) + 1

        return {
            "total_talks": total_talks,
            "total_attendees": total_attendees,
            "unique_workers": unique_attendees,
            "avg_attendance": total_attendees / total_talks if total_talks else 0,
            "topics_covered": topics_covered
        }
```

## Quick Start

```python
# Initialize generator
generator = ToolboxTalkGenerator()

# Generate contextual daily talk
talk = generator.generate_daily_talk(
    project="Office Tower",
    weather="Hot, 95°F, sunny",
    activities=["concrete pour", "steel erection"],
    recent_incidents=["near miss - unsecured tool dropped"]
)

# Get formatted script
script = generator.format_talk_script(talk)
print(script)

# Record attendance
record = generator.record_talk(
    talk_id=talk.id,
    project="Office Tower",
    location="Level 5 staging area",
    presenter="John Smith",
    attendees=["Worker 1", "Worker 2", "Worker 3"],
    questions=["Where are the water coolers?"],
    follow_ups=["Add water station near grid C"]
)

# Get summary
summary = generator.get_attendance_summary()
print(f"Total talks: {summary['total_talks']}")
print(f"Unique workers trained: {summary['unique_workers']}")
```

## Requirements

```bash
pip install (no external dependencies)
```

## Integration with LLM

```python
def generate_with_llm(topic: str, context: str) -> str:
    """Use LLM to generate custom toolbox talk."""
    prompt = f"""
    Generate a 10-minute toolbox talk for construction workers about: {topic}

    Context: {context}

    Include:
    1. Brief introduction (why this matters)
    2. 4-5 specific hazards
    3. 4-5 control measures
    4. 3 key points to remember
    5. 2-3 discussion questions

    Keep language simple and direct. Workers have varying English levels.
    """

    # Call your LLM API here
    # response = llm.generate(prompt)
    return response
```
