from django.urls import path
from . import views
urlpatterns = [ 
    path('save_budget/', views.saveBudget, name='save_budget'),
    path('add_to_budget/', views.addToBudget, name='add_to_budget'),
    path('edit_budget/(<categoryName>\s+)', views.editBudgetCategory, name='editBudgetCategory'),
    path('delete_budget/(<categoryName>\s+)', views.deleteBudgetCategory, name='deleteBudgetCategory'),
    path('add_goal/', views.addGoal, name='add_goal'),
    path('edit_goal/(<goalName>\s+)', views.editGoal, name='editGoal'),
    path('delete_goal/(<goalName>\s+)', views.deleteGoal, name='deleteGoal'),

    path('', views.budget, name='budget-home')

]
