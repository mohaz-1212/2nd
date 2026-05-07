"""
URL configuration for Store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Corner.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError

def create_admin():
    try:
        User = get_user_model()
        email = "admin@engineers.com"
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password="engineers2026"
            )
            print("=== Superuser created successfully ===")
    except (OperationalError, ProgrammingError):
        # هذا يمنع الكود من التعطل إذا كانت الجداول لم تُنشأ بعد
        pass
    except Exception as e:
        print(f"Error: {e}")

# استدعاء الدالة
create_admin()
