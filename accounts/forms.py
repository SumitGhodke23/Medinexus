from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from patients.models import Patients


class PatientSignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, label="Full name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=15, required=False, label="Phone")
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label="Date of birth")
    gender = forms.CharField(max_length=20, required=False, label="Gender")
    blood_group = forms.CharField(max_length=5, required=False, label="Blood group")
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Address")

    class Meta:
        model = User
        fields = ("username", "full_name", "email", "phone", "date_of_birth", "gender", "blood_group", "address", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Please use Patient Login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Patients.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"].strip(),
                email=self.cleaned_data["email"],
                phone=self.cleaned_data.get("phone", "").strip(),
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                gender=self.cleaned_data.get("gender", "").strip(),
                blood_group=self.cleaned_data.get("blood_group", "").strip(),
                address=self.cleaned_data.get("address", "").strip(),
            )
        return user