"""
Helper functions for the Biometric app.
"""

from django.conf import settings

from Organization.views import _get_offices_queryset

from Biometric.models import BiometricDevice


def device_payload(device):
    """Build API payload for a BiometricDevice."""
    return {
        "id": device.id,
        "office_id": device.office_id,
        "office_name": device.office.name if hasattr(device, "office") and device.office else None,
        "device_id": device.device_id,
        "name": device.name or "",
        "is_active": device.is_active,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }


def get_devices_queryset(user):
    """Biometric devices in offices the user can access."""
    offices = _get_offices_queryset(user)
    return BiometricDevice.objects.filter(office__in=offices).select_related("office")


def get_essl_conn_params():
    """Connection params for ESSL DB from settings."""
    db = settings.DATABASES.get("essl_db", {})
    return {
        "host": db.get("HOST", "localhost"),
        "port": int(db.get("PORT", 3306)),
        "user": db.get("USER", ""),
        "password": db.get("PASSWORD", ""),
        "database": db.get("NAME", ""),
        "charset": "utf8mb4",
    }


def format_time_for_essl(val):
    """Format a time value for ESSL log response (HH:MM:SS or None)."""
    if val is None:
        return None
    if hasattr(val, "strftime"):
        return val.strftime("%H:%M:%S")
    return str(val)
