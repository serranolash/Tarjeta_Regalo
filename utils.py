import datetime
import barcode
from barcode.writer import ImageWriter
import os
from io import BytesIO
from django.core.files.images import ImageFile
from .models import Tipo, Voucher, Etiqueta
from barcode import Code128
from PIL import Image
import tempfile
from django.core.files.base import ContentFile
import pytz
from django.utils import timezone
from django.conf import settings


# Obtener el objeto datetime desde la base de datos
my_datetime = timezone.now()

# Convertir a la zona horaria configurada en Django
my_datetime = timezone.localtime(my_datetime, pytz.timezone(settings.TIME_ZONE))


def generar_vouchers(tipo, cantidad, usuario):
    # Obtener el tipo de voucher correspondiente
    tipo_id = tipo.id
    tipo_nombre = tipo.tipo

    # Crear el lote y orden correspondientes
    ahora = datetime.datetime.now()
    lote = ahora.strftime('%y%j')  # últimos dos dígitos del año + día del año
    ultima_orden = Voucher.objects.filter(lote=lote).order_by('-orden').first().orden if Voucher.objects.filter(lote=lote).count() > 0 else 0
    orden = "{:04d}".format(int(ultima_orden) + 1)

    vouchers_generados = []
    for i in range(cantidad):
        # Crear el número de serie
        serie = f"{tipo.tipo}{str(lote)}{orden}"

        # Crear el voucher correspondiente
        voucher = Voucher(serie=serie, lote=lote, orden=orden, monto=tipo.monto, tipo=tipo.nombre, creado_usr=usuario)
        #voucher.impreso = True
        voucher.save()

        vouchers_generados.append(voucher)
        print(f"Voucher generado: {voucher.serie}")

        # Actualizar el orden
        orden = "{:04d}".format(int(orden) + 1)

    etiquetas_generadas = []
    for voucher in vouchers_generados:
        # Crear la etiqueta correspondiente
        if Etiqueta.objects.filter(serie=voucher.serie).exists():
            continue

        with BytesIO() as buffer:
            barcode.generate('EAN13', voucher.serie, writer=ImageWriter(), output=buffer)

            etiqueta_imagen = Etiqueta(serie=voucher.serie, creado_usr=usuario)

            # Cargar los datos de la imagen desde el objeto BytesIO
            buffer.seek(0)
            img = Image.open(buffer)

            # Guardar la imagen como la imagen de la etiqueta
            with BytesIO() as image_buffer:
                img.save(image_buffer, format='PNG')
                etiqueta_imagen.imagen = image_buffer.getvalue()

            etiqueta_imagen.save()
            #etiquetas_generadas.append(etiqueta_imagen)
            print(f"Etiqueta generada: {etiqueta_imagen.serie}")

    print(f"Total de etiquetas generadas: {len(etiquetas_generadas)}")
    return etiquetas_generadas
