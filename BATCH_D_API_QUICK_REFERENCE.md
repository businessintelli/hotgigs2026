# Batch D VMS Enhancement - API Quick Reference

## All 27 New Endpoints

### Rate Cards (`/api/v1/rate-cards`)

```
POST   /rate-cards
       Create rate card with entries
       Body: RateCardCreate
       Returns: RateCardResponse (201)

GET    /rate-cards
       List rate cards
       Params: client_org_id?, status?
       Returns: List[RateCardResponse]

GET    /rate-cards/{id}
       Get rate card by ID
       Returns: RateCardResponse

PUT    /rate-cards/{id}
       Update rate card
       Body: RateCardUpdate
       Returns: RateCardResponse

POST   /rate-cards/validate
       Validate rates against card
       Body: RateValidationRequest
       Returns: RateValidationResponse

DELETE /rate-cards/{id}
       Archive rate card (soft delete)
       Returns: 204 No Content
```

---

### Compliance Management (`/api/v1/compliance`)

```
POST   /compliance/requirements
       Create compliance requirement
       Body: ComplianceRequirementCreate
       Returns: ComplianceRequirementResponse (201)

GET    /compliance/requirements
       List requirements
       Params: org_id?, requirement_type?
       Returns: List[ComplianceRequirementResponse]

POST   /compliance/records
       Create compliance record
       Body: ComplianceRecordCreate
       Returns: ComplianceRecordResponse (201)

PUT    /compliance/records/{id}
       Update record status
       Body: ComplianceRecordUpdate
       Returns: ComplianceRecordResponse

GET    /compliance/placement/{placement_id}
       Check placement compliance
       Returns: PlacementComplianceResponse

GET    /compliance/supplier/{supplier_org_id}/score
       Get supplier compliance score
       Returns: ComplianceScoreResponse

GET    /compliance/expiring
       Get expiring compliance items
       Params: days=30
       Returns: List[ComplianceRecordResponse]
```

---

### SLA Management (`/api/v1/sla`)

```
POST   /sla/configurations
       Create SLA configuration
       Body: SLAConfigurationCreate
       Returns: SLAConfigurationResponse (201)

GET    /sla/configurations
       List SLA configurations
       Params: org_id?
       Returns: List[SLAConfigurationResponse]

POST   /sla/detect-breaches
       Trigger breach detection
       Params: organization_id (required)
       Returns: {"organization_id": int, "breaches_detected": int, "status": str}

GET    /sla/breaches
       List SLA breaches
       Params: org_id?, severity?, metric_type?, is_resolved?
       Returns: List[SLABreachResponse]

PUT    /sla/breaches/{id}/resolve
       Resolve a breach
       Body: SLABreachResolve (resolution_notes: str)
       Returns: SLABreachResponse

GET    /sla/dashboard
       Get SLA dashboard
       Params: org_id (required)
       Returns: SLADashboardResponse
```

---

### VMS Timesheets (`/api/v1/vms`)

```
POST   /vms/timesheets
       Supplier submits timesheet
       Body: TimesheetCreate
       Returns: TimesheetResponse (201)

GET    /vms/timesheets
       List timesheets
       Params: status?, org_type?, period?
       Returns: List[TimesheetResponse]

PUT    /vms/timesheets/{id}/msp-review
       MSP reviews timesheet
       Body: TimesheetApproveRequest
       Returns: TimesheetResponse

PUT    /vms/timesheets/{id}/client-approve
       Client approves timesheet
       Body: TimesheetApproveRequest
       Returns: TimesheetResponse

GET    /vms/timesheets/{id}/compliance-check
       Check timesheet compliance
       Returns: {"timesheet_id": int, "is_compliant": bool, "issues": [...]}
```

---

### Auto Invoicing (`/api/v1/invoicing`)

```
POST   /invoicing/generate
       Generate invoices from timesheets
       Params: client_org_id, period_start, period_end
       Returns: InvoiceResponse (201)

POST   /invoicing/preview
       Preview invoice generation
       Params: client_org_id, period_start, period_end
       Returns: {
                  "client_org_id": int,
                  "period_start": str,
                  "period_end": str,
                  "timesheet_count": int,
                  "total_hours": float,
                  "total_amount": float
                }

POST   /invoicing/supplier-remittance
       Generate supplier payment statement
       Params: supplier_org_id, period_start, period_end
       Returns: {
                  "supplier_org_id": int,
                  "period_start": str,
                  "period_end": str,
                  "total_timesheets": int,
                  "total_hours": float,
                  "total_amount": float,
                  "status": str
                }
```

---

## Role Requirements by Module

### Rate Cards
- client_admin, msp_admin, platform_admin

### Compliance
- POST requirements: msp_admin, platform_admin
- GET requirements: msp_admin, platform_admin
- POST/PUT/GET records: msp_admin, client_admin, platform_admin

### SLA
- All endpoints: msp_admin, platform_admin

### VMS Timesheets
- POST (submit): supplier_admin, supplier_recruiter, contractor
- GET/PUT (review/approve): supplier_admin, msp_admin, client_admin, platform_admin

### Auto Invoicing
- All endpoints: msp_admin, client_admin, platform_admin

---

## Status Codes

### Success
- `201 Created` - Resource created (POST endpoints)
- `200 OK` - Request successful (GET, PUT endpoints)
- `204 No Content` - Resource deleted (DELETE endpoints)

### Client Errors
- `400 Bad Request` - Invalid input/validation failure
- `404 Not Found` - Resource not found
- `403 Forbidden` - Insufficient permissions

### Server Errors
- `500 Internal Server Error` - Unexpected error

---

## Common Query Parameters

### Pagination
- `skip: int (default: 0)` - Offset
- `limit: int (default: 20)` - Page size

### Filtering
- `status: str?` - Filter by status
- `org_id: int?` - Filter by organization
- `org_type: str?` - Filter by org type (supplier/client/msp)
- `period: str?` - Filter by period
- `severity: str?` - Filter by severity (SLA)
- `metric_type: str?` - Filter by metric type (SLA)
- `is_resolved: bool?` - Filter by resolution status (SLA)

### Time-based
- `days: int (default: 30)` - Lookahead window for expiring items
- `period_start: date` - Period start date
- `period_end: date` - Period end date

---

## Common Request Body Fields

### Rate Card
```json
{
  "client_org_id": 123,
  "job_category": "Software Engineer",
  "location": "San Francisco, CA",
  "bill_rate_min": 75.0,
  "bill_rate_max": 150.0,
  "pay_rate_min": 50.0,
  "pay_rate_max": 100.0,
  "overtime_multiplier": 1.5,
  "effective_from": "2026-01-01",
  "effective_to": "2026-12-31",
  "entries": [
    {
      "skill_name": "Python",
      "skill_level": "Senior",
      "bill_rate": 120.0,
      "pay_rate": 85.0
    }
  ]
}
```

### Compliance Record
```json
{
  "placement_id": 456,
  "candidate_id": 789,
  "compliance_requirement_id": 101,
  "required_by": "2026-04-01",
  "provider_name": "ADP",
  "provider_reference_id": "REF-123"
}
```

### Timesheet
```json
{
  "placement_id": 456,
  "contractor_id": 789,
  "customer_id": 123,
  "period_start": "2026-03-01",
  "period_end": "2026-03-07",
  "regular_rate": 50.0
}
```

---

## Response Examples

### RateCardResponse
```json
{
  "id": 1,
  "client_org_id": 123,
  "job_category": "Software Engineer",
  "location": "San Francisco, CA",
  "bill_rate_min": 75.0,
  "bill_rate_max": 150.0,
  "pay_rate_min": 50.0,
  "pay_rate_max": 100.0,
  "status": "ACTIVE",
  "entries": [
    {
      "id": 101,
      "skill_name": "Python",
      "skill_level": "Senior",
      "bill_rate": 120.0,
      "pay_rate": 85.0
    }
  ],
  "created_at": "2026-03-08T12:00:00",
  "updated_at": "2026-03-08T12:00:00"
}
```

### RateValidationResponse
```json
{
  "is_valid": true,
  "rate_card_id": 1,
  "violations": [],
  "message": "Rates are valid"
}
```

### ComplianceScoreResponse
```json
{
  "supplier_org_id": 456,
  "overall_score": 95.5,
  "completed_requirements": 18,
  "total_requirements": 20,
  "expired_requirements": 1,
  "failed_requirements": 1
}
```

### SLADashboardResponse
```json
{
  "total_configs": 5,
  "active_breaches": 2,
  "resolved_breaches": 8,
  "critical_breaches": 1,
  "total_penalties": 1500.0,
  "breaches_by_metric": {
    "RESPONSE_TIME": 3,
    "QUALITY": 2
  },
  "breaches_by_severity": {
    "CRITICAL": 1,
    "MEDIUM": 4
  }
}
```

### TimesheetResponse
```json
{
  "id": 789,
  "placement_id": 456,
  "contractor_id": 999,
  "period_start": "2026-03-01",
  "period_end": "2026-03-07",
  "total_regular_hours": 40.0,
  "total_overtime_hours": 5.0,
  "total_hours": 45.0,
  "bill_rate": 100.0,
  "regular_rate": 75.0,
  "regular_amount": 3000.0,
  "overtime_amount": 562.5,
  "total_bill_amount": 4500.0,
  "status": "SUBMITTED",
  "created_at": "2026-03-08T10:00:00",
  "updated_at": "2026-03-08T10:00:00"
}
```

---

## Integration Points

### With Services
- RateCardService: validation, listing, retrieval
- ComplianceService: tracking, scoring, expiry monitoring
- SLAService: configuration, breach detection, resolution
- VMSTimesheetService: creation, approval workflow, compliance checks
- AutoInvoiceService: generation, preview, remittance

### With Models
- RateCard, RateCardEntry
- ComplianceRequirement, ComplianceRecord, ComplianceScore
- SLAConfiguration, SLABreachRecord
- Timesheet, TimesheetEntry
- Invoice, InvoiceLineItem, PlacementRecord

### With Authentication
- JWT token validation via `require_role()` dependency
- User context extracted from token claims
- Role-based access control enforcement

### With Database
- AsyncSession for all database operations
- Async/await pattern throughout
- Proper transaction management

---

## Testing Examples

### Create Rate Card
```bash
curl -X POST http://localhost:8000/api/v1/rate-cards \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "client_org_id": 123,
    "job_category": "Senior Engineer",
    "bill_rate_min": 100,
    "bill_rate_max": 200,
    "pay_rate_min": 70,
    "pay_rate_max": 150,
    "effective_from": "2026-01-01"
  }'
```

### Validate Rates
```bash
curl -X POST http://localhost:8000/api/v1/rate-cards/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "client_org_id": 123,
    "job_category": "Senior Engineer",
    "bill_rate": 150,
    "pay_rate": 100
  }'
```

### List SLA Breaches
```bash
curl "http://localhost:8000/api/v1/sla/breaches?org_id=123&severity=CRITICAL" \
  -H "Authorization: Bearer <token>"
```

### Generate Invoice Preview
```bash
curl "http://localhost:8000/api/v1/invoicing/preview?client_org_id=123&period_start=2026-03-01&period_end=2026-03-31" \
  -X POST \
  -H "Authorization: Bearer <token>"
```

---

**Created:** March 8, 2026
**Total Endpoints:** 27
**Documentation Status:** Complete
