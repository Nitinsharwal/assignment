from rest_framework import serializers
from .models import Expense, User, ExpenseSplit

class ExpenseSerializer(serializers.ModelSerializer):
    splits = serializers.DictField(write_only=True, required=False)  # Accept splits in the request

    class Meta:
        model = Expense
        fields = ['description', 'total_amount', 'split_type', 'payer', 'participants', 'splits','amount_owed','id', 'amount', 'description', 'date']

class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['expense', 'user', 'amount_owed']
