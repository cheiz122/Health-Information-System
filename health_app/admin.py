from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Patient, Program, Enrollment, Diagnosis, DoctorProfile

# ────────────────────────────────────────────────────────────────────────────────
# First UNREGISTER the existing User model
# ────────────────────────────────────────────────────────────────────────────────
admin.site.unregister(get_user_model())

# Then REGISTER it again
admin.site.register(get_user_model(), UserAdmin)

# ────────────────────────────────────────────────────────────────────────────────
# Register other models
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'program')
    search_fields = ('user__username', 'program__name')

admin.site.register(Patient)
admin.site.register(Program)
admin.site.register(Enrollment)
admin.site.register(Diagnosis)
