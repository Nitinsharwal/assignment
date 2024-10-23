from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()    
    SPLIT_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
    ]
    
    description = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payer_expenses')
    participants = models.ManyToManyField(User, through='ExpenseSplit')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.description} - {self.total_amount}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.name} owes {self.amount_owed} for {self.expense.description}"

def split_expense(expense, splits=None):
    participants = expense.participants.all()
    total_amount = expense.total_amount
    split_type = expense.split_type

    if split_type == 'equal':
        # Split equally among participants
        equal_share = total_amount / participants.count()
        for participant in participants:
            ExpenseSplit.objects.create(expense=expense, user=participant, amount_owed=equal_share)

    elif split_type == 'exact':
        # For exact split, the `splits` argument contains the exact amounts for each participant
        if splits:
            for participant, exact_amount in splits.items():
                ExpenseSplit.objects.create(expense=expense, user=User.objects.get(pk=participant), amount_owed=exact_amount)
    
    elif split_type == 'percentage':
        # For percentage split, the `splits` argument contains the percentages for each participant
        if splits:
            for participant, percentage in splits.items():
                amount_owed = (percentage / 100) * total_amount
                ExpenseSplit.objects.create(expense=expense, user=User.objects.get(pk=participant), amount_owed=amount_owed)

    elif split_type == 'percentage':
        if splits:
            total_percentage = sum(splits.values())
            if total_percentage != 100:
                raise ValueError("Percentages must add up to 100%")
            for participant, percentage in splits.items():
                amount_owed = (percentage / 100) * total_amount
                ExpenseSplit.objects.create(expense=expense, user=User.objects.get(pk=participant), amount_owed=amount_owed)
