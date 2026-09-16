from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/export/branch/', views.dashboard_export_branch, name='dashboard-export-branch'),
    path('dashboard/export/pending/', views.dashboard_export_pending, name='dashboard-export-pending'),
    path('dashboard/export/recent/', views.dashboard_export_recent, name='dashboard-export-recent'),
    path('students/', views.student_list, name='student-list'),
    path('students/upload/', views.student_upload, name='student-upload'),
    path('students/upload/sample/', views.sample_format, name='sample-format'),
    path('students/demand/', views.demand_list, name='demand-list'),
    path('students/demand/upload/', views.demand_upload, name='demand-upload'),
    path('students/demand/upload/sample/', views.demand_sample_format, name='demand-sample-format'),
    path('students/<str:roll_no>/', views.student_detail, name='student-detail'),

    path('students/<str:roll_no>/certificate/', views.certificate_view, name='certificate-view'),
    path('students/<str:roll_no>/certificate/edit/', views.certificate_edit, name='certificate-edit'),
    path('students/<str:roll_no>/send-for-approval/', views.send_for_approval, name='send-for-approval'),

    path('approvals/<str:dept_slug>/', views.approval_queue, name='approval-queue'),
    path('approvals/<str:dept_slug>/<int:approval_id>/decide/', views.approval_decide, name='approval-decide'),
]
