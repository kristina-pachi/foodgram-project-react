from rest_framework import permissions, pagination, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import MyUser
from .serializers import UserSerializer
from api.serializers import GetFollowSerializer


class MyUserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(
            methods=['get'],
            detail=False,
            serializer_class=GetFollowSerializer,
            permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        user = request.user
        authors = MyUser.objects.filter(following__user=user)
        serializer = self.serializer(authors, many=True)
        return Response(serializer.data)
