# in backend/apps/budget/serializers.py

from rest_framework import serializers
from .models import MonthlyBudgetReport

class MonthlyBudgetReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the MonthlyBudgetReport model.
    """
    class Meta:
        model = MonthlyBudgetReport
        fields = '__all__'
