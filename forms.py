from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Voucher, Tipo, Local, CustomUser
class TipoForm(forms.ModelForm):
    monto = forms.IntegerField()

    class Meta:
        model = Tipo
        fields = ['monto','nombre']
        

class ImprimirEtiquetasForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, max_value=100)
    tipo = forms.ModelChoiceField(queryset=Tipo.objects.all())


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].label = 'Seleccionar tipo'

    cantidad.widget.attrs.update({'class': 'form-control'})
    tipo.widget.attrs.update({'class': 'form-control'})


class LocalForm(forms.Form):
    local_id = forms.ModelChoiceField(queryset=Local.objects.all(), label='Local')

class VoucherForm(forms.Form):
    vouchers = forms.ModelMultipleChoiceField(queryset=Voucher.objects.none(), widget=forms.CheckboxSelectMultiple, label='Vouchers')

    def set_voucher_queryset(self, vouchers):
        self.fields['vouchers'].queryset = vouchers


class VenderForm(forms.Form):
    local = forms.ModelChoiceField(queryset=Local.objects.all(), label='Local de venta')
    voucher = forms.ModelChoiceField(queryset=Voucher.objects.filter(estado='DISPONIBLE'), label='Voucher a vender')


class VoucherUpdateForm(forms.ModelForm):
    audit = forms.BooleanField(required=False)
    destr = forms.BooleanField(required=False)
    destr_usr = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Voucher
        fields = ['audit', 'audit_fecha', 'audit_usr', 'destr', 'destr_fecha', 'destr_usr']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']


class AuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
