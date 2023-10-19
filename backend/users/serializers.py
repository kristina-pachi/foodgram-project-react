from rest_framework import serializers

from .models import MyUser
from recipes.models import Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'id',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, author=obj).exists()
