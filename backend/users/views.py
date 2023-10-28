from rest_framework import permissions, pagination, viewsets

from .models import MyUser
from .serializers import UserSerializer


class MyUserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
