"""
Helper functions for the Attendance / Regularization module.
"""

from decimal import Decimal

from django.db.models import Q

from Organization.models import Office
from Users.models import User, UserRole

from Employee.utils import is_superadmin


# ── Permission helpers ──────────────────────────────────────────────


def can_regularize_employee(user, employee) -> bool:
    """True if *user* is allowed to create a regularization for *employee*. Manager: only their offices. Office Admin/Supervisor: only their office."""
    if is_superadmin(user):
        return True

    if user.organization_id != employee.organization_id:
        return False

    if user.role == UserRole.ORG_ADMIN:
        return True

    if user.role in (UserRole.OFFICE_ADMIN, UserRole.SUPERVISOR):
        return getattr(user, "office_id", None) == employee.office_id

    if user.role == UserRole.OFFICE_MANAGER:
        return Office.objects.filter(
            pk=employee.office_id, managers=user
        ).exists()

    return False


def is_auto_approved(user) -> bool:
    """Roles whose regularizations skip the approval queue."""
    if is_superadmin(user):
        return True
    return user.role in (
        UserRole.ORG_ADMIN,
        UserRole.OFFICE_ADMIN,
        UserRole.OFFICE_MANAGER,
    )


def can_review_regularization(user, regularization) -> bool:
    """True if *user* may approve/reject *regularization*. Manager: only their offices. Office Admin/Supervisor: only their office."""
    if is_superadmin(user):
        return True

    emp = regularization.employee
    if user.organization_id != emp.organization_id:
        return False

    if user.role == UserRole.ORG_ADMIN:
        return True

    if user.role in (UserRole.OFFICE_ADMIN, UserRole.SUPERVISOR):
        return getattr(user, "office_id", None) == emp.office_id

    if user.role == UserRole.OFFICE_MANAGER:
        return Office.objects.filter(
            pk=emp.office_id, managers=user
        ).exists()

    return False


# ── Approver discovery ──────────────────────────────────────────────


def get_approvers_for_employee(employee):
    """
    Return a queryset of Users who should receive a pending-regularization
    notification for *employee*: office managers of that office + office
    admins / org admins in the same organization.
    """
    office_manager_ids = Office.objects.filter(
        pk=employee.office_id,
    ).values_list("managers__id", flat=True)

    return User.objects.filter(
        Q(pk__in=office_manager_ids)
        | Q(role__in=[UserRole.ORG_ADMIN, UserRole.OFFICE_ADMIN]),
        is_active=True,
        organization_id=employee.organization_id,
    )


# ── Attendance mutation ─────────────────────────────────────────────


def apply_regularization(regularization):
    """Write the approved values back to the Attendance row."""
    att = regularization.attendance
    att.status = regularization.new_status

    if regularization.new_first_in is not None:
        att.first_in = regularization.new_first_in
    if regularization.new_last_out is not None:
        att.last_out = regularization.new_last_out

    if att.first_in and att.last_out:
        delta = att.last_out - att.first_in
        att.working_hours = Decimal(str(round(delta.total_seconds() / 3600, 2)))
    att.save()


# ── JSON payload builders ───────────────────────────────────────────


def regularization_payload(reg) -> dict:
    return {
        "id": reg.id,
        "attendance_id": reg.attendance_id,
        "employee_id": reg.employee_id,
        "employee_name": reg.employee.name if hasattr(reg, "employee") and reg.employee else None,
        "date": reg.date.isoformat(),
        "new_status": reg.new_status,
        "new_first_in": reg.new_first_in.isoformat() if reg.new_first_in else None,
        "new_last_out": reg.new_last_out.isoformat() if reg.new_last_out else None,
        "reason": reg.reason,
        "status": reg.status,
        "requested_by_id": reg.requested_by_id,
        "requested_by_name": reg.requested_by.name if hasattr(reg, "requested_by") and reg.requested_by else None,
        "reviewed_by_id": reg.reviewed_by_id,
        "reviewed_by_name": reg.reviewed_by.name if (reg.reviewed_by_id and hasattr(reg, "reviewed_by") and reg.reviewed_by) else None,
        "reviewed_at": reg.reviewed_at.isoformat() if reg.reviewed_at else None,
        "review_remarks": reg.review_remarks or "",
        "created_at": reg.created_at.isoformat() if reg.created_at else None,
        "updated_at": reg.updated_at.isoformat() if reg.updated_at else None,
    }
