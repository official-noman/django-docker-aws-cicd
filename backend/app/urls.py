from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Health Check View
def health_check(request):
    return JsonResponse({"status": "ok", "service": "inventory-api"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check), # DevOps Endpoint
    path('api/', include('inventory.urls'))
]