from rest_framework import serializers

from .models import MyUser


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = MyUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Пользователя с username "me" '
                                              'нельзя зарегистрировать')
        return value


class TokenSerializer(serializers.ModelSerializer):
    """Выдача токена."""
    class Meta:
        model = MyUser
        fields = ('username', 'email')
