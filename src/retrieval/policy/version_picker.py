from datetime import datetime

def get_applicable_version(booking: dict = None) -> str:
    """
    Returns 'v1' for bookings made before 1 July 2026, 
    'v2' for bookings made on or after 1 July 2026,
    or 'unknown' if it cannot be determined.
    """
    if not booking or not booking.get('booked_at'):
        return 'unknown'
        
    try:
        booked_at_str = booking['booked_at']
        booked_at = datetime.strptime(booked_at_str, '%Y-%m-%d %H:%M:%S')
        cutoff = datetime(2026, 7, 1, 0, 0, 0)
        
        if booked_at < cutoff:
            return 'v1'
        else:
            return 'v2'
    except Exception:
        return 'unknown'
