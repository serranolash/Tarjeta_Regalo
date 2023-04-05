from django.db import models
import datetime
import decimal
from django.contrib.auth import get_user_model
import uuid
import barcode
from barcode import Code128
from django.core.files import File
import io
from PIL import Image
from barcode.writer import ImageWriter
from barcode.codex import Code128
import uuid
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
import random
import string
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser


def generar_tipo(monto):
    monto_str = str(monto)
    digitos_no_ceros = monto_str.rstrip('0')
    cant_ceros = len(monto_str) - len(digitos_no_ceros)
    tipo_nombre = f"{str(digitos_no_ceros).zfill(2)}{str(cant_ceros).zfill(2)}"
    
    return tipo_nombre


def generar_serie(self):
        tipo_int = int(self.tipo)
        tipo_str = f"{self.tipo}{self.lote}"
        return "{}{:03d}".format(tipo_str, self.orden)   

# Create your models here.
class Tipo(models.Model):
    
    nombre = models.CharField(max_length=50, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    

class Etiqueta(models.Model):
    serie = models.CharField(max_length=100)
    imagen = models.BinaryField()
    creado_fecha = models.DateTimeField(default=timezone.now)
    creado_usr = models.CharField(max_length=50)

class Local(models.Model):
    nombre = models.CharField(max_length=50)    

    def __str__(self):
        return self.nombre
            
class Voucher(models.Model):
    ESTADOS = (
        ('ACTIVO', 'Activo'),
        ('CADUCADO', 'Caducado'),
        ('CANJEADO', 'Canjeado'),
        ('IMPRESO', 'Impreso'),
    )
    
    # Campos
    serie = models.CharField(max_length=20, primary_key=True)    
    lote = models.CharField(max_length=20)
    orden = models.CharField(max_length=20)
    tipo = models.CharField(max_length=2, default='PC')
    creado_fecha = models.DateTimeField(auto_now_add=True)
    creado_usr = models.CharField(max_length=50)    
    impreso = models.BooleanField(default=False)
    impreso_fecha = models.DateTimeField(null=True, blank=True)
    impreso_usr = models.CharField(max_length=50, null=True, blank=True)
    impresiones = models.PositiveIntegerField(default=0) # Campo adiciona
    enviado = models.BooleanField(default=False)
    enviado_fecha = models.DateTimeField(null=True, blank=True)
    enviado_usr = models.CharField(max_length=50, null=True, blank=True)
    vendido = models.BooleanField(default=False)
    vendido_fecha = models.DateTimeField(null=True, blank=True)
    vendido_usr = models.CharField(max_length=50, null=True, blank=True)
    usado = models.BooleanField(default=False)
    usado_fecha = models.DateTimeField(null=True, blank=True)
    usado_usr = models.CharField(max_length=50, null=True, blank=True)
    audit = models.BooleanField(default=False)
    audit_fecha = models.DateTimeField(null=True, blank=True)
    audit_usr = models.CharField(max_length=50, null=True, blank=True)
    destr = models.BooleanField(default=False)
    destr_fecha = models.DateTimeField(null=True, blank=True)
    destr_usr = models.CharField(max_length=50, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='ARG')
    estado = models.CharField(max_length=20, default='DISPONIBLE')
    local = models.ForeignKey(Local, null=True, on_delete=models.CASCADE)
    recibido = models.BooleanField(default=False)
    recibido_fecha = models.DateTimeField(null=True, blank=True)
    recibido_usr = models.CharField(max_length=100, null=True, blank=True)
   


    # Métodos
    def __str__(self):
        return self.serie
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        (1, 'Usuario Común'),
        (2, 'Usuario Avanzado'),
        (3, 'Administrador'),
        (4, 'Auditor'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.username