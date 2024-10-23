from django.urls import path
from .views import AddExpenseView, UserExpensesView  # Import correctly

urlpatterns = [
    path('', AddExpenseView.as_view(), name='add_expense'),
    path('user-expenses/', UserExpensesView.as_view(), name='user_expenses'),
    # other URL patterns...
]
