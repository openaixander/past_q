from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from cloudinary.models import CloudinaryField
# Create your models here.



class MyAccountManager(BaseUserManager):
    # this here represents the student creation account
    def create_user(self, full_name, username, email, password=None):
        # if the student doesn't provide an email, it should raise an error
        if not email:
            raise ValueError('User must have an email')
        
        # if the student doesn't provide a usename(which will be generated automatically), it should raise an error
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, full_name, username, email, password=None):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
            password=password
        )

        # this here are the permission of a superuser(which is the admin)
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True

        # save everything
        user.save(using=self._db)
        return user


#Since I am creating a custom user model, well, I need to inherit some stuff 
class Account(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(
        verbose_name='email',
        max_length=50,
        unique=True,
    )
    phone_number = models.CharField(max_length=50)

    # addtional fields for lecturers


    # overriding the default manager settings of django
    objects = MyAccountManager()

    # these here are the required fields, for user to create a custom user.
    # A flag should be created to distinguish between student and lecturer

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # this here is what I added, user account needs to activated before they can use the web app
    is_active = models.BooleanField(default=False)
    password_reset_used = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    is_lecturer = models.BooleanField(default=False)
    # this here is an additional security, which only the admin can approve an account belongs to the lecturer
    is_approved = models.BooleanField(default=False)

    # this here is what the user needs to sign into the admin panel
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'full_name',
    ]

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    

    @property
    def user_type(self):
        if self.is_lecturer:
            return 'lecturer'
        return 'student'

class LecturerProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='lecturer_profile')
    employee_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    faculty_position = models.CharField(max_length=20)
    office_number = models.CharField(max_length=50, blank=True, null=True)
    id_card = CloudinaryField('image', 
                          folder='id_cards/',  # Maintains your folder structure
                          resource_type='image')


    def __str__(self):
        return f"{self.user.full_name} - {self.faculty_position}"
    
