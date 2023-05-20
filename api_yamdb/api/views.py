from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, views
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import (DestroyModelMixin,
                                   CreateModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Title, Category, Genre, Review
from users.models import User
from .filter import TitleFilter
from .permissions import (AdminOnly, IsAdminUserOrReadOnly,
                          AdminModeratorAuthorPermission)
from .serializers import (TitleSerializer, CategorySerializer,
                          GenreSerializer, UsersSerializer,
                          ReviewSerializer, JWTTokenSerializer,
                          CommentSerializer, TitleReadSerializer,
                          SignupSerializer
                          )
from .utils import send_confirmation_code


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    http_method_names = ['patch', 'get', 'post', 'delete']

    @action(methods=['patch', 'get'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='me', url_name='me')
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)

        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=self.request.user.role)
        return Response(serializer.data)


class CategoryViewSet(CreateModelMixin, ListModelMixin,
                      DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['=name']
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class GenreViewSet(CreateModelMixin, ListModelMixin,
                   DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUserOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(
            title=title,
            author=self.request.user
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review.objects.filter(title_id=title.id), pk=review.id
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review.objects.filter(title_id=title.id), pk=review.id
        )
        serializer.save(
            review=review,
            author=self.request.user
        )


class SignupView(views.APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError as error:
            raise ValidationError(
                ('Ошибка при попытке создать новую запись '
                 f'в базе с username={username}, email={email}')
            ) from error

        user.save()
        send_confirmation_code(user)
        return Response(serializer.validated_data, status=HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class TokenView(views.APIView):

    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = request.data['confirmation_code']

        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {
                    "confirmation_code": ("Неверный код доступа "
                                          f"{confirmation_code}")
                },
                status=HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "token": str(
                    RefreshToken.for_user(user).access_token
                )
            }
        )
