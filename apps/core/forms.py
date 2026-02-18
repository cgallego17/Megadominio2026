from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from apps.accounts.models import Country, State, City, UserAddress
from apps.clients.models import Client
from apps.services.models import Service, ClientService
from apps.quotes.models import Quote, QuoteItem
from apps.invoices.models import Invoice, InvoiceItem, CuentaDeCobro, CuentaDeCobroItem
from apps.store.models import ProductCategory, Product, Order, OrderItem
from .models import HomeClientLogo, HomeTestimonial

User = get_user_model()

# ── Shared widget attrs ──────────────────────────────────────────────
_input = {
    'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2.5 focus:border-red-500 focus:ring-1 focus:ring-red-500 placeholder-gray-500',
}
_select = {
    'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2.5 focus:border-red-500 focus:ring-1 focus:ring-red-500',
}
_textarea = {
    'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2.5 focus:border-red-500 focus:ring-1 focus:ring-red-500 placeholder-gray-500',
    'rows': '3',
}
_checkbox = {
    'class': 'w-4 h-4 text-red-600 bg-gray-800 border-gray-600 rounded focus:ring-red-500',
}
_date = {
    'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2.5 focus:border-red-500 focus:ring-1 focus:ring-red-500',
    'type': 'date',
}
_number = {
    'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2.5 focus:border-red-500 focus:ring-1 focus:ring-red-500',
    'step': '0.01',
}


# ══════════════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════════════

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'document_type', 'document_number',
                  'company', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={**_input, 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 324 4011967'}),
            'document_type': forms.Select(attrs=_select),
            'document_number': forms.TextInput(attrs={**_input, 'placeholder': '123456789'}),
            'company': forms.TextInput(attrs={**_input, 'placeholder': 'Empresa S.A.S'}),
            'address': forms.TextInput(attrs={**_input, 'placeholder': 'Dirección completa'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }


# ══════════════════════════════════════════════════════════════════════
# HOME: LOGOS DE CLIENTES Y TESTIMONIOS
# ══════════════════════════════════════════════════════════════════════

class HomeClientLogoForm(forms.ModelForm):
    class Meta:
        model = HomeClientLogo
        fields = ['name', 'url', 'image', 'icon', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre de la marca'}),
            'url': forms.URLInput(attrs={**_input, 'placeholder': 'https://www.ejemplo.com'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2 focus:border-red-500 focus:ring-1 focus:ring-red-500 file:mr-4 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-600 file:text-white hover:file:bg-red-700',
                'accept': 'image/*',
            }),
            'icon': forms.TextInput(attrs={**_input, 'placeholder': 'fa-rocket (si no hay imagen)'}),
            'order': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '0', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }


class HomeTestimonialForm(forms.ModelForm):
    class Meta:
        model = HomeTestimonial
        fields = [
            'name', 'role', 'company', 'initials', 'avatar',
            'rating', 'comment', 'order', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre del cliente'}),
            'role': forms.TextInput(attrs={**_input, 'placeholder': 'Cargo'}),
            'company': forms.TextInput(attrs={**_input, 'placeholder': 'Empresa'}),
            'initials': forms.TextInput(attrs={**_input, 'placeholder': 'Iniciales (p. ej. AM)'}),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2 focus:border-red-500 focus:ring-1 focus:ring-red-500 file:mr-4 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-600 file:text-white hover:file:bg-red-700',
                'accept': 'image/*',
            }),
            'rating': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '5', 'min': '1', 'max': '5'}),
            'comment': forms.Textarea(attrs={**_textarea, 'placeholder': 'Comentario del cliente...'}),
            'order': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '0', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }

    def clean_rating(self):
        r = self.cleaned_data.get('rating') or 5
        if r < 1:
            r = 1
        if r > 5:
            r = 5
        return r

# ══════════════════════════════════════════════════════════════════════
# SERVICIOS
# ══════════════════════════════════════════════════════════════════════

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'billing_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre del servicio'}),
            'description': forms.Textarea(attrs={**_textarea, 'placeholder': 'Descripción del servicio...'}),
            'price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'billing_type': forms.Select(attrs=_select),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }


# ══════════════════════════════════════════════════════════════════════
# COTIZACIONES + ITEMS (inline formset)
# ══════════════════════════════════════════════════════════════════════

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['client', 'status', 'discount_percentage', 'discount_amount',
                  'tax_percentage', 'notes', 'valid_until']
        widgets = {
            'client': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'discount_percentage': forms.NumberInput(attrs={**_number, 'placeholder': '0'}),
            'discount_amount': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'tax_percentage': forms.NumberInput(attrs={**_number, 'placeholder': '19'}),
            'notes': forms.Textarea(attrs={**_textarea, 'placeholder': 'Notas adicionales...'}),
            'valid_until': forms.DateInput(attrs=_date),
        }


class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['service', 'description', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs=_select),
            'description': forms.TextInput(attrs={**_input, 'placeholder': 'Descripción del item'}),
            'quantity': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '1', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
        }


QuoteItemFormSet = inlineformset_factory(
    Quote, QuoteItem, form=QuoteItemForm,
    extra=1, can_delete=True,
)


# ══════════════════════════════════════════════════════════════════════
# FACTURAS + ITEMS (inline formset)
# ══════════════════════════════════════════════════════════════════════

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'quote', 'status', 'subtotal', 'discount_amount',
                  'tax_amount', 'total', 'issue_date', 'due_date', 'notes']
        widgets = {
            'client': forms.Select(attrs=_select),
            'quote': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'subtotal': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'discount_amount': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'tax_amount': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'total': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'issue_date': forms.DateInput(attrs=_date),
            'due_date': forms.DateInput(attrs=_date),
            'notes': forms.Textarea(attrs={**_textarea, 'placeholder': 'Notas...'}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['service', 'description', 'quantity', 'unit_price', 'subtotal']
        widgets = {
            'service': forms.Select(attrs=_select),
            'description': forms.TextInput(attrs={**_input, 'placeholder': 'Descripción'}),
            'quantity': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '1', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'subtotal': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
        }


InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    extra=1, can_delete=True,
)


# ══════════════════════════════════════════════════════════════════════
# CUENTAS DE COBRO + ITEMS (inline formset)
# ══════════════════════════════════════════════════════════════════════

class CuentaDeCobroForm(forms.ModelForm):
    class Meta:
        model = CuentaDeCobro
        fields = ['client', 'quote', 'discount_amount', 'tax_percentage',
                  'issue_date', 'due_date', 'notes']
        widgets = {
            'client': forms.Select(attrs=_select),
            'quote': forms.Select(attrs=_select),
            'discount_amount': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'tax_percentage': forms.NumberInput(attrs={**_number, 'placeholder': '15'}),
            'issue_date': forms.DateInput(attrs=_date),
            'due_date': forms.DateInput(attrs=_date),
            'notes': forms.Textarea(attrs={**_textarea, 'placeholder': 'Notas...'}),
        }


class CuentaDeCobroItemForm(forms.ModelForm):
    class Meta:
        model = CuentaDeCobroItem
        fields = ['service', 'description', 'quantity', 'unit_price']
        widgets = {
            'service': forms.Select(attrs=_select),
            'description': forms.TextInput(attrs={**_input, 'placeholder': 'Descripción del item'}),
            'quantity': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '1', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
        }


CuentaDeCobroItemFormSet = inlineformset_factory(
    CuentaDeCobro, CuentaDeCobroItem, form=CuentaDeCobroItemForm,
    extra=1, can_delete=True,
)


# ══════════════════════════════════════════════════════════════════════
# SERVICIOS DE CLIENTES (ClientService)
# ══════════════════════════════════════════════════════════════════════

class ClientServiceForm(forms.ModelForm):
    class Meta:
        model = ClientService
        fields = ['client', 'service', 'billing_type', 'status', 'start_date', 'end_date',
                  'monthly_price', 'renewal_price', 'notes']
        widgets = {
            'client': forms.Select(attrs=_select),
            'service': forms.Select(attrs=_select),
            'billing_type': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'end_date': forms.DateInput(attrs=_date),
            'monthly_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'renewal_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00 (0 = igual al valor)'}),
            'notes': forms.Textarea(attrs={**_textarea, 'placeholder': 'Notas sobre este servicio...'}),
        }


# ══════════════════════════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════════════════════════

class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña', required=False,
        widget=forms.PasswordInput(attrs={**_input, 'placeholder': 'Dejar vacío para no cambiar'}),
        help_text='Dejar vacío para mantener la contraseña actual.',
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', required=False,
        widget=forms.PasswordInput(attrs={**_input, 'placeholder': 'Repetir contraseña'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'role', 'is_active', 'is_verified']
        widgets = {
            'username': forms.TextInput(attrs={**_input, 'placeholder': 'nombre_usuario'}),
            'first_name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={**_input, 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={**_input, 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 324 4011967'}),
            'role': forms.Select(attrs=_select),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
            'is_verified': forms.CheckboxInput(attrs=_checkbox),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(p1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get('password1')
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
        return user


class UserCreateForm(UserForm):
    password1 = forms.CharField(
        label='Contraseña', required=True,
        widget=forms.PasswordInput(attrs={**_input, 'placeholder': 'Contraseña'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña', required=True,
        widget=forms.PasswordInput(attrs={**_input, 'placeholder': 'Repetir contraseña'}),
    )


class QuoteRequestForm(forms.Form):
    """Formulario para solicitud de cotización desde el sitio web"""
    
    # Información del cliente
    name = forms.CharField(
        max_length=200,
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition',
            'placeholder': 'Juan Pérez'
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition',
            'placeholder': 'juan@ejemplo.com'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition',
            'placeholder': '+57 324 4011967'
        })
    )
    
    company = forms.CharField(
        max_length=200,
        required=False,
        label="Empresa (opcional)",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition',
            'placeholder': 'Mi Empresa S.A.S'
        })
    )
    
    # Información del servicio
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        label="Servicio de interés",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition'
        })
    )
    
    message = forms.CharField(
        label="Cuéntanos sobre tu proyecto",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition',
            'placeholder': 'Describe brevemente lo que necesitas...',
            'rows': 4
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


# ══════════════════════════════════════════════════════════════════════
# CATEGORÍAS DE PRODUCTOS
# ══════════════════════════════════════════════════════════════════════

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'icon', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre de la categoría'}),
            'icon': forms.TextInput(attrs={**_input, 'placeholder': 'fa-tag'}),
            'order': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '0'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }


# ══════════════════════════════════════════════════════════════════════
# PRODUCTOS
# ══════════════════════════════════════════════════════════════════════

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'image', 'price',
                  'compare_price', 'icon', 'icon_color', 'badge', 'stock',
                  'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre del producto'}),
            'category': forms.Select(attrs=_select),
            'description': forms.Textarea(attrs={**_textarea, 'placeholder': 'Descripción del producto...'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2 focus:border-red-500 focus:ring-1 focus:ring-red-500 file:mr-4 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-600 file:text-white hover:file:bg-red-700',
                'accept': 'image/*',
            }),
            'price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'compare_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00 (opcional)'}),
            'icon': forms.TextInput(attrs={**_input, 'placeholder': 'fa-box'}),
            'icon_color': forms.TextInput(attrs={**_input, 'placeholder': 'text-red-500'}),
            'badge': forms.Select(attrs=_select),
            'stock': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '0', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
            'is_featured': forms.CheckboxInput(attrs=_checkbox),
        }


# ══════════════════════════════════════════════════════════════════════
# ÓRDENES + ITEMS (inline formset)
# ══════════════════════════════════════════════════════════════════════

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['number', 'customer_name', 'customer_email', 'customer_phone',
                  'customer_address', 'status', 'shipping_cost', 'discount', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={**_input, 'placeholder': 'ORD-001'}),
            'customer_name': forms.TextInput(attrs={**_input, 'placeholder': 'Nombre del cliente'}),
            'customer_email': forms.EmailInput(attrs={**_input, 'placeholder': 'correo@ejemplo.com'}),
            'customer_phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 324 4011967'}),
            'customer_address': forms.Textarea(attrs={**_textarea, 'placeholder': 'Dirección de envío...'}),
            'status': forms.Select(attrs=_select),
            'shipping_cost': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'discount': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
            'notes': forms.Textarea(attrs={**_textarea, 'placeholder': 'Notas internas...'}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'description', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs=_select),
            'description': forms.TextInput(attrs={**_input, 'placeholder': 'Descripción del item'}),
            'quantity': forms.NumberInput(attrs={**_number, 'step': '1', 'placeholder': '1', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True,
)


# ══════════════════════════════════════════════════════════════════════
# REGISTRO DE USUARIO
# ══════════════════════════════════════════════════════════════════════

class SignupForm(forms.Form):
    """Formulario de registro público."""
    _input_cls = (
        'w-full px-4 py-3 rounded-lg border border-gray-300 '
        'focus:border-red-500 focus:ring-2 focus:ring-red-200 '
        'transition text-gray-900 placeholder-gray-400'
    )

    # Honeypot — hidden field, bots fill it, humans don't
    website_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'tabindex': '-1', 'autocomplete': 'off',
        }),
    )

    first_name = forms.CharField(
        max_length=30, label='Nombre',
        widget=forms.TextInput(attrs={
            'class': _input_cls,
            'placeholder': 'Tu nombre',
        }),
    )
    last_name = forms.CharField(
        max_length=30, label='Apellido',
        widget=forms.TextInput(attrs={
            'class': _input_cls,
            'placeholder': 'Tu apellido',
        }),
    )
    email = forms.EmailField(
        label='Correo electr\u00f3nico',
        widget=forms.EmailInput(attrs={
            'class': _input_cls,
            'placeholder': 'tu@email.com',
        }),
    )
    phone = forms.CharField(
        max_length=20, label='Tel\u00e9fono', required=False,
        widget=forms.TextInput(attrs={
            'class': _input_cls,
            'placeholder': '+57 324 4011967',
        }),
    )
    password1 = forms.CharField(
        label='Contrase\u00f1a',
        widget=forms.PasswordInput(attrs={
            'class': _input_cls,
            'placeholder': 'M\u00ednimo 8 caracteres',
            'id': 'id_password1',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contrase\u00f1a',
        widget=forms.PasswordInput(attrs={
            'class': _input_cls,
            'placeholder': 'Repite tu contrase\u00f1a',
        }),
    )
    accept_terms = forms.BooleanField(
        label='Acepto los t\u00e9rminos y condiciones',
        error_messages={
            'required': 'Debes aceptar los t\u00e9rminos para registrarte.',
        },
    )

    CUSTOMER_TYPE_CHOICES = (
        ('person', 'Persona natural'),
        ('company', 'Empresa'),
    )
    DOCUMENT_TYPE_CHOICES = (
        ('nit', 'NIT'),
        ('cc', 'Cédula de ciudadanía'),
        ('ce', 'Cédula de extranjería'),
        ('passport', 'Pasaporte'),
    )
    customer_type = forms.ChoiceField(
        label='Tipo de cliente', choices=CUSTOMER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': _input_cls}),
    )
    document_type = forms.ChoiceField(
        label='Tipo de documento', choices=DOCUMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': _input_cls, 'id': 'id_document_type'}),
    )
    document_number = forms.CharField(
        max_length=50, label='Número de documento',
        widget=forms.TextInput(attrs={'class': _input_cls, 'placeholder': 'Número identificaci\u00f3n'}),
    )

    address = forms.CharField(
        label='Dirección', max_length=255,
        widget=forms.TextInput(attrs={'class': _input_cls, 'placeholder': 'Calle, número, barrio…'}),
    )
    country = forms.ModelChoiceField(
        label='País', queryset=Country.objects.none(),
        widget=forms.Select(attrs={'class': _input_cls, 'id': 'id_country'}),
    )
    state = forms.ModelChoiceField(
        label='Departamento', queryset=State.objects.none(),
        widget=forms.Select(attrs={'class': _input_cls, 'id': 'id_state'}),
    )
    city = forms.ModelChoiceField(
        label='Ciudad', queryset=City.objects.none(),
        widget=forms.Select(attrs={'class': _input_cls, 'id': 'id_city'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.all()
        # Prefer posted data; otherwise set default to Colombia
        if 'country' in self.data:
            try:
                cid = int(self.data.get('country') or 0)
                self.fields['state'].queryset = State.objects.filter(country_id=cid)
            except (TypeError, ValueError):
                self.fields['state'].queryset = State.objects.none()
        else:
            try:
                co = Country.objects.filter(iso2__iexact='CO').first() or Country.objects.filter(name__iexact='Colombia').first()
                if co:
                    self.fields['country'].initial = co.pk
                    self.fields['state'].queryset = State.objects.filter(country=co)
            except Exception:
                pass
        if 'state' in self.data:
            try:
                sid = int(self.data.get('state') or 0)
                self.fields['city'].queryset = City.objects.filter(state_id=sid)
            except (TypeError, ValueError):
                self.fields['city'].queryset = City.objects.none()

    def clean_website_url(self):
        """Honeypot: reject if filled."""
        if self.cleaned_data.get('website_url'):
            raise forms.ValidationError('Bot detected.')
        return ''

    def clean_first_name(self):
        import re
        name = self.cleaned_data['first_name'].strip()
        name = re.sub(r'[<>{}\[\]\\]', '', name)
        if not name:
            raise forms.ValidationError('Nombre inv\u00e1lido.')
        return name

    def clean_last_name(self):
        import re
        name = self.cleaned_data['last_name'].strip()
        name = re.sub(r'[<>{}\[\]\\]', '', name)
        if not name:
            raise forms.ValidationError('Apellido inv\u00e1lido.')
        return name

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo electr\u00f3nico.'
            )
        disposable = [
            'mailinator.com', 'guerrillamail.com', 'tempmail.com',
            'throwaway.email', 'yopmail.com', 'sharklasers.com',
            'guerrillamailblock.com', 'grr.la', 'dispostable.com',
        ]
        domain = email.split('@')[-1]
        if domain in disposable:
            raise forms.ValidationError(
                'No se permiten correos temporales.'
            )
        return email

    def clean_phone(self):
        import re
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            phone = re.sub(r'[^\d+\- ]', '', phone)
        return phone

    def clean(self):
        import re
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contrase\u00f1as no coinciden.')
        if p1:
            if len(p1) < 8:
                self.add_error(
                    'password1',
                    'La contrase\u00f1a debe tener al menos 8 caracteres.'
                )
            if not re.search(r'[A-Z]', p1):
                self.add_error(
                    'password1',
                    'Debe contener al menos una letra may\u00fascula.'
                )
            if not re.search(r'[a-z]', p1):
                self.add_error(
                    'password1',
                    'Debe contener al menos una letra min\u00fascula.'
                )
            if not re.search(r'\d', p1):
                self.add_error(
                    'password1',
                    'Debe contener al menos un n\u00famero.'
                )
            if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+]', p1):
                self.add_error(
                    'password1',
                    'Debe contener al menos un car\u00e1cter especial.'
                )
            email = cleaned.get('email', '')
            name = cleaned.get('first_name', '')
            if email and p1.lower() in email.lower():
                self.add_error(
                    'password1',
                    'La contrase\u00f1a no puede contener tu email.'
                )
            if name and len(name) > 2 and name.lower() in p1.lower():
                self.add_error(
                    'password1',
                    'La contrase\u00f1a no puede contener tu nombre.'
                )
        ct = cleaned.get('customer_type')
        dt = cleaned.get('document_type')
        if ct and dt:
            if ct == 'company' and dt != 'nit':
                self.add_error('document_type', 'Para empresa el documento debe ser NIT.')
            if ct == 'person' and dt not in {'cc', 'ce', 'passport'}:
                self.add_error('document_type', 'Selecciona un documento válido para persona.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        base_username = data['email'].split('@')[0]
        username = base_username
        n = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{n}'
            n += 1

        user = User.objects.create_user(
            username=username,
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='client',
        )
        if data.get('phone'):
            user.phone = data['phone']
            user.save(update_fields=['phone'])
        try:
            ct = data.get('customer_type')
            dt = data.get('document_type')
            dn = data.get('document_number', '').strip()
            map_dt = {'nit': 'rtn', 'cc': 'dni', 'ce': 'other', 'passport': 'passport'}
            client = Client.objects.create(
                user=user,
                name=(data['first_name'] + ' ' + data['last_name']).strip(),
                email=data['email'],
                phone=data.get('phone', ''),
                document_type=map_dt.get(dt, 'other'),
                document_number=dn,
                company='' if ct == 'person' else '',
                address=data.get('address', ''),
                is_active=True,
            )
            try:
                ua = UserAddress(
                    user=user,
                    label='Principal',
                    address=data.get('address', ''),
                    country=data.get('country'),
                    state=data.get('state'),
                    city=data.get('city'),
                    is_default=True,
                )
                ua.save()
            except Exception:
                pass
        except Exception:
            pass
        return user


# ══════════════════════════════════════════════════════════════════════
# EDITAR PERFIL (Panel de usuario)
# ══════════════════════════════════════════════════════════════════════

_profile_input = {
    'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 '
             'focus:border-red-500 focus:ring-2 focus:ring-red-200 '
             'transition text-gray-900 placeholder-gray-400',
}


class ProfileForm(forms.ModelForm):
    """Formulario para que el usuario edite su perfil."""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                **_profile_input, 'placeholder': 'Tu nombre',
            }),
            'last_name': forms.TextInput(attrs={
                **_profile_input, 'placeholder': 'Tu apellido',
            }),
            'email': forms.EmailInput(attrs={
                **_profile_input, 'placeholder': 'tu@email.com',
            }),
            'phone': forms.TextInput(attrs={
                **_profile_input, 'placeholder': '+57 324 4011967',
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                'Ya existe otra cuenta con este correo.'
            )
        return email


class UserAddressForm(forms.ModelForm):
    """Formulario para agregar/editar direcciones del usuario."""

    _sel = {
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 '
                 'focus:border-red-500 focus:ring-2 focus:ring-red-200 '
                 'transition text-gray-900 bg-white',
    }

    class Meta:
        from apps.accounts.models import UserAddress
        model = UserAddress
        fields = [
            'label', 'address', 'country', 'state',
            'city', 'postal_code', 'is_default',
        ]
        widgets = {
            'label': forms.TextInput(attrs={
                **_profile_input,
                'placeholder': 'Ej: Casa, Oficina…',
            }),
            'address': forms.TextInput(attrs={
                **_profile_input,
                'placeholder': 'Calle, número, barrio…',
            }),
            'postal_code': forms.TextInput(attrs={
                **_profile_input, 'placeholder': 'Código postal',
            }),
        }
        labels = {
            'label': 'Etiqueta',
            'address': 'Dirección',
            'country': 'País',
            'state': 'Departamento',
            'city': 'Ciudad',
            'postal_code': 'Código postal',
            'is_default': 'Dirección principal',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import Country, State, City

        iso_map = dict(
            Country.objects.values_list('pk', 'iso2')
        )

        class CountrySelect(forms.Select):
            """Select that adds data-iso2 to each country option."""
            def create_option(self, name, value, label, selected,
                              index, subindex=None, attrs=None):
                opt = super().create_option(
                    name, value, label, selected,
                    index, subindex, attrs,
                )
                if value and value in iso_map:
                    opt['attrs']['data-iso2'] = iso_map[value]
                return opt

        self.fields['country'].widget = CountrySelect(
            attrs={**self._sel, 'id': 'id_country'}
        )
        self.fields['country'].queryset = Country.objects.all()
        self.fields['country'].empty_label = '— Selecciona país —'

        self.fields['state'].widget = forms.Select(
            attrs={**self._sel, 'id': 'id_state'}
        )
        self.fields['state'].empty_label = '— Selecciona departamento —'

        self.fields['city'].widget = forms.Select(
            attrs={**self._sel, 'id': 'id_city'}
        )
        self.fields['city'].empty_label = '— Selecciona ciudad —'

        if self.instance and self.instance.pk:
            if self.instance.country_id:
                self.fields['state'].queryset = State.objects.filter(
                    country_id=self.instance.country_id
                )
            else:
                self.fields['state'].queryset = State.objects.none()
            if self.instance.state_id:
                self.fields['city'].queryset = City.objects.filter(
                    state_id=self.instance.state_id
                )
            else:
                self.fields['city'].queryset = City.objects.none()
        elif self.data.get('country'):
            try:
                cid = int(self.data.get('country'))
                self.fields['state'].queryset = (
                    State.objects.filter(country_id=cid)
                )
            except (ValueError, TypeError):
                self.fields['state'].queryset = State.objects.none()
            try:
                sid = int(self.data.get('state'))
                self.fields['city'].queryset = (
                    City.objects.filter(state_id=sid)
                )
            except (ValueError, TypeError):
                self.fields['city'].queryset = City.objects.none()
        else:
            self.fields['state'].queryset = State.objects.none()
            self.fields['city'].queryset = City.objects.none()


class PasswordChangeForm(forms.Form):
    """Formulario para cambiar contraseña desde el panel."""
    current_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            **_profile_input, 'placeholder': 'Tu contraseña actual',
        }),
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            **_profile_input, 'placeholder': 'Mínimo 8 caracteres',
        }),
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            **_profile_input, 'placeholder': 'Repite la nueva contraseña',
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data['current_password']
        if not self.user.check_password(pwd):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Las contraseñas no coinciden.')
        if p1 and len(p1) < 8:
            self.add_error(
                'new_password1',
                'La contraseña debe tener al menos 8 caracteres.'
            )
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save(update_fields=['password'])
        return self.user
