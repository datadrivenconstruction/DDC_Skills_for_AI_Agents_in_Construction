---
name: material-delivery-tracker
description: "Track material deliveries, manage inventory, and coordinate logistics. Monitor delivery schedules and site storage."
---

# Material Delivery Tracker

## Business Case

### Problem Statement
Material logistics cause project delays:
- Missed deliveries impact schedule
- Storage space constraints
- No visibility into delivery status
- Difficult coordination with vendors

### Solution
Centralized material delivery tracking system that manages schedules, monitors status, and coordinates site logistics.

### Business Value
- **Schedule protection** - Timely material availability
- **Cost savings** - Reduce expediting fees
- **Site efficiency** - Optimized storage planning
- **Vendor coordination** - Better communication

## Technical Implementation

```python
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DeliveryStatus(Enum):
    """Delivery status."""
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PARTIAL = "partial"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class DeliveryPriority(Enum):
    """Delivery priority."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MaterialCategory(Enum):
    """Material categories."""
    STRUCTURAL = "structural"
    CONCRETE = "concrete"
    MEP = "mep"
    FINISHES = "finishes"
    EQUIPMENT = "equipment"
    OTHER = "other"


@dataclass
class MaterialItem:
    """Material item in delivery."""
    item_id: str
    description: str
    quantity_ordered: float
    quantity_received: float
    unit: str
    category: MaterialCategory
    spec_section: str = ""
    notes: str = ""

    @property
    def is_complete(self) -> bool:
        return self.quantity_received >= self.quantity_ordered


@dataclass
class Delivery:
    """Material delivery record."""
    delivery_id: str
    po_number: str
    vendor: str
    vendor_contact: str
    vendor_phone: str
    scheduled_date: date
    priority: DeliveryPriority
    status: DeliveryStatus
    items: List[MaterialItem]
    delivery_location: str
    storage_area: str
    receiver: str = ""
    actual_date: Optional[date] = None
    tracking_number: str = ""
    carrier: str = ""
    notes: str = ""
    delay_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'delivery_id': self.delivery_id,
            'po_number': self.po_number,
            'vendor': self.vendor,
            'scheduled_date': self.scheduled_date.isoformat(),
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'status': self.status.value,
            'priority': self.priority.value,
            'items_count': len(self.items),
            'location': self.delivery_location,
            'storage': self.storage_area
        }


@dataclass
class StorageArea:
    """Site storage area."""
    area_id: str
    name: str
    location: str
    capacity_sqm: float
    current_usage_sqm: float
    material_types: List[str]
    is_covered: bool
    access_restrictions: str = ""


class MaterialDeliveryTracker:
    """Track material deliveries and logistics."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.deliveries: Dict[str, Delivery] = {}
        self.storage_areas: Dict[str, StorageArea] = {}
        self._delivery_counter = 0

    def schedule_delivery(self,
                         po_number: str,
                         vendor: str,
                         scheduled_date: date,
                         delivery_location: str,
                         storage_area: str,
                         priority: DeliveryPriority = DeliveryPriority.NORMAL,
                         vendor_contact: str = "",
                         vendor_phone: str = "") -> Delivery:
        """Schedule new delivery."""
        self._delivery_counter += 1
        delivery_id = f"DEL-{self._delivery_counter:05d}"

        delivery = Delivery(
            delivery_id=delivery_id,
            po_number=po_number,
            vendor=vendor,
            vendor_contact=vendor_contact,
            vendor_phone=vendor_phone,
            scheduled_date=scheduled_date,
            priority=priority,
            status=DeliveryStatus.SCHEDULED,
            items=[],
            delivery_location=delivery_location,
            storage_area=storage_area
        )

        self.deliveries[delivery_id] = delivery
        return delivery

    def add_item(self, delivery_id: str,
                description: str,
                quantity: float,
                unit: str,
                category: MaterialCategory,
                spec_section: str = "") -> MaterialItem:
        """Add item to delivery."""
        if delivery_id not in self.deliveries:
            raise ValueError(f"Delivery {delivery_id} not found")

        delivery = self.deliveries[delivery_id]
        item_id = f"{delivery_id}-{len(delivery.items) + 1:03d}"

        item = MaterialItem(
            item_id=item_id,
            description=description,
            quantity_ordered=quantity,
            quantity_received=0,
            unit=unit,
            category=category,
            spec_section=spec_section
        )

        delivery.items.append(item)
        return item

    def update_status(self, delivery_id: str, status: DeliveryStatus,
                     tracking_number: str = "", carrier: str = "",
                     delay_reason: str = ""):
        """Update delivery status."""
        if delivery_id not in self.deliveries:
            raise ValueError(f"Delivery {delivery_id} not found")

        delivery = self.deliveries[delivery_id]
        delivery.status = status

        if tracking_number:
            delivery.tracking_number = tracking_number
        if carrier:
            delivery.carrier = carrier
        if delay_reason:
            delivery.delay_reason = delay_reason

    def receive_delivery(self, delivery_id: str, receiver: str,
                        received_quantities: Dict[str, float] = None,
                        actual_date: date = None):
        """Record delivery receipt."""
        if delivery_id not in self.deliveries:
            raise ValueError(f"Delivery {delivery_id} not found")

        delivery = self.deliveries[delivery_id]
        delivery.receiver = receiver
        delivery.actual_date = actual_date or date.today()

        # Update received quantities
        if received_quantities:
            for item in delivery.items:
                if item.item_id in received_quantities:
                    item.quantity_received = received_quantities[item.item_id]
        else:
            # Assume full receipt
            for item in delivery.items:
                item.quantity_received = item.quantity_ordered

        # Check if all items complete
        all_complete = all(item.is_complete for item in delivery.items)
        if all_complete:
            delivery.status = DeliveryStatus.DELIVERED
        else:
            delivery.status = DeliveryStatus.PARTIAL

    def add_storage_area(self, area_id: str, name: str, location: str,
                        capacity_sqm: float, material_types: List[str],
                        is_covered: bool = False) -> StorageArea:
        """Add storage area."""
        area = StorageArea(
            area_id=area_id,
            name=name,
            location=location,
            capacity_sqm=capacity_sqm,
            current_usage_sqm=0,
            material_types=material_types,
            is_covered=is_covered
        )
        self.storage_areas[area_id] = area
        return area

    def get_upcoming_deliveries(self, days: int = 7) -> List[Delivery]:
        """Get deliveries scheduled within specified days."""
        cutoff = date.today() + timedelta(days=days)
        return [d for d in self.deliveries.values()
                if d.status in [DeliveryStatus.SCHEDULED, DeliveryStatus.IN_TRANSIT]
                and d.scheduled_date <= cutoff]

    def get_delayed_deliveries(self) -> List[Delivery]:
        """Get overdue deliveries."""
        today = date.today()
        return [d for d in self.deliveries.values()
                if d.status in [DeliveryStatus.SCHEDULED, DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELAYED]
                and d.scheduled_date < today]

    def get_deliveries_by_vendor(self, vendor: str) -> List[Delivery]:
        """Get all deliveries from a vendor."""
        return [d for d in self.deliveries.values()
                if vendor.lower() in d.vendor.lower()]

    def get_summary(self) -> Dict[str, Any]:
        """Generate delivery summary."""
        deliveries = list(self.deliveries.values())

        by_status = {}
        by_priority = {}
        by_vendor = {}

        for d in deliveries:
            status = d.status.value
            by_status[status] = by_status.get(status, 0) + 1

            priority = d.priority.value
            by_priority[priority] = by_priority.get(priority, 0) + 1

            by_vendor[d.vendor] = by_vendor.get(d.vendor, 0) + 1

        # Upcoming this week
        upcoming = self.get_upcoming_deliveries(7)
        delayed = self.get_delayed_deliveries()

        # On-time delivery rate
        completed = [d for d in deliveries if d.status == DeliveryStatus.DELIVERED]
        on_time = sum(1 for d in completed
                     if d.actual_date and d.actual_date <= d.scheduled_date)
        otd_rate = (on_time / len(completed) * 100) if completed else 0

        return {
            'project': self.project_name,
            'total_deliveries': len(deliveries),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_vendor': by_vendor,
            'upcoming_7_days': len(upcoming),
            'overdue': len(delayed),
            'on_time_delivery_rate': round(otd_rate, 1),
            'storage_areas': len(self.storage_areas)
        }

    def export_schedule(self, output_path: str):
        """Export delivery schedule to Excel."""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Delivery schedule
            schedule_data = [d.to_dict() for d in self.deliveries.values()]
            schedule_df = pd.DataFrame(schedule_data)
            if not schedule_df.empty:
                schedule_df.to_excel(writer, sheet_name='Schedule', index=False)

            # Item details
            items_data = []
            for delivery in self.deliveries.values():
                for item in delivery.items:
                    items_data.append({
                        'Delivery ID': delivery.delivery_id,
                        'PO': delivery.po_number,
                        'Item': item.description,
                        'Ordered': item.quantity_ordered,
                        'Received': item.quantity_received,
                        'Unit': item.unit,
                        'Category': item.category.value,
                        'Complete': item.is_complete
                    })
            if items_data:
                pd.DataFrame(items_data).to_excel(writer, sheet_name='Items', index=False)

            # Upcoming
            upcoming = self.get_upcoming_deliveries(14)
            if upcoming:
                upcoming_df = pd.DataFrame([d.to_dict() for d in upcoming])
                upcoming_df.to_excel(writer, sheet_name='Upcoming', index=False)

        return output_path
```

## Quick Start

```python
from datetime import date, timedelta

# Initialize tracker
tracker = MaterialDeliveryTracker("Office Tower")

# Schedule delivery
delivery = tracker.schedule_delivery(
    po_number="PO-2024-001",
    vendor="ABC Steel Supply",
    scheduled_date=date.today() + timedelta(days=7),
    delivery_location="Site Gate A",
    storage_area="Laydown Area 1",
    priority=DeliveryPriority.HIGH
)

# Add items
tracker.add_item(delivery.delivery_id, "W8x31 Beams", 50, "EA", MaterialCategory.STRUCTURAL)
tracker.add_item(delivery.delivery_id, "Connection Plates", 200, "EA", MaterialCategory.STRUCTURAL)

# Check upcoming
upcoming = tracker.get_upcoming_deliveries(7)
print(f"Deliveries this week: {len(upcoming)}")
```

## Common Use Cases

### 1. Update Transit Status
```python
tracker.update_status(delivery.delivery_id, DeliveryStatus.IN_TRANSIT,
                     tracking_number="TRACK123", carrier="XYZ Freight")
```

### 2. Receive Delivery
```python
tracker.receive_delivery(delivery.delivery_id, receiver="John Smith")
```

### 3. Monitor Delays
```python
delayed = tracker.get_delayed_deliveries()
for d in delayed:
    print(f"{d.delivery_id}: {d.vendor} - was due {d.scheduled_date}")
```

## Resources
- **DDC Book**: Chapter 3.4 - Procurement
- **Reference**: Materials Management
