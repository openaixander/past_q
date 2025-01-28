from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from zipfile import ZipFile
from .decorator import approved_lecturer_required
from django.core.serializers import serialize
# from django.contrib import messages
from accounts.models import LecturerProfile
from django.contrib import messages
from .models import StudentDashboardCard, LecturerDashboardCard, Department, Level, Semester, Course, Session, PastQuestion, StudyMaterial
from .forms import PastQuestionForm, StudyMaterialForm
import os
import cloudinary.uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from io import BytesIO
import requests
# Create your views here.


def index(request):
    # this is the welcome page of the past question application
    return render(request, 'faculty/index.html')

def choice(request):
    return render(request, 'faculty/choice.html')

def about_pastq(request):
    return render(request, 'faculty/about_pastq.html')


def student_dashboard(request):
    cards = StudentDashboardCard.objects.all()
    context = {
        'cards':cards
    }
    return render(request, 'faculty/student_dashboard.html', context)



def view_or_download_pastq(request):
    # Fetch all departments, levels, semesters, and years
    departments = Department.objects.all()
    levels = Level.objects.all()
    semesters = Semester.objects.all()
    sessions = Session.objects.all().order_by('-value')  # Newest years first

    # Initialize courses queryset
    courses = Course.objects.none()

    # Check if form data is submitted
    if request.method == 'POST':
        department_id = request.POST.get('department')
        level_id = request.POST.get('level')
        semester_id = request.POST.get('semester')

        # Filter courses based on selected criteria
        courses = Course.objects.filter(
            departments__id=department_id,
            levels__id=level_id,
            semesters__id=semester_id
        )

        # If it's an AJAX request, return filtered courses as JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            courses_data = serialize('json', courses, fields=('id', 'code', 'name'))
            return JsonResponse({'courses': courses_data})

    # Serialize all courses for initial page load
    all_courses_json = serialize('json', Course.objects.all(), fields=('id', 'code', 'name'))

    context = {
        'departments': departments,
        'levels': levels,
        'semesters': semesters,
        'years': sessions,
        'courses': courses,
        'all_courses_json': all_courses_json,
    }

    return render(request, 'faculty/view_or_download_pastq.html', context)

def process_past_question_form(request):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        year_id = request.POST.get('year')
        
        # Debug print statements
        # print(f"Received course_id: {course_id}, year_id: {year_id}")

        try:
            course = Course.objects.get(id=course_id)
            year = Session.objects.get(id=year_id)  # Change this line
            
            # Debug print statements
            print(f"Found course: {course}, year: {year}")

            past_question = PastQuestion.objects.filter(course=course, year=year).first()
            
            if past_question:
                return redirect(reverse('faculty:view_past_question', kwargs={'pk': past_question.pk}))
            else:
                # Show that pastq does not exist
                return render(request, 'faculty/no_past_question_found.html', {'course': course, 'year': year})
        
        except Course.DoesNotExist:
            print(f"Course with id {course_id} does not exist")
            return render(request, 'faculty/error.html', {'message': 'Selected course does not exist.'})
        
        except Session.DoesNotExist:
            print(f"Session with id {year_id} does not exist")
            return render(request, 'faculty/error.html', {'message': 'Selected year does not exist.'})
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return render(request, 'faculty/error.html', {'message': 'An unexpected error occurred.'})

    # If not POST, redirect to the form page
    return redirect('faculty:view_or_download_pastq')


def view_past_question(request, pk):
    past_question = get_object_or_404(PastQuestion, pk=pk)

    context = {
        'past_question':past_question
    }
    return render(request, 'faculty/view_past_question.html', context)

def download_pastq_images(request, pk):
    """Download all images for a past question as a zip file"""
    past_question = get_object_or_404(PastQuestion, pk=pk)
    images = past_question.images.all()

    if not images:
        raise Http404("No images available for download")

    # Create a zip file in memory
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for image in images:
            if image.image:
                # Download from Cloudinary
                response = cloudinary.api.resource(image.image.public_id)
                image_url = response['secure_url']
                image_content = requests.get(image_url).content
                
                # Add to zip with proper filename
                filename = f"page_{image.page_number}{os.path.splitext(image.image.public_id)[1]}"
                zip_file.writestr(filename, image_content)

    # Prepare the response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{past_question.course.code}_pastq_{past_question.year.value}.zip"'
    
    return response

def no_past_question_found(request):
    return render(request, 'faculty/no_past_question_found.html')


def download_materials(request):
    # this has the same logic as the view_or_download_pastq function
    # we need to fetch all the instances made in the database for the faculty
    departments = Department.objects.all()
    levels = Level.objects.all()
    semesters = Semester.objects.all()
    sessions = Session.objects.all().order_by('-value') #newer sessions first will show

    # Let query the course table
    courses = Course.objects.none()


    # we now check if the data being queried by the user is a post request
    if request.method == 'POST':
        # we now initialize whatever data the user submitted and then equate it to the variables below
        department_id = request.POST.get('department')
        level_id = request.POST.get('level')
        semester_id = request.POST.get('semester')

        # filter courses based on the selected criteria. If department>level 1>first_semester, then let it just show those courses related to these selected criteria
        courses = Course.objects.filter(
            # these are fields in the db and then we are equating them to the form data we recieved from the user
            departments__id=department_id,
            levels__id=level_id,
            semesters__id=semester_id
        )

        # here we use AJAX to dynamically get the related data from the data base
        # then it shows related data without refreshing the page

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            courses_data = serialize('json', courses, fields=('id', 'code', 'name'))
            return JsonResponse({'courses': courses_data})
        
    all_courses_json = serialize('json', Course.objects.all(), fields=('id', 'code', 'name'))

    context = {
    'departments': departments,
    'levels': levels,
    'semesters': semesters,
    'years': sessions,
    'courses': courses,
    'all_courses_json': all_courses_json,
    }
    
    return render(request, 'faculty/download_materials.html', context)

def process_materials(request):
    # Here, data will be submitted to this view function and it will perform the data manipulation here
    if request.method == 'POST':
        course_id = request.POST.get('course')
        year_id = request.POST.get('year')

        try:
            course = Course.objects.get(id=course_id)
            year = Session.objects.get(id=year_id)

            material = StudyMaterial.objects.filter(course=course, year=year).first()

            if material:
                return redirect(reverse('faculty:download_study_materials', kwargs={'pk':material.pk}))
            else:
                # if it does not exist, tell the user it doesn't exist
                return render(request, 'faculty/no_download_materials_found.html', {'course': course, 'year':year})
        except Course.DoesNotExist:
            # print(f"Course with id {course_id} does not exist")
            return render(request, 'faculty/error.html', {'message': 'Selected course does not exist.'})
        
        except Session.DoesNotExist:
            print(f"Session with id {year_id} does not exist")
            # return render(request, 'faculty/error.html', {'message': 'Selected year does not exist.'})
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            # return render(request, 'faculty/error.html', {'message': 'An unexpected error occurred.'})

    # If not POST, redirect to the form page
    return redirect('faculty:download_materials')


def download_study_materials(request, pk):
    material = get_object_or_404(StudyMaterial, pk=pk)
    
    # Fetch all study materials for the same course and year
    study_materials = StudyMaterial.objects.filter(
        course=material.course, 
        year=material.year
    )

    context = {
        'material': material,
        'study_materials': study_materials
    }
    return render(request, 'faculty/download_study_materials.html', context)


def download_file(request, pk):
    """Download a single study material file"""
    material = get_object_or_404(StudyMaterial, pk=pk)
    
    try:
        # Get the Cloudinary resource
        response = cloudinary.api.resource(material.files.public_id)
        file_url = response['secure_url']
        
        # Stream the file from Cloudinary
        file_response = requests.get(file_url)
        
        # Prepare the response
        response = HttpResponse(file_response.content, content_type=file_response.headers['Content-Type'])
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(material.files.public_id)}"'
        return response
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        raise Http404("File not found")

def download_multiple_files(request, pk):
    """Download all materials for a specific course and year as a zip"""
    material = get_object_or_404(StudyMaterial, pk=pk)
    
    # Get all materials for this course and year
    study_materials = StudyMaterial.objects.filter(
        course=material.course, 
        year=material.year
    )
    
    # Create a zip file in memory
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for mat in study_materials:
            if mat.files:
                # Download from Cloudinary
                response = cloudinary.api.resource(mat.files.public_id)
                file_url = response['secure_url']
                file_content = requests.get(file_url).content
                
                # Add to zip with proper filename
                filename = os.path.basename(mat.files.public_id)
                zip_file.writestr(filename, file_content)

    # Prepare the response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{material.course.code}_materials.zip"'
    
    return response

def no_download_materials_found(request):
    return render(request, 'faculty/no_download_materials_found.html')



# This here is LECTURER LOGIC VIEW

# this decorator checks to see if the current user is a lecturer before they can be given access
@approved_lecturer_required
def lecturer_dashboard(request):
    user = request.user
    lecturer_profile = get_object_or_404(LecturerProfile, user=user)
    cards = LecturerDashboardCard.objects.all()


    context = {
        'lecturer_profile':lecturer_profile,
        'cards': cards
    }
    return render(request, 'faculty/lecturer_dashboard.html', context)


@approved_lecturer_required
def upload_pastq(request):
    if request.method == 'POST':
        form = PastQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Past questions uploaded successfully!')
            return redirect('faculty:lecturer_dashboard')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, 'Error uploading files. Please check the form.')
    else:
        form = PastQuestionForm()

    return render(request, 'faculty/upload_pastq.html', {'form': form})

@approved_lecturer_required
def load_courses(request):
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    courses = Course.objects.filter(
        departments__id=department_id,
        levels__id=level_id,
        semesters__id=semester_id
    ).distinct()
    
    # Debug information
    # print(f"Department: {department_id}, Level: {level_id}, Semester: {semester_id}")
    # print(f"Number of courses found: {courses.count()}")
    
    course_data = list(courses.values('id', 'name', 'code'))
    return JsonResponse(course_data, safe=False)



@approved_lecturer_required
def upload_study_material(request):
    if request.method == 'POST':
        # Create a form without the files field
        form = StudyMaterialForm(request.POST)
        
        # Manually validate the form (excluding files)
        if form.is_valid():
            department_id = request.POST.get('department')
            level_id = request.POST.get('level')
            semester_id = request.POST.get('semester')
            course_id = request.POST.get('course')
            
            try:
                course = Course.objects.get(
                    id=course_id,
                    departments__id=department_id,
                    levels__id=level_id,
                    semesters__id=semester_id
                )
                
                # Manually get files
                files = request.FILES.getlist('files')
                
                # Validate file types manually
                valid_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx']
                valid_files = []
                
                for file in files:
                    ext = file.name.split('.')[-1].lower()
                    if ext in valid_extensions:
                        valid_files.append(file)
                    else:
                        messages.error(request, f'Invalid file type for {file.name}')
                
                # Create StudyMaterial instances for valid files
                study_materials = []
                for uploaded_file in valid_files:
                    study_material = StudyMaterial.objects.create(
                        course=course,
                        title=form.cleaned_data['title'],
                        material_type=form.cleaned_data['material_type'],
                        year=form.cleaned_data['year'],
                        files=uploaded_file,
                    )
                    study_materials.append(study_material)
                
                if study_materials:
                    messages.success(request, f'{len(study_materials)} study material(s) uploaded successfully!')
                    return redirect('faculty:lecturer_dashboard')
                else:
                    messages.error(request, 'No valid files were uploaded.')
            
            except Course.DoesNotExist:
                messages.error(request, 'Selected course does not exist.')
        else:
            # Print form errors for debugging
            print(form.errors)
    
    else:
        form = StudyMaterialForm()

    context = {
        'form': form,
        'departments': Department.objects.all(),
        'levels': Level.objects.all(),
        'semesters': Semester.objects.all(),
    }
    return render(request, 'faculty/upload_study_materials.html', context)


# This view handles dynamic course loading
def load_courses_for_material(request):
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    courses = Course.objects.filter(
        departments__id=department_id,
        levels__id=level_id,
        semesters__id=semester_id
    ).distinct()
    
    return JsonResponse(list(courses.values('id', 'code', 'name')), safe=False)