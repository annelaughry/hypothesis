# core/serializers.py
from .models import Points
from rest_framework import serializers

class PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Points
        fields = ['user', 'team', 'points_earned']
