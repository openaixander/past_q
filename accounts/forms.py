from django import forms

from .models import Account, LecturerProfile


# this here is the account form for the lecturer and student
class AccountForm(forms.ModelForm):
    """
    This here list the form that will be submitted,
    and then saved in the database
    """
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                'class':'form-control',
                'id':'password',
                'placeholder':'Password',
            }
        ),
        required=True # This makes the field required (by default, fields are required)
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs= {
                'class':'form-control',
                'id':'confirmPassword',
                'placeholder':'Confirm Password',
            }
        ),
        required=True # This makes the field required (by default, fields are required)
    )

    user_type = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                'class':'form-check-input',
                'id':'userType',
            }
        ),
        required=False
    )

    class Meta:
        model = Account
        fields = [
            'full_name',
            'email',
            # 'phone_number',
        ]


    # Now, I am going to style these model fields
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        # this here styles those model fields in the front end
        self.fields['full_name'].widget.attrs['class']='form-control'
        self.fields['email'].widget.attrs['class']='form-control'

        self.fields['full_name'].widget.attrs['placeholder']='Full Name'
        self.fields['email'].widget.attrs['placeholder']='Email Address'


        # for field in self.fields:
        #     self.fields[field].widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super(AccountForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')


        if len(password) < 8:
            raise forms.ValidationError('Password must be atleast 8 characters long.')
        
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match. Please enter the same password in both fields.')


class LecturerProfileForm(forms.ModelForm):

    class Meta:
        model = LecturerProfile
        fields = [
            'employee_id',
            'department',
            'faculty_position',
            'office_number',
            'id_card',
        ]

    def __init__(self, *args, **kwargs):
        super(LecturerProfileForm, self).__init__(*args, **kwargs)


        self.fields['employee_id'].widget.attrs['placeholder'] = 'Employee ID'
        self.fields['department'].widget.attrs['placeholder'] = 'Department'
        self.fields['faculty_position'].widget.attrs['placeholder'] = 'Faculty Position'
        self.fields['office_number'].widget.attrs['placeholder'] = 'Office Number'
        self.fields['id_card'].widget.attrs['id'] = 'idCard'
        self.fields['id_card'].widget.attrs['accept'] = 'image/*'
    
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'