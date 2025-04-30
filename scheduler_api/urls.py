from django.urls import path, reverse
from . import views


urlpatterns = [
    
    path('',views.user_specific_view),
    #path("candidate/<str:candidate_name>", views.candidate_view, name="candidate_detail"),
    path("client/", views.schedule_interview, name="client_detail"),
    path("candidate/", views.candidate_view, name="candidate_detail"),
    #path("client/<str:client_name>/", views.schedule_interview, name="client_detail"),
    #path("candidate/<str:candidate_name>/", views.candidate_view, name="candidate_detail"),
    path('candidate/accept', views.handle_confirmation, name='accept'),
    path('candidate/reschedule',views.handle_rescheduling, name='reschedule')

]