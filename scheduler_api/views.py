from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import InterviewForm
from .models import User, Candidate, Client, Interview
from django.utils import timezone
from datetime import datetime, time
import zoneinfo



                


def user_specific_view(request):
    '''
        Renders a template based on user-type
    '''

    #print(user_type)
    user = request.user
    print(user)
    
    if(user.type == "CLIENT"):
        form = InterviewForm()
        template_name = "scheduler_api/scheduler.html"
        return render(request, template_name, {'form': form})
        
    else:
        template_name = "scheduler_api/list_interviews.html"
        candidate_obj = get_object_or_404(Candidate, username=user.username)
        interviews = Interview.objects.filter(candidate=candidate_obj)
        context = {
            'candidate_name': user.username,
            'interviews' : interviews
        }
        return render(request, template_name, context)
    
    


def candidate_view(request):

    '''
        Renders the html which displays the list of interviews scheduled and the selected interview details 
        such as client, Time slot in IST, Options to 'accept' or 'reschedule' the time slot for the given candidate

    '''
    selected_interview = None

    #candidate_obj = get_object_or_404(Candidate, username=candidate_name)
    #interviews = Interview.objects.filter(candidate=candidate_obj)
    
    #gets the selected interview obj 
    if request.method == 'POST':
        selected_id = request.POST.get('object_id')
        if selected_id:
            selected_interview = Interview.objects.get(pk=selected_id)
            print("In selected obj: ", selected_interview)
            ist_datetime = localize_to_ist(selected_interview.date, selected_interview.time, selected_interview.time_zone)
            print("ist_datetime: ", ist_datetime)
            context = {
                    'selected_interview': selected_interview,
                    'client': selected_interview.client.username,
                    'scheduled_date': ist_datetime.date(),
                    'scheduled_time': ist_datetime.time()
                }
            
            return render(request, 'scheduler_api/candidate.html', context)

    return HttpResponse("No interviews Found!")       
    


def schedule_interview(request):
     
     '''
        Renders the InterviewForm to the client to initiate the scheduling;
        Converts the client timezone to Candidate timezone - IST and checks whether the selected time slot falls between 6am IST to 10pm IST
        Once the condition met, the interview object has been created & saved with the status - Pending
        Else, re-renders the form with the error message

    '''
     
     client_name = request.user.username
     print("client name : ", client_name)
     
     if request.method == 'POST':
        form = InterviewForm(request.POST)

        if form.is_valid():
            candidate_name = form.cleaned_data['candidate']  
            slot_date = form.cleaned_data['date']
            slot_time = form.cleaned_data['time']
            slot_time_zone = form.cleaned_data['time_zone']

            # retrieving the candidate and client object 
            candidate_obj= Candidate.objects.get(username=candidate_name)
            client_obj = Client.objects.get(username=client_name)
            print(candidate_name)
            print(client_name)

            # converts to IST timezone
            ist_datetime = localize_to_ist(slot_date, slot_time, slot_time_zone)
            ist_time = ist_datetime.time()
            print("Time slot in IST ", ist_time)

            # checks whether the IST time slot falls between 6am to 10pm 
            if(is_valid_ist_hour(ist_time)):
                interview_slot = Interview.objects.create(candidate=candidate_obj, client=client_obj, date=slot_date, time=slot_time, time_zone=slot_time_zone)
                interview_slot.save()
                return HttpResponse(str(interview_slot))
            
            else:
                form.add_error(None, "Please select different Time slot as this falls this out of working hours in IST" )
                return render(request, 'scheduler_api/scheduler.html', {'form': form})
                
     else:
        form = InterviewForm()
        return render(request, 'scheduler_api/scheduler.html', {'form': form})


def handle_confirmation(request):

    '''
        Triggers when the candidate clicks 'Accept' in the candidate view page

    '''
    if request.method == 'POST':
        obj_id = request.POST.get('accept_obj')
        interview_obj = Interview.objects.get(pk=obj_id)
    
        if(interview_obj.status == 'accepted'):
            return HttpResponse("Your Interview slot has already been accepted")

        interview_obj.status = 'accepted'
        interview_obj.save()
        return HttpResponse("Your Interview slot is confirmed.")  

    return HttpResponse("No interview found")
    
    
def handle_rescheduling(request):

    '''
        Triggers when the candidate clicks 'Reschedule' in the candidate view page

    '''
    if request.method == 'POST':
        obj_id = request.POST.get('reschedule_obj')
        interview_obj = Interview.objects.get(pk=obj_id)

        if(interview_obj.status == 'rescheduled'):
            return HttpResponse("Your reschedule request has already been sent")
    
        interview_obj.status = 'rescheduled'
        interview_obj.save()
        return HttpResponse("Your Interview slot is requested for Rescheduling.")

    return HttpResponse("No Interview found")
    

   
def localize_to_ist(date, time, time_zone):

    '''
        Performs Time zone conversion and returns IST datetime

    '''
    
    slot_datetime = datetime.combine(date, time)    #combine data and time to datetime object

    # get timezone aware datetime object 
    localized_datetime = timezone.make_aware(slot_datetime, zoneinfo.ZoneInfo(time_zone))

    # localize to IST timezone
    IST = zoneinfo.ZoneInfo('Asia/Kolkata')
    ist_datetime = localized_datetime.astimezone(IST)

    return ist_datetime


def is_valid_ist_hour(ist_time):

    '''
        Performs Time Validation check

    '''
    start_time = time(6,00)
    end_time = time(22,00)

    if(ist_time >= start_time and ist_time <= end_time):
        return True 

    return False