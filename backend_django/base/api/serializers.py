from rest_framework import serializers
from base.models import Order
from base.models import IdTemporal
from PIL import Image as PilImage
import base64
import re
import pytesseract
from io import BytesIO

temp_data_list = []
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['phone_number', 'order_id'] 

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        order_id = validated_data.get('order_id')
        # Crear el registro final en la tabla Order
        order = Order.objects.create(
            phone_number=phone_number,
            order_id=order_id
        )
        # Eliminar el ID temporal de la tabla IdTemporal
        IdTemporal.objects.filter(numero_id=order_id).delete()
        return order

#METODO PARA PROCESAR IMAGEN DIVIDIENDO EN 3 PARTES
class BaseSerializer(serializers.Serializer):
    def process_image(self, imagen_base64):
        try:
            print("Iniciando el procesamiento de la imagen...")
            # Decodificar la imagen de base64
            image_data = base64.b64decode(imagen_base64)
            image = PilImage.open(BytesIO(image_data))
             # Divido la imagen en tres partes
            width, height = image.size
            # Dividimos la imagen en tres partes verticalmente
            third_height = height // 3
            partes = [
                image.crop((0, 0, width, third_height)),# Parte 1
                image.crop((0, third_height, width, 2 * third_height)),# Parte 2
                image.crop((0, 2 * third_height, width, height))# Parte 3
            ]
            # OCR en cada parte
            for i, parte in enumerate(partes):
                extracted_text = self.perform_ocr(parte)
                print(f"Texto extraído en la parte {i+1}: {extracted_text}")
                # Intento extraer el número de ID de esta parte
                id_number = self.extract_id_number(extracted_text)
                if id_number:
                    print(f"ID encontrado en la parte {i+1}: {id_number}")
                    # return id_number
                    if self.check_id_exists(id_number):
                        raise serializers.ValidationError({
                            "error": "El ID ya existe en la base de datos.",
                            "id": id_number,
                            "exists": True
                        })
                    return id_number

            # Si no se encuentra un ID en ninguna parte
            print("No se encontró un ID en ninguna parte de la imagen.")
            return None

        except serializers.ValidationError:
            raise  # Re-lanzar errores de validación
        except Exception as e:
            print(f"Excepción atrapada en process_image: {str(e)}")
            # raise serializers.ValidationError(f"Error al procesar la imagen: {str(e)}")
            raise serializers.ValidationError(f"Error al procesar la imagen completa: {str({e.args[0]['error']})}")
    def perform_ocr(self, image):
        try:
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise serializers.ValidationError(f"Error al realizar OCR: {str(e)}")
        
    def check_id_exists(self, id_number):
        """
        Verifica si el ID existe en cualquiera de las tablas
        """
        if Order.objects.filter(order_id=id_number).exists():
            return True
        if IdTemporal.objects.filter(numero_id=id_number).exists():
            return True
        return False

class CheckIdSerializer(serializers.Serializer):
    order_id = serializers.CharField()

    def validate_order_id(self, value):
        if not value:
            raise serializers.ValidationError("El ID es requerido")
        return value
    
#METODO PARA PROCESAR IMAGEN SIN DIVIDIR
class BaseSerializer2(serializers.Serializer):

    def extract_id_number(self, text):
        id_pattern = re.compile(r'\b\d{11,16}\b')
        match = id_pattern.search(text)
        return match.group() if match else None
    def check_id_exists(self, id_number):
        """
        Verifica si el ID existe en cualquiera de las tablas
        """
        if Order.objects.filter(order_id=id_number).exists():
            return True
        if IdTemporal.objects.filter(numero_id=id_number).exists():
            return True
        return False
    def process_image(self, imagen_base64):
        try:
            print("Iniciando el procesamiento de la imagen completa...")
            # Decodificar la imagen de base64
            image_data = base64.b64decode(imagen_base64)
            image = PilImage.open(BytesIO(image_data))
            extracted_text = self.perform_ocr(image)
            print(f"Texto extraído: {extracted_text}")
            # Intento extraer el número de ID de esta parte
            id_number = self.extract_id_number(extracted_text)
            if id_number:
                print(f"TELEFONO encontrado: {id_number}")
                if self.check_id_exists(id_number):
                    raise serializers.ValidationError({
                        "error": "El ID ya existe en la base de datos",
                        "id": id_number,
                        "exists": True
                    })
                return id_number

        except Exception as e:
            print(f"Excepción atrapada en save_full_image: {e.args[0]['error']}")
            raise serializers.ValidationError(f"Error al procesar la imagen completa: {str({e.args[0]['error']})}")
    def perform_ocr(self, image):
        try:
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise serializers.ValidationError(f"Error al realizar OCR: {str(e)}")

#METODO PARA PROCESAR ID (llama al metodo Base)
class ProcesarBase64Serializer(BaseSerializer):
    base64 = serializers.CharField(write_only=True)
    id_number = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # Procesar la imagen base64
        imagen_base64 = validated_data.get('base64')
        id_number = self.process_image(imagen_base64)
        if not id_number:
            return {"error": "No se pudo extraer un ID válido de la imagen."}

        # Agregar el ID a la lista si no existe
        if not any(item['id_number'] == id_number for item in temp_data_list):
            temp_data_list.append({'id_number': id_number, 'phone_number': None})
        print("Estado de temp_data_list:", temp_data_list)

        if not IdTemporal.objects.filter(numero_id=id_number).exists():
            IdTemporal.objects.create(numero_id=id_number)

        return {'id_number': id_number}#ENVIAR id mas mensaje

    def extract_id_number(self, text):
        id_pattern = re.compile(r'\b\d{11,16}\b')
        match = id_pattern.search(text)
        return match.group() if match else None

#METODO PARA PROCESAR TELEFONO
class ProcesarTelefonoSerializer(BaseSerializer2):
    base64 = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(read_only=True)

    def create(self, validated_data):
        # Procesar la imagen base64
        imagen_base64 = validated_data.get('base64')
        phone_number = self.process_image(imagen_base64)

        if not phone_number:
            return {"error": "No se pudo extraer un número de teléfono válido de la imagen."}
        #Verifico si el numero coincide con el ID
        for item in temp_data_list:
            if item['id_number'] == phone_number:
                return {"error": "El número extraído es un ID. Proporcione una imagen con un número de teléfono."}

        for item in temp_data_list:
            if item['phone_number'] is None:  # Si el ID aún no tiene teléfono asociado
                item['phone_number'] = phone_number  # Asignar el teléfono
                
                print(f"Teléfono asignado al ID: {item['id_number']}")
                print("Estado de temp_data_list:", temp_data_list)
                # Verificar si ambos datos estan completos (ID y teléfono)
                if item['id_number'] and item['phone_number']:
                # Guardar la orden en la base de datos
                    order_serializer = OrderSerializer(data={
                        'phone_number': item['phone_number'],
                        'order_id': item['id_number']
                    })
                if order_serializer.is_valid():
                    order_serializer.save()
                    print(f"Orden guardada: {item['id_number']} con teléfono: {item['phone_number']}")
                    temp_data_list.remove(item)  # Eliminar el item después de guardar
                    print("Estado de temp_data_list:", temp_data_list)
                    return {"message": "Orden Guardada correctamente", 'order_id': item['id_number'], 'phone_number': item['phone_number']}
                else:
                    return {"error": "Error al guardar la orden en la base de datos.", "details": order_serializer.errors}
        # Retornar el número de teléfono extraído
        return {"message": f"Número de teléfono encontrado: {phone_number}"}
    def extract_id_number(self, text):
    #7 digitos con espacios y guiones
        phone_pattern = re.compile(r'(?<!\d)(\d[\d\s-]{6,})(?=\b)')
        match = phone_pattern.search(text)
    #limpiar el resultado
        if match:
            #Elimino espacios y guiones
            cleaned_number = match.group().replace(" ", "").replace("-", "")
            #Solo digitos
            return ''.join(filter(str.isdigit, cleaned_number))
        return None
    
