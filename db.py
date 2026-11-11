"""Read-only monitoring helpers. No OTP, password, session, or account data is stored."""
import os
import logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger('autologger.db')
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    url, key = os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')
    if not url or not key:
        return None
    try:
        from supabase import create_client
        _client = create_client(url, key)
        return _client
    except Exception:
        log.exception('Could not initialize database client')
        return None


def check_database():
    client = _get_client()
    if client is None:
        # Database is optional; health is degraded only when credentials were configured
        return not (os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_KEY'))
    try:
        # A minimal read-only query verifies connectivity without exposing records.
        client.table('inventory').select('id').limit(1).execute()
        return True
    except Exception:
        log.exception('Database health check failed')
        return False


def get_monitoring_stats():
    client = _get_client()
    stats = {'database': 'not_configured' if client is None else 'unknown',
             'inventory_total': None, 'inventory_available': None,
             'inventory_unavailable': None,
             'note': 'Configure a read-only inventory table with id and status columns to show counts.'}
    if client is None:
        return stats
    try:
        # Only aggregate counts are returned. No phone numbers or other item values are read.
        rows = client.table('inventory').select('id,status').limit(5000).execute().data or []
        stats['database'] = 'ok'
        stats['inventory_total'] = len(rows)
        stats['inventory_available'] = sum(1 for row in rows if str(row.get('status', '')).lower() == 'available')
        stats['inventory_unavailable'] = sum(1 for row in rows if str(row.get('status', '')).lower() in ('unavailable', 'out_of_stock'))
        stats['note'] = 'Aggregate counts only; item identifiers and personal data are not displayed.'
    except Exception:
        stats['database'] = 'error'
        log.exception('Inventory aggregate query failed')
    return stats
