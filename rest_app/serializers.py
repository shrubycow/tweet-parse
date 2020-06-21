from rest_framework import serializers
from .models import TweetIds


class TweetIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = TweetIds
        fields = ['id']