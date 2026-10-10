import sqlite3
from src.retrieval.db.connection import get_connection

STATUS_MAP = {
    "UPC": "Upcoming",
    "ONG": "Ongoing",
    "CMP": "Completed",
    "CNL_U": "Cancelled by customer",
    "CNL_S": "Cancelled by RideWise",
    "NSH": "No-show"
}

def _mask_dl(dl):
    if not dl: return dl
    return "*" * max(0, len(dl) - 4) + dl[-4:]

def _map_status(status):
    return STATUS_MAP.get(status, status)

def _is_owner(cur, booking_id, customer_id):
    if not customer_id: return True
    cur.execute("SELECT 1 FROM bookings WHERE booking_id = ? AND customer_id = ?", (booking_id, customer_id))
    return cur.fetchone() is not None

def get_profile(customer_id):
    if not customer_id: return None
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE customer_id = ? LIMIT 50", (customer_id,))
        row = cur.fetchone()
        if not row:
            return None
        prof = dict(row)
        prof['driving_license_no'] = _mask_dl(prof.get('driving_license_no'))
        return prof

def list_bookings(customer_id, status=None):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if customer_id:
            if status:
                cur.execute("SELECT * FROM bookings WHERE customer_id = ? AND booking_status = ? LIMIT 50", (customer_id, status))
            else:
                cur.execute("SELECT * FROM bookings WHERE customer_id = ? LIMIT 50", (customer_id,))
        else:
            if status:
                cur.execute("SELECT * FROM bookings WHERE booking_status = ? LIMIT 50", (status,))
            else:
                cur.execute("SELECT * FROM bookings LIMIT 50")
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r['booking_status'] = _map_status(r.get('booking_status'))
        return rows

def get_booking(customer_id, booking_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if customer_id:
            cur.execute("SELECT * FROM bookings WHERE booking_id = ? AND customer_id = ? LIMIT 50", (booking_id, customer_id))
        else:
            cur.execute("SELECT * FROM bookings WHERE booking_id = ? LIMIT 50", (booking_id,))
        row = cur.fetchone()
        if not row:
            return {"error": "not_found"}
        d = dict(row)
        d['booking_status'] = _map_status(d.get('booking_status'))
        return d

def get_booking_payments(customer_id, booking_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if not _is_owner(cur, booking_id, customer_id):
            return {"error": "not_found"}
        if customer_id:
            cur.execute("SELECT p.* FROM payments p JOIN bookings b ON p.booking_id = b.booking_id WHERE b.customer_id = ? AND p.booking_id = ? LIMIT 50", (customer_id, booking_id))
        else:
            cur.execute("SELECT * FROM payments WHERE booking_id = ? LIMIT 50", (booking_id,))
        return [dict(r) for r in cur.fetchall()]

def get_booking_damage_reports(customer_id, booking_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if not _is_owner(cur, booking_id, customer_id):
            return {"error": "not_found"}
        if customer_id:
            cur.execute("SELECT d.* FROM damage_reports d JOIN bookings b ON d.booking_id = b.booking_id WHERE b.customer_id = ? AND d.booking_id = ? LIMIT 50", (customer_id, booking_id))
        else:
            cur.execute("SELECT * FROM damage_reports WHERE booking_id = ? LIMIT 50", (booking_id,))
        return [dict(r) for r in cur.fetchall()]

def get_vehicle_for_booking(customer_id, booking_id):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if not _is_owner(cur, booking_id, customer_id):
            return {"error": "not_found"}
        if customer_id:
            cur.execute("SELECT v.* FROM vehicles v JOIN bookings b ON v.vehicle_id = b.vehicle_id WHERE b.customer_id = ? AND b.booking_id = ? LIMIT 50", (customer_id, booking_id))
        else:
            cur.execute("SELECT v.* FROM vehicles v JOIN bookings b ON v.vehicle_id = b.vehicle_id WHERE b.booking_id = ? LIMIT 50", (booking_id,))
        row = cur.fetchone()
        return dict(row) if row else {"error": "not_found"}
