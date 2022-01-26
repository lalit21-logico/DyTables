

from django.contrib import admin
from django.urls import path, include
import TMS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('TMS.urls')),
]

#handler404 = TMS.views.handler404
#handler500 = TMS.views.handler500
