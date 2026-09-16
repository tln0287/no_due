from django.contrib import admin

from .models import Clearance, Demand, DueApproval, Transaction

admin.site.site_header = 'No Due Tc Management'
admin.site.site_title = 'No Due Tc Management'
admin.site.index_title = 'No Due Tc Management'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'roll_no', 'course', 'branch', 'section', 'year', 'academic_year', 'total', 'order_status', 'transaction_date')
    list_filter = ('course', 'branch', 'year', 'academic_year', 'order_status', 'admission_type')
    search_fields = ('order_id', 'name', 'roll_no', 'id_no', 'mobile_number', 'email')


@admin.register(Demand)
class DemandAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'name', 'course', 'branch', 'section', 'year', 'academic_year', 'installment', 'total', 'updated_at')
    list_filter = ('installment', 'course', 'branch', 'year', 'academic_year', 'admission_type')
    search_fields = ('roll_no', 'name', 'id_no', 'mobile_number', 'email')


class DueApprovalInline(admin.TabularInline):
    model = DueApproval
    extra = 0
    fields = ('department', 'status', 'amount_due', 'remarks', 'decided_by', 'decided_at')
    readonly_fields = ('requested_at',)


@admin.register(Clearance)
class ClearanceAdmin(admin.ModelAdmin):
    list_display = ('roll_no', 'approval_status', 'other_fee_cleared', 'updated_at')
    search_fields = ('roll_no',)
    inlines = [DueApprovalInline]


@admin.register(DueApproval)
class DueApprovalAdmin(admin.ModelAdmin):
    list_display = ('clearance', 'department', 'status', 'amount_due', 'decided_by', 'decided_at', 'requested_at')
    list_filter = ('department', 'status')
    search_fields = ('clearance__roll_no',)
