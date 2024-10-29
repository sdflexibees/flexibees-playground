"""flexibees_candidate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from core.proxy_redirect import proxy_function
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

mobile_schema_view = get_schema_view(
    openapi.Info(
        title="Candidate API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/candidate/', include('apps.candidate.urls'))],
    url='http://127.0.0.1:8000/'
    # url='https://candidate.flexibees.com/'
)

web_schema_view = get_schema_view(
    openapi.Info(
        title="Admin API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/admin/', include('apps.admin_app.urls'))],
    url='http://127.0.0.1:8000/'
    # url='https://candidate.flexibees.com/'
)

web_schema_view1 = get_schema_view(
    openapi.Info(
        title="Website API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/website/', include('apps.candidate.website_urls'))],
    url='http://127.0.0.1:8000/'
    # url='https://candidate.flexibees.com/'
)

web_schema_view2 = get_schema_view(
    openapi.Info(
        title="Finance API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('api/finance/', include('apps.finance.urls'))],
    url='http://127.0.0.1:8000/'
    # url='https://candidate.flexibees.com/'
)

from apps.admin_app.views import TimeoutAPI
urlpatterns = [
    path('timeout/<int:time>/', TimeoutAPI.as_view({'get': 'timeout'})),
    path('', web_schema_view.with_ui('swagger', cache_timeout=0), name='admin-swagger-ui'),
    path('candidate-docs/', mobile_schema_view.with_ui('swagger', cache_timeout=0), name='candidate-swagger-ui'),
    path('website-docs/', web_schema_view1.with_ui('swagger', cache_timeout=0), name='website-swagger-ui'),
    path('finance-docs/', web_schema_view2.with_ui('swagger', cache_timeout=0), name='finance-swagger-ui'),
    path('admin/', admin.site.urls),
    path('api/admin/', include('apps.admin_app.urls')),
    path('api/candidate/', include('apps.candidate.urls')),
    path('api/website/', include('apps.candidate.website_urls')),
    path('api/availability/', include('apps.availability.urls')),
    # path('api/employer/', include('apps.employer.urls')),
    # Proxy all employer-related URLs to the external server
    re_path(r'^api/employer/.*$', proxy_function, name='employer-proxy'),
    path('api/common/', include('apps.common.urls')),
    path('api/finance/', include('apps.finance.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
            static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
