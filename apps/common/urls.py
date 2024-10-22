from django.urls import path
from apps.common.views import AssetUpload


urlpatterns = [
    # media upload 
    path("asset-upload",AssetUpload.as_view({'post': 'post'}))
]
