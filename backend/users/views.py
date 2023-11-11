from rest_framework import permissions, pagination, generics

from .models import MyUser
from api.serializers import GetFollowSerializer


class APIMyUser(generics.ListCreateAPIView):
    """
    Принимает только GET запрос,
    отдаёт список подписок.
    """

    serializer_class = GetFollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = MyUser.objects.filter(following__user=user)
        return queryset
