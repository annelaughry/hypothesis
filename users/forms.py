from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Profile
import python_avatars as pa

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        help_text="Enter a valid email address"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'level', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        validate_password(password1, self.instance)

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        return password2


class StrongPasswordChangeForm(PasswordChangeForm):
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if len(password1) < 12:
            raise forms.ValidationError("Password must be at least 12 characters long.")

        validate_password(password1, self.user)

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("New passwords don't match.")

        return password2


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'school', 'age', 'avatar']


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'school', 'avatar']


class AvatarCustomizationForm(forms.ModelForm):
    HAIR_TYPE_CHOICES = [(h.name, h.name.replace("_", " ").title()) for h in pa.HairType]
    HAIR_COLOR_CHOICES = [(c.name, c.name.replace("_", " ").title()) for c in pa.HairColor]
    SKIN_COLOR_CHOICES = [(s.name, s.name.replace("_", " ").title()) for s in pa.SkinColor]
    CLOTHING_TYPE_CHOICES = [(c.name, c.name.replace("_", " ").title()) for c in pa.ClothingType]
    CLOTHING_COLOR_CHOICES = [(c.name, c.name.replace("_", " ").title()) for c in pa.ClothingColor]
    FACIAL_HAIR_CHOICES = [(f.name, f.name.replace("_", " ").title()) for f in pa.FacialHairType]
    EYE_TYPE_CHOICES = [(e.name, e.name.replace("_", " ").title()) for e in pa.EyeType]
    EYEBROW_TYPE_CHOICES = [(e.name, e.name.replace("_", " ").title()) for e in pa.EyebrowType]
    MOUTH_TYPE_CHOICES = [(m.name, m.name.replace("_", " ").title()) for m in pa.MouthType]
    ACCESSORY_CHOICES = [(a.name, a.name.replace("_", " ").title()) for a in pa.AccessoryType]

    hair_type = forms.ChoiceField(choices=HAIR_TYPE_CHOICES, required=False, label="Hair Type")
    hair_color = forms.ChoiceField(choices=HAIR_COLOR_CHOICES, required=False, label="Hair Color")
    skin_color = forms.ChoiceField(choices=SKIN_COLOR_CHOICES, required=False, label="Skin Color")
    clothing_type = forms.ChoiceField(choices=CLOTHING_TYPE_CHOICES, required=False, label="Clothing Type")
    clothing_color = forms.ChoiceField(choices=CLOTHING_COLOR_CHOICES, required=False, label="Clothing Color")
    facial_hair = forms.ChoiceField(choices=FACIAL_HAIR_CHOICES, required=False, label="Facial Hair")
    eyes = forms.ChoiceField(choices=EYE_TYPE_CHOICES, required=False, label="Eye Type")
    eyebrows = forms.ChoiceField(choices=EYEBROW_TYPE_CHOICES, required=False, label="Eyebrow Type")
    mouth = forms.ChoiceField(choices=MOUTH_TYPE_CHOICES, required=False, label="Mouth Type")
    accessory = forms.ChoiceField(choices=ACCESSORY_CHOICES, required=False, label="Accessory")
    shirt_text = forms.CharField(max_length=20, required=False, help_text="Optional text on shirt")

    class Meta:
        model = Profile
        fields = [
            'avatar', 
            'hair_type', 'hair_color', 'skin_color', 'clothing_type',
            'clothing_color', 'facial_hair', 'eyes', 'eyebrows',
            'mouth', 'accessory', 'shirt_text'
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'school',
            'age',
            'avatar',
            'pip_quote'
        ]

        widgets = {
            'avatar': forms.ClearableFileInput(),
        }
