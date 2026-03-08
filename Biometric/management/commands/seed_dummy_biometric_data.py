"""
Django management command to seed dummy biometric attendance data for employees.

Usage:
    python manage.py seed_dummy_biometric_data [--month N] [--year Y] [--clear]

Without --month/--year, uses the current month and year. Creates punch logs in
DummyEsslBiometricAttendanceData for your existing Employees (UserId = Employee.emp_code);
each employee gets multiple in/out logs per day.
"""

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from Biometric.models import DummyEsslBiometricAttendanceData
from Employee.models import Employee


def make_log_date(year: int, month: int, day: int, hour: int, minute: int, second: int) -> datetime:
    """Build a naive datetime, then make timezone-aware."""
    dt = datetime(year, month, day, hour, minute, second)
    return timezone.make_aware(dt) if timezone.is_naive(dt) else dt


class Command(BaseCommand):
    help = "Seed DummyEsslBiometricAttendanceData with dummy punch logs for employees (current month by default)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--month",
            type=int,
            default=None,
            help="Month (1-12). Default: current month",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Year. Default: current year",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing DummyEsslBiometricAttendanceData before seeding",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        month = options["month"] if options["month"] is not None else now.month
        year = options["year"] if options["year"] is not None else now.year
        clear = options["clear"]

        if clear:
            deleted, _ = DummyEsslBiometricAttendanceData.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing records"))

        employees = list(Employee.objects.filter(is_active=True).values_list("emp_code", flat=True))
        if not employees:
            self.stdout.write(self.style.WARNING("No active employees found. Create employees first."))
            return

        # Device IDs to use (from BiometricDevice or default)
        try:
            from Biometric.models import BiometricDevice
            device_ids = list(BiometricDevice.objects.filter(is_active=True).values_list("device_id", flat=True))
        except Exception:
            device_ids = []
        if not device_ids:
            device_ids = ["3", "9"]

        # Base DeviceLogId - start high to avoid collisions
        max_row = DummyEsslBiometricAttendanceData.objects.aggregate(
            mx=models.Max("DeviceLogId")
        )
        base_log_id = (max_row.get("mx") or 1298800) + 1

        # Days in month
        if month == 2:
            days_in_month = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
        else:
            days_in_month = 31 if month in (1, 3, 5, 7, 8, 10, 12) else 30

        # For current month, only generate up to today; otherwise full month
        if month == now.month and year == now.year:
            days_in_month = min(days_in_month, now.day)
        days = days_in_month

        records = []
        log_id = base_log_id

        for day in range(1, days + 1):
            for emp_code in employees:
                device_id = random.choice(device_ids)
                # 2-4 punches per employee per day: check-in, check-out, maybe lunch out/in
                num_punches = random.randint(2, 4)
                punch_times = []

                # Check-in: 8:00-10:00
                h1, m1 = 8 + random.randint(0, 2), random.randint(0, 59)
                punch_times.append((h1, m1, "in"))

                # Check-out: 17:00-19:00 (or lunch out/in if 4 punches)
                if num_punches >= 4:
                    h2, m2 = 12 + random.randint(0, 1), random.randint(0, 59)
                    punch_times.append((h2, m2, "out"))
                    h3, m3 = 13 + random.randint(0, 1), random.randint(0, 59)
                    punch_times.append((h3, m3, "in"))
                h_last, m_last = 17 + random.randint(0, 2), random.randint(0, 59)
                punch_times.append((h_last, m_last, "out"))

                for idx, (h, m, direction) in enumerate(punch_times[:num_punches]):
                    s = random.randint(0, 59)
                    log_dt = make_log_date(year, month, day, h, m, s)
                    download_dt = log_dt + timedelta(seconds=random.randint(0, 5))

                    records.append(
                        DummyEsslBiometricAttendanceData(
                            DeviceLogId=log_id,
                            DownloadDate=download_dt,
                            DeviceId=device_id,
                            UserId=str(emp_code),
                            LogDate=log_dt,
                            Direction=direction,
                            AttDirection="",
                            C1=direction,
                            C2="",
                            C3="",
                            C4="0",
                            C5="1",
                            C6="0",
                            C7="0",
                            WorkCode="0",
                            hrapp_syncstatus="",
                        )
                    )
                    log_id += 1

        DummyEsslBiometricAttendanceData.objects.bulk_create(records)
        self.stdout.write(self.style.SUCCESS(f"Created {len(records)} dummy biometric records for {len(employees)} employees, {days} days in {year}-{month:02d}"))
