from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'style': 'resize: none;'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all duration-300'
            })
        # Personnalisation des messages d'aide
        self.fields['username'].help_text = '150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement.'
        self.fields['password1'].help_text = 'Votre mot de passe doit contenir au moins 8 caractères.'
        self.fields['password2'].help_text = 'Entrez le même mot de passe que précédemment, pour vérification.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get('instance')
        
        # Définir les classes de base pour tous les champs
        base_classes = "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all duration-300"
        
        # Personnaliser chaque champ avec ses propres attributs
        self.fields['first_name'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'Votre prénom',
        })
        
        self.fields['last_name'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'Votre nom',
        })
        
        self.fields['email'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'votre@email.com',
            'type': 'email',
        })
        
        self.fields['phone_number'].widget.attrs.update({
            'class': base_classes,
            'placeholder': 'Votre numéro de téléphone',
            'type': 'tel',
        })
        
        self.fields['address'].widget = forms.Textarea(attrs={
            'class': f"{base_classes} h-24 resize-none",
            'placeholder': 'Votre adresse complète',
            'rows': 3,
        })

        # Si l'utilisateur existe, mettre à jour les placeholders avec ses données actuelles
        if user:
            for field_name in self.fields:
                current_value = getattr(user, field_name, '')
                if current_value:
                    self.fields[field_name].widget.attrs['placeholder'] = current_value

class EmployeeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_employee = True
        if commit:
            user.save()
        return user 