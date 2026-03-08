# Batch B & C Quick Reference Guide

## Quick Start: Using Services

### Rate Card Service
```python
from services.rate_card_service import RateCardService

service = RateCardService(db)

# Create rate card
rate_card = await service.create_rate_card({
    "client_org_id": 1,
    "job_category": "Software Engineer",
    "bill_rate_min": 75,
    "bill_rate_max": 150,
    "pay_rate_min": 45,
    "pay_rate_max": 95,
    "effective_from": date(2026, 1, 1),
    "entries": []
})

# Validate rates
is_valid, validation = await service.validate_submission_rates(
    client_org_id=1,
    job_category="Software Engineer",
    bill_rate=100,
    pay_rate=80
)
```

### Compliance Service
```python
from services.compliance_service import ComplianceService

service = ComplianceService(db)

# Create compliance record
record = await service.create_record({
    "placement_id": 1,
    "requirement_type": "Background Check",
    "status": "PENDING"
})

# Check placement compliance
is_compliant, status = await service.check_placement_compliance(placement_id=1)

# Calculate supplier score
score = await service.calculate_supplier_compliance_score(supplier_org_id=1)
```

### SLA Service
```python
from services.sla_service import SLAService

service = SLAService(db)

# Record breach
breach = await service.record_breach(
    sla_config_id=1,
    metric_type="response_time",
    severity="MEDIUM",
    threshold=24.0,
    actual=48.0,
    penalty=100.0
)

# Get dashboard
dashboard = await service.get_sla_dashboard(organization_id=1)
```

### VMS Timesheet Service
```python
from services.vms_timesheet_service import VMSTimesheetService

service = VMSTimesheetService(db)

# Create timesheet
ts = await service.create_vms_timesheet(
    placement_id=1,
    period_start=date(2026, 3, 1),
    period_end=date(2026, 3, 7),
    entries=[{"work_date": date(2026, 3, 1), "hours_regular": 8}],
    submitted_by=1
)

# MSP approval
ts = await service.msp_review_timesheet(timesheet_id=1, reviewer_id=2, decision="approve")

# Check compliance
compliance = await service.check_timesheet_compliance(timesheet_id=1)
```

### Auto Invoice Service
```python
from services.auto_invoice_service import AutoInvoiceService

service = AutoInvoiceService(db)

# Generate invoice
invoice = await service.generate_invoice_from_timesheets(
    client_org_id=1,
    period_start=date(2026, 3, 1),
    period_end=date(2026, 3, 31)
)

# Preview before generation
preview = await service.preview_invoice(
    client_org_id=1,
    period_start=date(2026, 3, 1),
    period_end=date(2026, 3, 31)
)
```

## Quick Start: Using Agents

### Rate Validation Agent
```python
from agents.rate_validation_agent import RateValidationAgent

agent = RateValidationAgent()

validation = agent.validate(
    proposed_bill_rate=100,
    proposed_pay_rate=80,
    rate_card={
        "bill_rate_min": 75,
        "bill_rate_max": 150,
        "pay_rate_min": 45,
        "pay_rate_max": 95
    }
)

print(f"Score: {validation.overall_score}")
print(f"Recommendation: {validation.recommendation}")
```

### Compliance Verification Agent
```python
from agents.compliance_verification_agent import ComplianceVerificationAgent

agent = ComplianceVerificationAgent()

verification = agent.verify(
    compliance_records=[
        {
            "id": 1,
            "requirement_type": "Background Check",
            "status": "COMPLETED",
            "is_mandatory": True,
            "passed": True,
            "expires_at": "2027-03-08T00:00:00"
        }
    ]
)

print(f"Risk Level: {verification.risk_level}")
print(f"Gaps: {verification.gaps}")
print(f"Recommendations: {verification.recommendations}")
```

### Workforce Forecasting Agent
```python
from agents.workforce_forecasting_agent import WorkforceForecastingAgent

agent = WorkforceForecastingAgent()

forecast = agent.forecast(
    historical_placements=[
        {
            "job_category": "Software Engineer",
            "skills": ["Python", "FastAPI"],
            "start_date": "2025-10-01"
        }
    ],
    current_active_placements=15,
    historical_peak=50
)

print(f"Predicted demand: {forecast.predicted_demand_by_category}")
print(f"Skill alerts: {forecast.skill_shortage_alerts}")
print(f"Capacity: {forecast.capacity_utilization_percent}%")
```

### Supplier Performance Prediction Agent
```python
from agents.supplier_performance_prediction_agent import SupplierPerformancePredictionAgent

agent = SupplierPerformancePredictionAgent()

prediction = agent.predict(
    supplier_data={
        "supplier_org_id": 1,
        "fill_rate": 0.85,
        "specializations": ["Python", "FastAPI", "AWS"],
        "active_placements": 8,
        "max_capacity": 20,
        "recent_fill_rate": 0.88,
        "sla_breaches_6months": 0,
        "avg_response_hours": 24
    },
    requirement_skills=["Python", "FastAPI"]
)

print(f"Fill Probability: {prediction.fill_probability}%")
print(f"Confidence: {prediction.confidence}")
print(f"Strengths: {prediction.strengths}")
print(f"Risks: {prediction.risks}")
```

### Auto Interview Scheduling Agent
```python
from agents.auto_interview_scheduling_agent import AutoInterviewSchedulingAgent

agent = AutoInterviewSchedulingAgent()

recommendation = agent.recommend_slots(
    candidate_availability=[
        {
            "date": "2026-03-15",
            "start_hour": 9,
            "end_hour": 17
        }
    ],
    interviewer_timezone="America/New_York",
    candidate_timezone="America/Los_Angeles",
    urgency_level="high",
    num_slots=5
)

print(f"Top Recommendation: {recommendation.top_recommendation}")
print(f"All Slots: {recommendation.recommended_slots}")
print(f"Timezone Score: {recommendation.timezone_match_score}")
```

## Integration Patterns

### Pattern 1: Full Rate Submission Validation
```python
# Use service to get rate card and agent to validate
rate_card_service = RateCardService(db)
validation_agent = RateValidationAgent()

# Get applicable rate card
rate_card = await rate_card_service.get_applicable_rate_card(
    client_org_id, job_category, location
)

# Validate using agent
if rate_card:
    validation = validation_agent.validate(
        proposed_bill_rate,
        proposed_pay_rate,
        rate_card=rate_card.__dict__
    )
else:
    validation = validation_agent.validate(
        proposed_bill_rate,
        proposed_pay_rate
    )

return validation
```

### Pattern 2: Placement Compliance Check
```python
# Check placement and verify risk
compliance_service = ComplianceService(db)
compliance_agent = ComplianceVerificationAgent()

# Get compliance records from service
is_compliant, status = await compliance_service.check_placement_compliance(placement_id)

# Verify with agent
records = [...]  # from database
verification = compliance_agent.verify(records)

if verification.risk_level == "HIGH":
    # Alert stakeholders
    await send_alert(f"High compliance risk: {verification.gaps}")
```

### Pattern 3: Supplier Selection with Prediction
```python
# Get candidate suppliers and predict best match
supplier_service = SupplierService(db)
prediction_agent = SupplierPerformancePredictionAgent()

suppliers = await supplier_service.get_suppliers_by_skills(skills)

predictions = []
for supplier in suppliers:
    pred = prediction_agent.predict(supplier.to_dict(), skills)
    predictions.append(pred)

# Sort by fill probability
predictions.sort(key=lambda p: p.fill_probability, reverse=True)

# Submit to top 3 with HIGH confidence
return predictions[:3]
```

## Error Handling

All services raise exceptions with meaningful messages:

```python
try:
    rate_card = await service.get_applicable_rate_card(...)
    if not rate_card:
        logger.info("No rate card found - using default")
except ValueError as e:
    logger.error(f"Invalid rate card request: {e}")
    raise
```

## Async/Await Usage

All service methods are async and require proper async context:

```python
# Correct
async def process():
    result = await service.create_record(data)
    return result

# Incorrect - will fail
result = service.create_record(data)  # Returns coroutine, not data
```

## Database Requirements

Services require SQLAlchemy AsyncSession:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...")
async_session = sessionmaker(engine, class_=AsyncSession)

async with async_session() as session:
    service = RateCardService(session)
    result = await service.create_rate_card(data)
```

## Performance Tips

1. **Rate Card Service**: Cache applicable rate cards for 1 hour
2. **Compliance Service**: Batch calculate scores during off-peak
3. **SLA Service**: Use indexed queries on severity and organization_id
4. **Timesheet Service**: Pre-validate placement existence before creation
5. **Invoice Service**: Generate invoices in batch for better performance

## Testing Agents

All agents have no database dependencies and can be unit tested easily:

```python
def test_rate_validation():
    agent = RateValidationAgent()
    result = agent.validate(100, 80)
    assert result.overall_score > 50
    assert result.recommendation in ["APPROVE", "REVIEW", "REJECT"]
```

