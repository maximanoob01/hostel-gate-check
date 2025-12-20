from django import forms
from .models import Student, LeaveRequest
from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "enrollment_number", 
            "full_name", 
            "course",          # New
            "year",            # New
            "photo",           # New
            "room_number", 
            "hostel_name", 
            "phone", 
            "guardian_name",   # New
            "emergency_phone", 
            "is_inside"
        ]
        
        # defining widgets to control how they look in HTML
        widgets = {
            "enrollment_number": forms.TextInput(attrs={
                "placeholder": "Enrollment Number", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "full_name": forms.TextInput(attrs={
                "placeholder": "Full name", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "course": forms.TextInput(attrs={
                "placeholder": "e.g. B.Tech CSE", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "year": forms.Select(attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "photo": forms.FileInput(attrs={
                "class": "hidden", # We hide this because we use a custom label in the HTML to trigger it
                "accept": "image/*"
            }),
            "room_number": forms.TextInput(attrs={
                "placeholder": "Room No.", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "hostel_name": forms.TextInput(attrs={
                "placeholder": "Hostel Name", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Student Phone", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "guardian_name": forms.TextInput(attrs={
                "placeholder": "Guardian Name", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "emergency_phone": forms.TextInput(attrs={
                "placeholder": "Emergency Contact", 
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            }),
            "is_inside": forms.CheckboxInput(attrs={
                "class": "h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            }),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "photo",
            "hostel_name",
            "room_number",
            "phone",
        ]

class CSVUploadForm(forms.Form):
    file = forms.FileField(
        help_text="Upload CSV with columns: enrollment_number, full_name, course, year, room_number, phone, hostel_name, guardian_name, emergency_phone",
        widget=forms.FileInput(attrs={
            "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
        })
    )

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["reason", "destination", "from_date", "to_date"]

        widgets = {
            "reason": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Enter reason for leave",
            }),
            "destination": forms.TextInput(attrs={
                "placeholder": "Enter destination",
            }),
            "from_date": forms.DateTimeInput(attrs={
                "type": "datetime-local",
            }),
            "to_date": forms.DateTimeInput(attrs={
                "type": "datetime-local",
            }),
        }