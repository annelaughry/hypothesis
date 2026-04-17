from django.urls import path
from . import views


app_name = 'programs'

urlpatterns = [
    path('', views.theme_list, name='programs'),
    path('theme/<int:theme_id>/', views.programs_by_theme, name='programs_by_theme'),
    path('program/<int:pk>/', views.program_detail, name='program_detail'),
    path('program/<int:pk>/register/', views.register_program, name='register_program'),
    path('program/<int:pk>/request-teach/', views.request_to_teach, name='request_to_teach'),
    path('<int:pk>/edit/', views.edit_program, name='program_edit'),
    path('<int:program_id>/activities/add/', views.add_activity, name='add_activity'),



    # ✅ Approvals (for Admins)
    path('approve-registration/<int:registration_id>/', views.approve_registration, name='approve_registration'),
    path('approve-teaching/<int:request_id>/', views.approve_teaching_request, name='approve_teaching_request'),
    path('<int:pk>/request-edit/', views.request_edit_access, name='request_edit_access'),
    path('approve-edit/<int:request_id>/', views.approve_edit_request, name='approve_edit_request'),
    path('programs/request-create/', views.request_program_creation, name='request_program_creation'),
    path("programs/approve-creation/<int:request_id>/", views.approve_program_creation, name="approve_program_creation"),


    
    path('create/', views.create_program, name='create_program'),

    path('program/<int:program_id>/guided/create/', views.create_guided_activity, name='create_guided_activity'),
    path('guided/<int:activity_id>/steps/', views.add_steps, name='add_steps'),
    path('guided/<int:activity_id>/', views.view_guided_activity, name='view_guided_activity'),
    path('guided/step/<int:step_id>/submit/', views.submit_step_response, name='submit_step_response'),
    path('guided/step/<int:step_id>/complete/', views.complete_step, name='complete_step'),
    path('teaching-completed/<int:request_id>/', views.mark_teaching_completed, name='mark_teaching_completed'),
    path('guided_activity/<int:activity_id>/review/', views.review_guided_activity, name='review_guided_activity'),
    path('step/<int:step_id>/student/<int:student_id>/award/', views.assign_step_points, name='assign_step_points'),
    path('activity/<int:activity_id>/assign_timeline/', views.assign_activity_timeline, name='assign_activity_timeline'),

    path('ysa-goals/', views.goal_list, name='goal_list'),
    path('ysa-goals/<slug:slug>/', views.goal_detail, name='goal_detail'),
    path('ysa-goals/<slug:slug>/explore/', views.explore_science, name='explore_science'),
    path('ysa-goals/<slug:slug>/plan/', views.plan_project, name='plan_project'),
    path('ysa-goals/<slug:slug>/datasets/', views.goal_dataset_list, name='goal_datasets'),
    path('datasets/<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('datasets/<int:pk>/edit/', views.edit_dataset, name='edit_dataset'),

    


]
