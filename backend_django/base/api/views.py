from rest_framework import generics

from rest_framework.permissions import AllowAny
from .permissions import HasValidAPIToken

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from base.models import Order
from base.models import IdTemporal
from .serializers import CheckIdSerializer, OrderSerializer
from .serializers import ProcesarBase64Serializer
from .serializers import ProcesarTelefonoSerializer


class ProcesarBase64APIView(APIView):

    permission_classes = [HasValidAPIToken]

    def post(self, request):
        serializer = ProcesarBase64Serializer(data=request.data)
        
        if serializer.is_valid():
            result = serializer.save()
            
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProcesarTelefonoAPIView(APIView):

    permission_classes = [HasValidAPIToken]

    def post(self, request):
        serializer = ProcesarTelefonoSerializer(data=request.data)
        serializer2 = CheckIdSerializer(data=request.data)

        if serializer2.is_valid():
            order_id = serializer2.validated_data['order_id']
            if not IdTemporal.objects.filter(numero_id=order_id).exists() or not Order.objects.filter(order_id=order_id).exists():
                return Response({"error": "El ID temporal no existe o ya ha sido utilizado."}, status=status.HTTP_400_BAD_REQUEST)
            
        if serializer.is_valid():
            result = serializer.save()
            
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    permission_classes = [HasValidAPIToken]

    def create(self, request, *args, **kwargs):
        # SE OBTIENE EL ID "TEMPORAL" DEL REQUEST
        order_id = request.data.get('order_id')

        # SE VALIDA SI EL ID "TEMPORAL" EXISTE
        if not IdTemporal.objects.filter(numero_id=order_id).exists():
            return Response({"error": "El ID temporal no existe o ya ha sido utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)
    
class CheckIdExistsAPIView(APIView):
    permission_classes = [HasValidAPIToken]

    def post(self, request):
        serializer = CheckIdSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            
            # Verificar en la tabla Order
            order_exists = Order.objects.filter(order_id=order_id).exists()
            
            # Verificar en la tabla IdTemporal
            temporal_exists = IdTemporal.objects.filter(numero_id=order_id).exists()
            
            return Response({
                'exists': order_exists or temporal_exists,
                'status': {
                    'in_orders': order_exists,
                    'in_temporal': temporal_exists
                }
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)