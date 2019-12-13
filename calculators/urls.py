from django.urls import path
from . import views

urlpatterns = [
    path('when_can_I_retire_form', views.whenCanIRetireFormScreen, name='calculators-whenCanIRetireFormScreen'),
    path('when_can_i_retire_result/', views.whenCanIRetireResultScreen, name='calculators-whenCanIRetireResult'),
    path('interest_form', views.interestFormScreen, name='calculators-interestFormScreen'),
    path('interest_result/', views.interestResultScreen, name='calculators-interestResultScreen'),
    path('time_to_pay_off_form', views.timeToPayOffFormScreen, name='calculators-timeToPayOffFormScreen'),
    path('time_to_pay_off_result/', views.timeToPayOffResultScreen, name='calculators-timeToPayOffResultScreen'),

]
