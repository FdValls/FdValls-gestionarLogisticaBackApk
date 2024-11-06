from django.urls import path
from .views import CheckIdExistsAPIView, OrderCreateAPIView
from .views import ProcesarBase64APIView
from .views import ProcesarTelefonoAPIView

urlpatterns = [
    path('create_order/', OrderCreateAPIView.as_view(), name='create_order'),
    path('procesar_base64/', ProcesarBase64APIView.as_view(), name='procesar_base64'),
    path('process-phone-number/', ProcesarTelefonoAPIView.as_view(), name='process_phone_number'),
    path('check-id/', CheckIdExistsAPIView.as_view(), name='check_id'),
]