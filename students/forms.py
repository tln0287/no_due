from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import inlineformset_factory

from .departments import STATUS_CLEARED, STATUS_DUES
from .models import Clearance, Demand, FeePaidRow, Transaction


class TransactionUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Transactions Excel file (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}),
    )

    def clean_excel_file(self):
        f = self.cleaned_data['excel_file']
        if not f.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Please upload an .xlsx file.')
        return f


class DemandUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Demand Excel file (.xlsx)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx'}),
    )

    def clean_excel_file(self):
        f = self.cleaned_data['excel_file']
        if not f.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Please upload an .xlsx file.')
        return f


class StudentFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Name / Roll No / ID No / Order / App Code', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search name, roll no, ID no, order, app code…'}))
    course = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    branch = forms.ChoiceField(required=False, label='Group / Branch', widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    academic_year = forms.ChoiceField(required=False, label='Academic Year', widget=forms.Select(attrs={'class': 'form-select'}))
    admission_type = forms.ChoiceField(required=False, label='Admission Type', widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, column in (
            ('course', 'course'), ('branch', 'branch'), ('section', 'section'),
            ('year', 'year'), ('academic_year', 'academic_year'), ('admission_type', 'admission_type'),
        ):
            values = (
                Transaction.objects.exclude(**{column: ''})
                .order_by(column).values_list(column, flat=True).distinct()
            )
            self.fields[field_name].choices = [('', 'All')] + [(v, v) for v in values]


class DemandFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Name / Roll No / ID No', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search name, roll no, ID no…'}))
    installment = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    course = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    branch = forms.ChoiceField(required=False, label='Group / Branch', widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    academic_year = forms.ChoiceField(required=False, label='Academic Year', widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(required=False, label='Payment Status', choices=[
        ('', 'All'), ('PAID', 'Paid'), ('UNPAID', 'Not Paid'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, column in (
            ('installment', 'installment'), ('course', 'course'), ('branch', 'branch'),
            ('section', 'section'), ('year', 'year'), ('academic_year', 'academic_year'),
        ):
            values = (
                Demand.objects.exclude(**{column: ''})
                .order_by(column).values_list(column, flat=True).distinct()
            )
            self.fields[field_name].choices = [('', 'All')] + [(v, v) for v in values]


class DashboardFilterForm(forms.Form):
    branch = forms.ChoiceField(required=False, label='Group / Branch', widget=forms.Select(attrs={'class': 'form-select'}))
    course = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    academic_year = forms.ChoiceField(required=False, label='Academic Year', widget=forms.Select(attrs={'class': 'form-select'}))
    installment = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, column in (('branch', 'branch'), ('course', 'course'), ('academic_year', 'academic_year')):
            values = (
                Demand.objects.exclude(**{column: ''})
                .order_by(column).values_list(column, flat=True).distinct()
            )
            self.fields[field_name].choices = [('', 'All')] + [(v, v) for v in values]
        installments = Demand.objects.order_by('installment').values_list('installment', flat=True).distinct()
        self.fields['installment'].choices = [('', 'All')] + [(v, v) for v in installments]


TEXT = forms.TextInput(attrs={'class': 'form-control'})
DATE = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
CHECK = forms.CheckboxInput(attrs={'class': 'form-check-input'})


class TCApplicationForm(forms.ModelForm):
    """Every field on the "Application of Transfer Certificate" section."""

    class Meta:
        model = Clearance
        fields = [
            'tc_ndc_no', 'admission_no', 'certificate_date',
            'student_name', 'father_name', 'mother_name', 'nationality', 'religion',
            'date_of_birth', 'branch_level', 'course_branch_name', 'roll_no_register',
            'year_of_study', 'date_of_last_exam', 'year_of_passing',
        ]
        widgets = {
            'tc_ndc_no': TEXT, 'admission_no': TEXT, 'certificate_date': DATE,
            'student_name': TEXT, 'father_name': TEXT, 'mother_name': TEXT,
            'nationality': TEXT, 'religion': TEXT, 'date_of_birth': DATE,
            'branch_level': forms.Select(attrs={'class': 'form-select'}),
            'course_branch_name': TEXT, 'roll_no_register': TEXT,
            'year_of_study': TEXT, 'date_of_last_exam': DATE, 'year_of_passing': TEXT,
        }

    def __init__(self, *args, defaults=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field, value in (defaults or {}).items():
            if field in self.fields and not self.initial.get(field):
                self.initial[field] = value


class NoDuesForm(forms.ModelForm):
    """Every field on the "No Due Certificate cum Study / Transfer Certificate"
    section that office staff still enter directly, apart from the
    fee-paid table (see FeeRowFormSet). Library / Laboratory / Sports
    clearance isn't here any more — those are decided independently by
    each department on its own approval queue (see DueApproval, and
    views.send_for_approval / approval_decide)."""

    class Meta:
        model = Clearance
        fields = [
            'section_display',
            'other_fee_desc', 'other_fee_amount', 'other_fee_cleared', 'other_fee_remarks',
            'prepared_by', 'verified_by', 'hod_name', 'os_name', 'accounts_officer_name', 'principal_name',
        ]
        widgets = {
            'section_display': TEXT,
            'other_fee_desc': TEXT, 'other_fee_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_fee_cleared': CHECK, 'other_fee_remarks': TEXT,
            'prepared_by': TEXT, 'verified_by': TEXT, 'hod_name': TEXT,
            'os_name': TEXT, 'accounts_officer_name': TEXT, 'principal_name': TEXT,
        }

    def __init__(self, *args, defaults=None, **kwargs):
        super().__init__(*args, **kwargs)
        for field, value in (defaults or {}).items():
            if field in self.fields and not self.initial.get(field):
                self.initial[field] = value


class StyledPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm with Bootstrap classes on its widgets, so it
    matches the rest of the app instead of Django's unstyled defaults."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ApprovalDecisionForm(forms.Form):
    """A single department admin's decision on one student's approval
    row — posted from that department's queue page."""

    status = forms.ChoiceField(
        choices=[(STATUS_CLEARED, 'No Due'), (STATUS_DUES, 'Dues')],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm status-select'}),
    )
    amount_due = forms.DecimalField(
        required=False, max_digits=12, decimal_places=2, min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm amount-input', 'placeholder': 'Amount (₹)', 'step': '0.01',
        }),
    )
    remarks = forms.CharField(
        required=False, max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Remarks (optional)'}),
    )

    def clean(self):
        cleaned = super().clean()
        # Amount only means anything alongside Dues — dropping it here
        # keeps a stale figure from lingering if a decision flips back
        # to No Due without the amount field being cleared by hand.
        if cleaned.get('status') != STATUS_DUES:
            cleaned['amount_due'] = None
        return cleaned


FeeRowFormSet = inlineformset_factory(
    Clearance, FeePaidRow,
    fields=['label', 'amount_paid', 'date_paid', 'receipt_no'],
    widgets={
        'label': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        'amount_paid': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
        'date_paid': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
        'receipt_no': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
    },
    extra=1, can_delete=True,
)
