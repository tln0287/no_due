from django.conf import settings
from django.db import models
from django.utils import timezone

from .departments import (
    DEPARTMENT_CODE_CHOICES,
    STATUS_CHOICES,
    STATUS_CLEARED,
    STATUS_DUES,
    STATUS_PENDING,
)


class Transaction(models.Model):
    """One fee-payment transaction imported from transactions.xlsx.

    The student table doesn't exist separately — a "student" is just the
    set of transactions sharing the same roll_no, so all filtering and
    reporting groups this table by roll_no.
    """

    order_id = models.CharField(max_length=40, unique=True)
    tracking = models.CharField(max_length=40, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    order_status = models.CharField(max_length=30, blank=True)
    status_message = models.CharField(max_length=255, blank=True)
    app_code = models.CharField(max_length=40, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    merchant_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, blank=True)

    billing_tel = models.CharField(max_length=20, blank=True)
    billing_email = models.CharField(max_length=255, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)

    id_no = models.CharField(max_length=40, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=255, blank=True)
    parent_mobile = models.CharField(max_length=20, blank=True)

    admission_type = models.CharField(max_length=30, blank=True)
    fee_type = models.CharField(max_length=60, blank=True)

    name = models.CharField(max_length=150, db_index=True)
    branch = models.CharField('Group / Branch', max_length=30, blank=True, db_index=True)
    course = models.CharField(max_length=30, blank=True, db_index=True)
    course_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    section = models.CharField(max_length=10, blank=True)
    year = models.CharField(max_length=10, blank=True, db_index=True)
    roll_no = models.CharField(max_length=40, db_index=True)
    academic_year = models.CharField(max_length=20, blank=True, db_index=True)

    issue_date = models.DateField(null=True, blank=True)
    due_date_installment1 = models.DateField(null=True, blank=True)

    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.CharField(max_length=255, blank=True)

    # Everything else from the "current dues" and "PAST DUES - ..." fee
    # columns, keyed by their original Excel header, kept verbatim so no
    # figure is lost even though most reports only need `total`.
    current_fees = models.JSONField(default=dict, blank=True)
    past_dues = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f'{self.order_id} · {self.name} ({self.roll_no})'


class Demand(models.Model):
    """One fee-demand row imported from upload.xlsx — how much a student
    owes for a given installment, as opposed to Transaction (what they've
    actually paid). upload.xlsx has one sheet per installment batch (e.g.
    "2ND YEAR 1st Install"); `installment` records which sheet a row came
    from, and together with roll_no is what re-uploads are matched on.
    """

    id_no = models.CharField('ID No.', max_length=40, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=255, blank=True)
    parent_mobile = models.CharField(max_length=20, blank=True)

    admission_type = models.CharField(max_length=30, blank=True)
    fee_type = models.CharField(max_length=60, blank=True)

    name = models.CharField(max_length=150, db_index=True)
    branch = models.CharField('Group / Branch', max_length=30, blank=True, db_index=True)
    course = models.CharField(max_length=30, blank=True, db_index=True)
    course_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    section = models.CharField(max_length=10, blank=True)
    year = models.CharField(max_length=10, blank=True, db_index=True)
    roll_no = models.CharField(max_length=40, db_index=True)
    academic_year = models.CharField(max_length=20, blank=True, db_index=True)

    issue_date = models.DateField(null=True, blank=True)
    due_date_installment1 = models.DateField(null=True, blank=True)

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.CharField(max_length=255, blank=True)
    rtf = models.DecimalField('RTF', max_digits=12, decimal_places=2, null=True, blank=True)

    # The 9 current-fee and 9 "PAST DUES - …" columns, keyed by their
    # original Excel header — same pattern as Transaction.current_fees.
    current_fees = models.JSONField(default=dict, blank=True)
    past_dues = models.JSONField(default=dict, blank=True)

    # Which upload.xlsx sheet this row came from, e.g. "2ND YEAR 1st Install".
    installment = models.CharField(max_length=100, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['roll_no', 'installment'], name='unique_demand_per_installment'),
        ]

    def __str__(self):
        return f'{self.installment} demand for {self.name} ({self.roll_no})'


class Clearance(models.Model):
    """Manually-maintained data needed for the TC / No-Dues certificate
    that has no source in the fee transactions sheet (personal details,
    non-tuition dues clearance, sign-off names)."""

    BRANCH_LEVEL_CHOICES = [
        ('JUNIOR', 'Junior'),
        ('DIPLOMA', 'Diploma'),
        ('DEGREE', 'Degree'),
        ('BTECH', 'B.Tech'),
        ('PG', 'PG Course'),
    ]

    roll_no = models.CharField(max_length=40, unique=True, db_index=True)

    tc_ndc_no = models.CharField('T.C. / N.D.C. No.', max_length=40, blank=True)
    admission_no = models.CharField(max_length=40, blank=True)
    certificate_date = models.DateField(null=True, blank=True)

    # Editable overrides for values that would otherwise come straight from
    # Transaction — printing/editing these never touches the transaction
    # table, they just replace what's shown on the certificate. Left blank,
    # the certificate falls back to the transaction-derived value (see
    # views._effective_fields).
    student_name = models.CharField('Name of Student', max_length=150, blank=True)
    course_branch_name = models.CharField('Course / Branch Name', max_length=100, blank=True)
    roll_no_register = models.CharField('Roll No. / Register No.', max_length=40, blank=True)
    year_of_study = models.CharField('Year of Study / Semester', max_length=60, blank=True)
    section_display = models.CharField('Section', max_length=20, blank=True)

    father_name = models.CharField("Father's / Guardian's Name", max_length=150, blank=True)
    mother_name = models.CharField("Mother's Name", max_length=150, blank=True)
    nationality = models.CharField(max_length=60, blank=True)
    religion = models.CharField(max_length=60, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    branch_level = models.CharField(max_length=10, choices=BRANCH_LEVEL_CHOICES, blank=True)
    date_of_last_exam = models.DateField(null=True, blank=True)
    year_of_passing = models.CharField(max_length=20, blank=True)

    # Library / Laboratory / Sports clearance is no longer entered here —
    # it's decided independently by each department's admins on their own
    # approval queue (see DueApproval below) once the office sends the
    # request with send_for_approval().
    other_fee_desc = models.CharField('Other Fee (specify)', max_length=100, blank=True)
    other_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    other_fee_cleared = models.BooleanField(default=False)
    other_fee_remarks = models.CharField(max_length=150, blank=True)

    prepared_by = models.CharField(max_length=100, blank=True)
    verified_by = models.CharField(max_length=100, blank=True)
    hod_name = models.CharField('HOD', max_length=100, blank=True)
    os_name = models.CharField('O/S (Office Superintendent)', max_length=100, blank=True)
    accounts_officer_name = models.CharField(max_length=100, blank=True)
    principal_name = models.CharField(max_length=100, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Clearance / certificate detail'
        verbose_name_plural = 'Clearance / certificate details'

    def ordered_approvals(self):
        """The three department approvals in a fixed display order, each
        paired with its (possibly missing, if never sent) DueApproval row."""
        by_code = {a.department: a for a in self.approvals.all()}
        return [
            {'code': code, 'label': label, 'approval': by_code.get(code)}
            for code, label in DEPARTMENT_CODE_CHOICES
        ]

    def approval_status(self):
        """Overall parallel-approval workflow status:

        - NOT_SENT — send_for_approval() hasn't been run yet (or not for
          every department).
        - DUES — at least one department marked it Dues.
        - PENDING — sent, but at least one department hasn't decided yet.
        - CLEARED — all three departments marked it cleared.
        """
        statuses = {a.department: a.status for a in self.approvals.all()}
        if len(statuses) < len(DEPARTMENT_CODE_CHOICES):
            return 'NOT_SENT'
        if any(s == STATUS_DUES for s in statuses.values()):
            return STATUS_DUES
        if any(s == STATUS_PENDING for s in statuses.values()):
            return STATUS_PENDING
        return STATUS_CLEARED

    def all_other_dues_cleared(self):
        """True only once Library, Laboratory, and Sports have all
        cleared the student *and* there's no outstanding "Other Fee"
        amount. Other Fee has no department workflow — it's cleared
        manually by office staff, same as before.
        """
        if self.other_fee_amount and not self.other_fee_cleared:
            return False
        return self.approval_status() == STATUS_CLEARED

    def __str__(self):
        return f'Clearance for {self.roll_no}'


class DueApproval(models.Model):
    """One department's decision in the parallel No-Dues approval
    workflow for a single student.

    All three rows (Library, Laboratory, Sports) are created together —
    as PENDING — the moment office staff sends a student's certificate
    for approval, so every department is notified/queued at the same
    time rather than one after another. Each department's admins then
    decide their own row independently; the overall certificate status
    (see Clearance.approval_status) is derived by combining all three.
    """

    clearance = models.ForeignKey(Clearance, related_name='approvals', on_delete=models.CASCADE)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CODE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount_due = models.DecimalField('Amount Due (₹)', max_digits=12, decimal_places=2, null=True, blank=True)
    remarks = models.CharField(max_length=150, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name='due_decisions', on_delete=models.SET_NULL,
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['department']
        constraints = [
            models.UniqueConstraint(fields=['clearance', 'department'], name='unique_department_per_clearance'),
        ]

    def mark(self, status, user, remarks='', amount_due=None):
        self.status = status
        self.remarks = remarks
        # Only Dues carries a real outstanding amount — clearing wipes
        # any figure left over from a previous decision.
        self.amount_due = amount_due if status == STATUS_DUES else None
        self.decided_by = user
        self.decided_at = timezone.now()
        self.save(update_fields=['status', 'remarks', 'amount_due', 'decided_by', 'decided_at'])

    def __str__(self):
        return f'{self.get_department_display()} — {self.clearance.roll_no} ({self.get_status_display()})'


class FeePaidRow(models.Model):
    """One row of the No-Due Certificate's "Tuition Fee Paid" table.

    Seeded from Transaction history every time the No-Due Certificate is
    opened — but only *new* transactions (not seen before) get a row
    added; anything already seeded is fully editable/addable/removable
    on its own from then on and never written back to Transaction.
    """

    clearance = models.ForeignKey(Clearance, related_name='fee_rows', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    label = models.CharField('Semester / Payment', max_length=100, blank=True)
    amount_paid = models.DecimalField('Amount Paid (₹)', max_digits=12, decimal_places=2, null=True, blank=True)
    date_paid = models.DateField(null=True, blank=True)
    receipt_no = models.CharField('Challan No. / Receipt No.', max_length=60, blank=True)

    # Which Transaction.order_id this row was seeded from, if any — used
    # only to detect "already synced" on the next seed pass. Deliberately
    # separate from receipt_no (which staff can freely retype on the
    # printed certificate) so editing that field can never cause the same
    # transaction to be re-added as a duplicate row.
    source_order_id = models.CharField(max_length=40, blank=True, editable=False, db_index=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.label} — {self.amount_paid}'
