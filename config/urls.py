from django.contrib import admin
from django.urls import path, include
from gate import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # =========================
    # Admin
    # =========================
    path("admin/", admin.site.urls),

    # =========================
    # Home
    # =========================
    path("", views.home, name="home"),

    # =========================
    # Post Login Redirect
    # =========================
    path("post-login/", views.post_login_redirect, name="post_login_redirect"),

    # =========================
    # Student
    # =========================
    path("student/profile/", views.student_profile, name="student_profile"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    
    path("student/apply-outpass/", views.apply_outpass, name="apply_outpass"),

    # =========================
    # Gate Operations
    # =========================
    path("gate/check/", views.check, name="check"),
    path("gate/toggle/", views.toggle_status, name="gate_toggle"),
    path("logs/", views.home, name="logs"),

    # =========================
    # Approval System
    # =========================
    path("approval/", views.approval_dashboard, name="approval_dashboard"),
    path("approval/<int:request_id>/approve/", views.approve_leave, name="approve_leave"),
    path("approval/<int:request_id>/reject/", views.reject_leave, name="reject_leave"),

    # =========================
    # Student Management
    # =========================
    path("students/add/", views.add_student, name="add_student"),
    path("students/import/", views.import_students_csv, name="import_students_csv"),

    # =========================
    # Lists
    # =========================
    path("inside/", views.inside_list, name="inside"),
    path("outside/", views.outside_list, name="outside"),

    # =========================
    # API (Mobile / Future)
    # =========================
    path("api/v1/check/", views.api_check, name="api_check"),

    # =========================
    # Authentication
    # =========================
    path("accounts/", include("django.contrib.auth.urls")),
]


# =========================
# Development Media Serving
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
