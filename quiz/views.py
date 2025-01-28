from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from faculty.decorator import student_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from faculty.models import Department, Level, Semester
from .models import Quiz, QuizAttempt, QuizResponse, Question, Choice
# Create your views here.



def quiz_list(request):
     # Get filter parameters
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    # Start with all active quizzes
    quizzes = Quiz.objects.filter(is_active=True)
    
    # Apply filters if they exist
    if department_id:
        quizzes = quizzes.filter(departments__id=department_id)
    if level_id:
        quizzes = quizzes.filter(levels__id=level_id)
    if semester_id:
        quizzes = quizzes.filter(semesters__id=semester_id)
    
    # Get unique values for filters
    departments = Department.objects.filter(quiz__in=quizzes).distinct()
    levels = Level.objects.filter(quiz__in=quizzes).distinct()
    semesters = Semester.objects.filter(quiz__in=quizzes).distinct()
    
    context = {
        'quizzes': quizzes,
        'departments': departments,
        'levels': levels,
        'semesters': semesters,
    }
    return render(request, 'quiz/quizzes.html', context)


@login_required(login_url='/accounts/login/')
@student_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if there's an incomplete attempt
    existing_attempt = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        completed=False
    ).first()
    
    if existing_attempt:
        # Resume existing attempt
        attempt = existing_attempt
    else:
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz
        )
    
    return redirect('quiz:take_quiz', attempt_id=attempt.id)


@login_required
@student_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.completed:
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    if request.method == 'POST':
        # Process quiz submission
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                choice_id = int(value)
                
                question = get_object_or_404(Question, id=question_id)
                choice = get_object_or_404(Choice, id=choice_id)
                
                # Save response
                QuizResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_choice=choice,
                    is_correct=choice.is_correct
                )
        
        # Calculate score
        total_questions = attempt.quiz.questions.count()
        correct_answers = attempt.responses.filter(is_correct=True).count()
        attempt.score = (correct_answers / total_questions) * 100
        attempt.end_time = timezone.now()
        attempt.completed = True
        attempt.save()
        
        return redirect('quiz:quiz_result', attempt_id=attempt.id)
    
    # Get questions for this quiz
    questions = attempt.quiz.questions.all().prefetch_related('choices')
    
    context = {
        'attempt': attempt,
        'questions': questions,
    }
    return render(request, 'quiz/take_quiz.html', context)


@login_required
@student_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if not attempt.completed:
        return redirect('quiz:take_quiz', attempt_id=attempt.id)
    
    context = {
        'attempt': attempt,
        'responses': attempt.responses.all(),
        'passed': attempt.score >= attempt.quiz.passing_score,
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required
@student_required
def load_quiz_filters(request):
    department_id = request.GET.get('department')
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    quizzes = Quiz.objects.filter(is_active=True)
    
    if department_id:
        quizzes = quizzes.filter(departments__id=department_id)
    if level_id:
        quizzes = quizzes.filter(levels__id=level_id)
    if semester_id:
        quizzes = quizzes.filter(semesters__id=semester_id)
    
    quiz_data = list(quizzes.values('id', 'title', 'duration_minutes', 'total_questions', 
                                   'course__code', 'course__name'))
    return JsonResponse(quiz_data, safe=False)

