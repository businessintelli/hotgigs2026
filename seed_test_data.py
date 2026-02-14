"""Seed test data into the running platform."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./hr_platform_test.db"

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DB_URL = "sqlite+aiosqlite:///./hr_platform_test.db"

async def seed():
    engine = create_async_engine(DB_URL, connect_args={"check_same_thread": False})
    S = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    now = datetime.utcnow()
    avail = now + timedelta(days=14)

    async with S() as session:
        # Users
        await session.execute(text(
            "INSERT OR IGNORE INTO users (id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, 1, :now, :now)"
        ), {"id": 1, "email": "admin@hrplatform.com", "fn": "Platform", "ln": "Admin", "pw": pwd.hash("admin123"), "role": "ADMIN", "now": now})

        await session.execute(text(
            "INSERT OR IGNORE INTO users (id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at) "
            "VALUES (:id, :email, :fn, :ln, :pw, :role, 1, :now, :now)"
        ), {"id": 2, "email": "recruiter@hrplatform.com", "fn": "Jane", "ln": "Recruiter", "pw": pwd.hash("recruiter123"), "role": "RECRUITER", "now": now})

        # Customers
        for cid, name, industry in [(1, "TechCorp Solutions", "Technology"), (2, "FinanceHub Global", "Finance"), (3, "HealthFirst Inc", "Healthcare")]:
            await session.execute(text(
                "INSERT OR IGNORE INTO customers (id, name, industry, is_active, created_at, updated_at) "
                "VALUES (:id, :name, :ind, 1, :now, :now)"
            ), {"id": cid, "name": name, "ind": industry, "now": now})

        # Requirements
        reqs = [
            (1, "Senior Python Developer", "Experienced Python dev with FastAPI", 1, "high", '["Python","FastAPI","PostgreSQL"]', 5, 10, 80.0, 120.0),
            (2, "React Frontend Engineer", "Strong React/TypeScript developer", 2, "medium", '["React","TypeScript","Tailwind"]', 3, 7, 70.0, 100.0),
            (3, "DevOps Engineer", "Cloud infrastructure specialist", 1, "high", '["AWS","Kubernetes","Terraform"]', 4, 8, 90.0, 130.0),
            (4, "Data Scientist", "ML/AI for healthcare analytics", 3, "medium", '["Python","TensorFlow","NLP"]', 3, 6, 85.0, 125.0),
        ]
        for rid, title, desc, cust, pri, skills, emin, emax, rmin, rmax in reqs:
            await session.execute(text(
                "INSERT OR IGNORE INTO requirements (id, title, description, customer_id, priority, skills_required, "
                "experience_min, experience_max, rate_min, rate_max, status, is_active, created_at, updated_at) "
                "VALUES (:id, :title, :desc, :cust, :pri, :skills, :emin, :emax, :rmin, :rmax, 'active', 1, :now, :now)"
            ), {"id": rid, "title": title, "desc": desc, "cust": cust, "pri": pri, "skills": skills,
                "emin": emin, "emax": emax, "rmin": rmin, "rmax": rmax, "now": now})

        # Candidates
        cands = [
            (1, "John", "Smith", "john.smith@email.com", '["Python","FastAPI","PostgreSQL","Docker"]', 7, "Senior Developer", 95.0, "sourced"),
            (2, "Sarah", "Johnson", "sarah.j@email.com", '["React","TypeScript","Node.js","Tailwind"]', 5, "Frontend Lead", 85.0, "sourced"),
            (3, "Mike", "Chen", "mike.chen@email.com", '["AWS","Kubernetes","Terraform","Docker"]', 6, "DevOps Engineer", 110.0, "matched"),
            (4, "Emily", "Davis", "emily.d@email.com", '["Python","TensorFlow","SQL","NLP"]', 4, "Data Scientist", 100.0, "sourced"),
            (5, "Alex", "Wilson", "alex.w@email.com", '["Java","Spring Boot","AWS"]', 8, "Senior Backend Dev", 115.0, "sourced"),
        ]
        for cid, fn, ln, email, skills, exp, title, rate, status in cands:
            await session.execute(text(
                "INSERT OR IGNORE INTO candidates (id, first_name, last_name, email, skills, "
                "total_experience_years, current_title, desired_rate, status, is_active, created_at, updated_at) "
                "VALUES (:id, :fn, :ln, :email, :skills, :exp, :title, :rate, :status, 1, :now, :now)"
            ), {"id": cid, "fn": fn, "ln": ln, "email": email, "skills": skills,
                "exp": exp, "title": title, "rate": rate, "status": status, "now": now})

        # Suppliers
        for sid, name, email, tier in [(1, "TalentBridge Partners", "contact@talentbridge.com", "gold"),
                                        (2, "StaffingPro Global", "info@staffingpro.com", "silver")]:
            await session.execute(text(
                "INSERT OR IGNORE INTO suppliers (id, company_name, contact_email, tier, is_active, created_at, updated_at) "
                "VALUES (:id, :name, :email, :tier, 1, :now, :now)"
            ), {"id": sid, "name": name, "email": email, "tier": tier, "now": now})

        await session.commit()
        print("Seed data created successfully!")

        for table in ['users', 'customers', 'requirements', 'candidates', 'suppliers']:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            print(f"  {table}: {result.scalar()} records")

    await engine.dispose()

asyncio.run(seed())
