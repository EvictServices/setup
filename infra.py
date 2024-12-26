import asyncio
import asyncpg
import redis
import os
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def import_schema():
    """Import the database schema from dump file"""
    try:
        schema_file = Path('setup/schema.sql')
        if not schema_file.exists():
            raise FileNotFoundError("Schema file not found")
            
        subprocess.run([
            'psql',
            '-h', 'localhost',
            '-U', 'admin',
            '-d', 'postgres',
            '-f', str(schema_file)
        ], env={**os.environ, 'PGPASSWORD': os.getenv('POSTGRES_ADMIN_PASSWORD')}, check=True)
        
        logger.info("Successfully imported database schema")
        
    except Exception as e:
        logger.error(f"Failed to import schema: {str(e)}")
        raise

async def verify_services():
    """Verify all infrastructure services are running"""
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='admin',
            password=os.getenv('POSTGRES_ADMIN_PASSWORD'),
            database='postgres'
        )
        await conn.execute('SELECT 1')
        await conn.close()
        logger.info("PostgreSQL connection successful")
        
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        r.close()
        logger.info("Redis connection successful")
        
    except Exception as e:
        logger.error(f"Service verification failed: {str(e)}")
        raise

async def main():
    """Main initialization function"""
    try:
        logger.info("Starting infrastructure initialization...")
        
        await verify_services()
        
        await import_schema()
        
        logger.info("Infrastructure initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Infrastructure initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
