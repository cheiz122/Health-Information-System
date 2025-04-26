from django.contrib import admin
from health_app.views import CustomLoginView
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('', include('health_app.urls')),
]
