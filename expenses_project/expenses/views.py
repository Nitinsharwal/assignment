from rest_framework import generics, status
from rest_framework.response import Response
from .models import Expense, User, ExpenseSplit
from .serializers import ExpenseSerializer
from .models import split_expense
from .serializers import ExpenseSplitSerializer
from django.test import TestCase
from django.views import View
from django.http import HttpResponse


class AddExpenseView(View):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    def get(self, request):
        return HttpResponse("This is the Add Expense page.")



class AddExpenseView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer

    def post(self, request, *args, **kwargs):
        try:
            splits = request.data.get('splits', {})
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            expense = serializer.save()
            split_expense(expense, splits)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserExpensesView(generics.ListAPIView):
    serializer_class = ExpenseSplitSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return ExpenseSplit.objects.filter(user_id=user_id)

class ExpenseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(name="User 1", email="user1@example.com", mobile="1111111111")
        self.user2 = User.objects.create(name="User 2", email="user2@example.com", mobile="2222222222")
        self.user3 = User.objects.create(name="User 3", email="user3@example.com", mobile="3333333333")

    def test_create_expense_equal_split(self):
        expense_data = {
            "description": "Dinner",
            "total_amount": 3000,
            "split_type": "equal",
            "payer": self.user1.id,
            "participants": [self.user1.id, self.user2.id, self.user3.id]
        }
        response = self.client.post(reverse('add-expense'), expense_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(ExpenseSplit.objects.count(), 3)
        splits = ExpenseSplit.objects.all()
        for split in splits:
            self.assertEqual(split.amount_owed, 1000)

class RetrieveUserExpensesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(name="User 1", email="user1@example.com", mobile="1111111111")
        self.expense = Expense.objects.create(description="Shopping", total_amount=1000, split_type="equal", payer=self.user)
        ExpenseSplit.objects.create(expense=self.expense, user=self.user, amount_owed=500)
    
    def test_retrieve_user_expenses(self):
        response = self.client.get(reverse('user-expenses', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Ensure 1 expense is returned
        self.assertEqual(response.data[0]['amount_owed'], '500.00')

class BalanceSheetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(name="User 1", email="user1@example.com", mobile="1111111111")
        self.expense = Expense.objects.create(description="Party", total_amount=2000, split_type="equal", payer=self.user)
        ExpenseSplit.objects.create(expense=self.expense, user=self.user, amount_owed=1000)

    def test_download_balance_sheet(self):
        response = self.client.get(reverse('download-balance-sheet'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        content = response.content.decode('utf-8')
        self.assertIn('User 1', content)  # Check if user appears in the CSV
        self.assertIn('Party', content)  # Check if expense appears in the CSV


