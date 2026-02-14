#!/bin/bash
set -e

echo "============================================"
echo "  HotGigs 2026 - Starting Application"
echo "============================================"
echo "  Database: ${DATABASE_URL:-not set}"
echo "  Redis:    ${REDIS_URL:-not set}"
echo "  RabbitMQ: ${RABBITMQ_URL:-not set}"
echo "============================================"

# Wait for database to be ready
echo "Waiting for database..."
for i in $(seq 1 30); do
    if python -c "
import sys
try:
    import psycopg2
    conn = psycopg2.connect('${DATABASE_SYNC_URL}')
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
        echo "Database is ready!"
        break
    fi
    echo "  Attempt $i/30 - waiting..."
    sleep 2
done

# Run database migrations if alembic.ini exists
if [ -f "alembic.ini" ]; then
    echo "Running database migrations..."
    alembic upgrade head 2>/dev/null || echo "Migrations skipped (no migration files or already up to date)"
fi

# Create tables via SQLAlchemy if needed
echo "Ensuring database tables exist..."
python -c "
import asyncio, os, sys
sys.path.insert(0, '/app')
os.environ.setdefault('PYTHONPATH', '/app')

async def create_tables():
    try:
        from database.connection import engine, init_db
        from database.base import Base
        # Import all models to register them
        import models.user, models.candidate, models.requirement
        import models.submission, models.interview, models.offer
        import models.supplier, models.contract, models.referral
        import models.customer, models.security, models.client
        import models.copilot, models.conversation, models.alerts
        import models.interview_intelligence
        import models.messaging, models.payment
        import models.timesheet, models.invoice

        await init_db()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('Database tables created/verified successfully')
    except Exception as e:
        print(f'Table creation warning: {e}')

asyncio.run(create_tables())
" 2>/dev/null || echo "Table auto-creation deferred to app startup"

# Seed initial admin user if needed
if [ "${SEED_DATA:-false}" = "true" ]; then
    echo "Seeding initial data..."
    python seed_test_data.py 2>/dev/null || echo "Seeding skipped"
fi

echo "Starting application server..."
exec "$@"
