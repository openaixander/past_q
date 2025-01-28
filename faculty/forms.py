from django import forms
from .models import Department, Level, Semester, Session, Course,PastQuestion, Image, StudyMaterial
from django.core.validators import FileExtensionValidator
from django.forms import ClearableFileInput


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class PastQuestionForm(forms.ModelForm):

    department = forms.ModelChoiceField(
        required=True,
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )

    level = forms.ModelChoiceField(
        required=True,
        queryset=Level.objects.all(),
        empty_label="Select Level",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )

    semester = forms.ModelChoiceField(
        required=True,
        queryset=Semester.objects.all(),
        empty_label="Select Semester",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )

    course = forms.ModelChoiceField(
        required=True,
        queryset=Course.objects.all(),
        empty_label="Select Course",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )
    year = forms.ModelChoiceField(
        required=True,
        queryset=Session.objects.all(),
        empty_label="Select Session",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )

    course_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'readonly':'readonly'
            }
        )
    )

    # file = forms.FileField(
    #     validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    #     widget=forms.FileInput(attrs={'accept': '.pdf'})
    # )

    images = MultipleFileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])
        ]
    )


    class Meta:
        model = PastQuestion
        fields = ['course', 'year']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.none()

        if 'department' in self.data and 'level' in self.data and 'semester' in self.data:
            try:
                department_id = int(self.data.get('department'))
                level_id = int(self.data.get('level'))
                semester_id = int(self.data.get('semester'))
                self.fields['course'].queryset = Course.objects.filter(
                    departments__id=department_id,
                    levels__id=level_id,
                    semesters__id=semester_id
                ).distinct()
            except (ValueError, TypeError):
                pass
    
    
    def clean_images(self):
        images = self.files.getlist('images')
        if not images:
            raise forms.ValidationError("At least one image is required.")
        return images
    
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            for index, image in enumerate(self.files.getlist('images'), start=1):
                Image.objects.create(
                    past_question=instance,
                    image=image,
                    page_number=index
                )
        return instance

    
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        if course:
            cleaned_data['course_code'] = course.code

    


class StudyMaterialForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    level = forms.ModelChoiceField(
        queryset=Level.objects.all(),
        empty_label="Select Level",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        empty_label="Select Semester",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), 
        empty_label="Select Course",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    year = forms.ModelChoiceField(
        required=True,
        queryset=Session.objects.all(),
        empty_label="Select Session",
        widget=forms.Select(
            attrs={
                'class':'form-control'
            }
        )
    )

    material_type = forms.ChoiceField(
        choices=StudyMaterial.MATERIAL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # files = MultipleFileField(
    #     validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])],
    #     widget=forms.FileInput(attrs={'multiple': True, 'class': 'form-control'})
    # )

    class Meta:
        model = StudyMaterial
        fields = ['title', 'material_type','year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.none()

        if 'department' in self.data and 'level' in self.data and 'semester' in self.data:
            try:
                department_id = int(self.data.get('department'))
                level_id = int(self.data.get('level'))
                semester_id = int(self.data.get('semester'))
                self.fields['course'].queryset = Course.objects.filter(
                    departments__id=department_id,
                    levels__id=level_id,
                    semesters__id=semester_id
                ).distinct()
            except (ValueError, TypeError):
                pass