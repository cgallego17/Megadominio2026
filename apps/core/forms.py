from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from apps.clients.models import Client
from apps.services.models import Service, ClientService
from apps.quotes.models import Quote, QuoteItem
from apps.invoices.models import Invoice, InvoiceItem, CuentaDeCobro, CuentaDeCobroItem
from apps.store.models import ProductCategory, Product, Order, OrderItem

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
            'phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 300 123 4567'}),
            'document_type': forms.Select(attrs=_select),
            'document_number': forms.TextInput(attrs={**_input, 'placeholder': '123456789'}),
            'company': forms.TextInput(attrs={**_input, 'placeholder': 'Empresa S.A.S'}),
            'address': forms.TextInput(attrs={**_input, 'placeholder': 'Dirección completa'}),
            'is_active': forms.CheckboxInput(attrs=_checkbox),
        }


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
        fields = ['client', 'service', 'status', 'start_date', 'end_date',
                  'monthly_price', 'notes']
        widgets = {
            'client': forms.Select(attrs=_select),
            'service': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'end_date': forms.DateInput(attrs=_date),
            'monthly_price': forms.NumberInput(attrs={**_number, 'placeholder': '0.00'}),
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
            'phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 300 123 4567'}),
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
            'placeholder': '+57 300 123 4567'
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
            'customer_phone': forms.TextInput(attrs={**_input, 'placeholder': '+57 300 123 4567'}),
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
    first_name = forms.CharField(
        max_length=30, label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': 'Tu nombre',
        }),
    )
    last_name = forms.CharField(
        max_length=30, label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': 'Tu apellido',
        }),
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': 'tu@email.com',
        }),
    )
    phone = forms.CharField(
        max_length=20, label='Teléfono', required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': '+57 300 123 4567',
        }),
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': 'Mínimo 8 caracteres',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 transition text-gray-900 placeholder-gray-400',
            'placeholder': 'Repite tu contraseña',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo electrónico.'
            )
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        if p1 and len(p1) < 8:
            self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        # Generar username a partir del email
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
                **_profile_input, 'placeholder': '+57 300 123 4567',
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
