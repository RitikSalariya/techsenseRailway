from django import forms
from django.contrib.auth.models import User
from .models import ContactMessage
from .models import Profile



from django.core.validators import validate_email

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'idea_description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500'
            }),
            'idea_description': forms.Textarea(attrs={
                'class': 'w-full border border-slate-200 rounded-lg px-3 py-2 text-sm min-h-[120px] focus:outline-none focus:ring-1 focus:ring-indigo-500'
            }),
        }


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-xl border border-slate-200 bg-white text-sm "
                     "focus:outline-none focus:ring-2 focus:ring-[#4F46E5]/40 focus:border-[#4F46E5] "
                     "placeholder:text-slate-400",
            "placeholder": "Choose a username",
        })
    )

    # 👇 THIS is where email becomes a real EmailField (type="email" in HTML)
    email = forms.EmailField(
        required=True,
        validators=[validate_email],
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 rounded-xl border border-slate-200 bg-white text-sm "
                     "focus:outline-none focus:ring-2 focus:ring-[#4F46E5]/40 focus:border-[#4F46E5] "
                     "placeholder:text-slate-400",
            "placeholder": "you@example.com",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-xl border border-slate-200 bg-white text-sm "
                     "focus:outline-none focus:ring-2 focus:ring-[#4F46E5]/40 focus:border-[#4F46E5] "
                     "placeholder:text-slate-400",
            "placeholder": "Create a password",
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-xl border border-slate-200 bg-white text-sm "
                     "focus:outline-none focus:ring-2 focus:ring-[#4F46E5]/40 focus:border-[#4F46E5] "
                     "placeholder:text-slate-400",
            "placeholder": "Repeat password",
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # ✅ keep BOTH fields here
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-[#F7F9FC] border border-slate-200 '
                         'focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-[#F7F9FC] border border-slate-200 '
                         'focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50',
                'placeholder': 'your.email@example.com',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make email NOT editable
        self.fields['email'].widget.attrs.update({
            'readonly': True,
            'style': 'background-color: #f1f5f9; cursor: not-allowed;'
        })
        self.fields['username'].widget.attrs.update({
            'readonly': True,
            'style': 'background-color: #f1f5f9; cursor: not-allowed;'
        })

        # Optional: Also disable validation updates
        self.fields['email'].disabled = True
        self.fields['username'].disabled = True

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'whatsapp', 'college', 'branch', 'year']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
            'whatsapp': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
            'college': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
            'branch': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
            'year': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-slate-200 bg-[#F7F9FC]'}),
        }
