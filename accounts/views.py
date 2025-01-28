from django.shortcuts import render, redirect
from .forms import AccountForm, LecturerProfileForm
from .models import Account

from .utils import send_activation_link, send_reset_password_link, decode_uid

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import password_validation
# from django.http import HttpResponse
# what i need for the email activation
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages, auth
from django.contrib.auth import authenticate


# from forms import regist
# Create your views here.


def register(request):
    # this is where the submission of the form happens
    
    # checks if the request method is actually a post or get request
    if request.method != 'POST':
        # if the request is not a post request, well just render the form again
        form = AccountForm()
    
    else:
        # If yes, the request method is actually a 'POST' request, we then collect the data
        # and save the data in the database.
        form = AccountForm(data=request.POST)
        # we now check if the form is valid
        if form.is_valid():
            # remember, we need to map the password and confirm_password to the database
            try:
                full_name = form.cleaned_data['full_name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                is_lecturer = form.cleaned_data['user_type']
                

                username = email.split('@')[0]

                # create the user account normally
                user = Account.objects.create_user(
                    full_name=full_name,
                    email=email,
                    username=username,
                    password=password,
                )
                # Once the user account has been created,
                # we set some fields to True or False, depends on how the form was submitted
                user.is_active = False
                # this here is either True or False
                user.is_lecturer = is_lecturer
                user.is_student = not is_lecturer  # Set is_student opposite to is_lecturer
                user.save()

                # since this has been saved, we now move to check if the user clicked on the is_lecturer checkbox

                if user.is_lecturer:
                    # keep the user id in a session, which will be used to be retrieved later
                    request.session['pending_lecturer_id'] = user.id
                    return redirect('accounts:lecturer_info')
                
                else:
                    # send activation link to the student account
                    send_activation_link(request, user, email)
                    messages.success(request, 'Please check your email to activate your student account.')
                    return redirect('/accounts/login/?command=verification&email='+email)
                    # return redirect('accounts:register')
                
            except Exception:
                messages.error(request, 'An error occurred during registration.')
                return redirect('accounts:register')
    context = {
        'form':form
    }
    return render(request, 'accounts/registration.html', context)


# this is the lecturer_info

def lecturer_info(request):
    # checks if user id is not in session
    if 'pending_lecturer_id' not in request.session:
        messages.error(request, 'Account does not exist')
        return redirect('accounts:register')
    

    # time to get the user_id from the database
    user = Account.objects.get(id=request.session['pending_lecturer_id'])

    # checks and see if the request method is not a post request
    if request.method != 'POST':
        form = LecturerProfileForm()
    
    else:
        form = LecturerProfileForm(request.POST, request.FILES)
        # checks if form is valid
        if form.is_valid:
            try:
                # do not save the form in the database yet, 
                # we have to look for the user in the database, then assign it
                lecturer_profile = form.save(commit=False)
                # the user submits this form, this data will be assign to them
                lecturer_profile.user = user
                lecturer_profile.save()

                email = user.email
                send_activation_link(request, user, email)

                # delete the session 
                del request.session['pending_lecturer_id']

                return redirect('/accounts/login/?command=verification&email='+email)
            
            except Exception as e:
                pass
    context = {
        'form': form
    }

    return render(request, 'accounts/lecturer_verification.html', context)


def activate(request, uidb64, token):
    # Now, it is time to activate the user account.
    """
    Activate the user account using the provided UID, token.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): The base64 encoded UID.
        token (str): The activation token.

    Returns:
        HttpResponseRedirect: Redirects to the appropriate page after activation.
    """
    try:
        uid = decode_uid(uidb64)
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is None:
        messages.error(request, 'Invalid activation link: User does not exist.')
        return redirect('accounts:register')
    
    if user.is_active:
        messages.warning(request, 'Your account has already been activated.')
        return redirect('accounts:login')
        # return redirect('accounts:register')
    
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()


        if user.is_lecturer:
            return redirect('accounts:lecturer_waiting')
        else: #student account
            messages.success(request, 'Congratulations! Your account has been activated.')
            return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link: The token is invalid')
        return redirect('accounts:register')
    


def lecturer_waiting(request):
    return render(request, 'accounts/lecturer_waiting.html')




def login(request):
 # Get the next URL if it exists (for quiz redirects)
    next_url = request.GET.get('next', '') or request.POST.get('next', '')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_active:
                    # Check if the user is a student for quiz access
                    if next_url and next_url.startswith('/quiz/') and not user.is_student:
                        messages.error(request, 'Only students can access quizzes.')
                        return redirect('accounts:login')

                    auth.login(request, user)
                    
                    # Redirect to next_url if it exists and is safe
                    if next_url and not next_url.startswith('http'):
                        return redirect(next_url)
                    
                    # Otherwise, redirect based on user type
                    if user.is_lecturer and user.is_approved:
                        return redirect('faculty:lecturer_dashboard')
                    elif user.is_student:
                        return redirect('faculty:student_dashboard')
                    else:
                        messages.info(request, 'Your account type is not recognized or not approved.')
                else:
                    messages.error(request, 'Your account is not active. Please check your email for activation instructions.')
            else:
                messages.error(request, 'Invalid email or password.')

        except Account.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

    # Pass next_url to the template
    context = {'next': next_url} if next_url else {}
    return render(request, 'accounts/login.html', context)


@login_required
def logout(request):
    auth.logout(request)
    messages.info(request, f'You have logged out. Visit us again.')
    return redirect('accounts:login')

def forgot_password(request):
    # first, we need to check if the request sent is POST request.
    if request.method == 'POST':
        # now get the email that has been submitted that wants to reset it password
        email = request.POST.get('email')
        # Now, we need to check if the email truly exist in the database

        if Account.objects.filter(email=email).exists():
            # if it exists, we need to be sure that the correct email is being returned
            user = Account.objects.get(email__exact=email)

            # now we send the email to the user
            send_reset_password_link(request, user, email)
            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('accounts:login')
        
        #  if the user doesn't exist, then send them a message to notify them
        else:
            messages.error(request, 'User does not exist!')
            return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    """
    Validate the password reset link.
    Args:
    request (HttpRequest): The HTTP request object.
    uidb64 (str): The base64 encoded UID of the user.
    token (str): The password reset token.
    Returns:
    HttpResponse: Redirects to the appropriate page based on validation results.
    """
    try:
        uid = decode_uid(uidb64)
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is None:
        messages.error(request, 'Invalid password reset link: User does not exist.')
        return redirect('accounts:forgot_password')

    if user.password_reset_used:
        messages.warning(request, 'This password reset link has already been used.')
        return redirect('accounts:forgot_password')

    if default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        user.password_reset_used = True
        user.save()
        messages.info(request, 'Please reset your password.')
        return redirect('accounts:reset_password')
    else:
        messages.error(request, 'This password reset link is invalid or has expired!')
        return redirect('accounts:forgot_password')
    

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:reset_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('accounts:reset_password')

        try:

            uid = request.session.get('uid')
            #value error: an exception that occurs when a function receives an argument of the correct data type but an inappropriate value.
            # if user is not in session, then raise a ValueError
            if not uid:
                raise ValueError("User ID not found in session")

            user = Account.objects.get(pk=uid)

            # Check if the new password is the same as the old password
            if user.check_password(password):
                messages.error(request, 'New password must be different from the old password.')
                return redirect('accounts:reset_password')

            # Validate the password using Django's password validation
            try:
                password_validation.validate_password(password, user)
            except password_validation.ValidationError as e:
                messages.error(request, '\n'.join(e.messages))
                return redirect('accounts:reset_password')

            user.set_password(password)
            user.password_reset_used = False
            user.save()

            del request.session['uid']

            messages.success(request, 'Password reset successful. You can now login with your new password.')
            return redirect('accounts:login')

        except (Account.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error resetting password: {str(e)}')
            return redirect('accounts:forgot_password')

    return render(request, 'accounts/reset_password.html')