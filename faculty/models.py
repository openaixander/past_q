from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from cloudinary.models import CloudinaryField
# Create your models here.

class StudentDashboardCard(models.Model):
    ICON_CHOICES = [
        ('book-open', 'book-open'),
        ('tasks', 'tasks'),
        ('chart-line', 'chart-line'),
        ('download', 'download'),
    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    action_text = models.CharField(max_length=50)
    url_name = models.CharField(max_length=200, help_text="Name of the URL pattern for this action")
    order = models.IntegerField(default=0)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    def get_absolute_url(self):
        return reverse(f"faculty:{self.url_name}")


class LecturerDashboardCard(models.Model):
    ICON_CHOICES = [
        ('file-upload', 'file-upload'),
        ('book', 'book'),
        ('edit', 'edit'),
        ('chart-line', 'chart-line'),

    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    action_text = models.CharField(max_length=50)
    url_name = models.CharField(max_length=200, help_text="Name of the URL pattern for this action")
    order = models.IntegerField(default=0)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    def get_absolute_url(self):
        return reverse(f"faculty:{self.url_name}")
        
    

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name
    
class Level(models.Model):
    value = models.IntegerField(unique=True)
    departments = models.ManyToManyField(Department)


    def __str__(self) -> str:
        return f"Level {self.value}"
    

class Semester(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.name
    
class Session(models.Model):
    value = models.CharField(max_length=20,unique=True)

    def __str__(self):
        return str(self.value)
    
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    departments = models.ManyToManyField(Department)
    levels = models.ManyToManyField(Level)
    semesters = models.ManyToManyField(Semester)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class PastQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.ForeignKey(Session, on_delete=models.CASCADE)
    # file = models.FileField(
    #     upload_to='past_questions/',
    #     validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    # )

    def __str__(self):
        return f"{self.course} - {self.year}"




class Image(models.Model):
    past_question = models.ForeignKey(PastQuestion, related_name='images', on_delete=models.CASCADE)
    # Replace ImageField with CloudinaryField
    image = CloudinaryField('image', 
                          folder='past_question_images/',  # Maintains your folder structure
                          resource_type='image')
    page_number = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['page_number']

    def __str__(self):
        return f"Image {self.page_number} for {self.past_question}"
    

class StudyMaterial(models.Model):
    MATERIAL_TYPES = [
        ('lecture_notes','Lecture Notes'),
        ('slides', 'Slides'),
        ('textbook','Textbook'),
        ('other','Other'),
    ]


    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=200,blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    files = CloudinaryField('files',
                          folder='study_materials/',
                          resource_type='raw',  # Changed from 'raw' to 'auto'
                          allowed_formats=['pdf', 'doc', 'docx', 'ppt', 'pptx'])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def get_file_info(self):
    """Get comprehensive file information from Cloudinary"""
        try:
            if self.files:
                resource = cloudinary.api.resource(self.files.public_id)
                return {
                    'size': resource.get('bytes', 0),
                    'format': resource.get('format', ''),
                    'original_filename': resource.get('original_filename', ''),
                    'secure_url': resource.get('secure_url', ''),
                    'created_at': resource.get('created_at', '')
                }
            return None
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None

    def get_formatted_size(self):
        """Return human-readable file size"""
        file_info = self.get_file_info()
        if file_info and 'size' in file_info:
            bytes_size = file_info['size']
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024
            return f"{bytes_size:.1f} GB"
        return "Size unknown"
    
    def get_original_filename(self):
        """Get the original filename"""
        file_info = self.get_file_info()
        if file_info and 'original_filename' in file_info:
            return file_info['original_filename']
        return "Unnamed file"

    def __str__(self):
        return f"{self.title} - {self.course}"
    

    class Meta:
        ordering = ['-uploaded_at']


