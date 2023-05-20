from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Title, Category, Genre, Review, Comments
from users.models import User
from api_yamdb import settings
from .utils import username_validation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(), )
    year = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(
        read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        model = Title


class UsersSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            username_validation,
        ]
    )

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        required=False,
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        fields = ('id', 'score', 'text', 'pub_date', 'author')
        read_only_fields = ('id', 'pub_date', 'author',)

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')

        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title_id)
        if (title.reviews.filter(author=author).exists()
                and self.context.get('request').method != 'PATCH'):
            raise serializers.ValidationError(
                'Можно оставлять только один отзыв!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        required=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'pub_date', 'author',)
        read_only_fields = ('id', 'pub_date', 'author',)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            username_validation,
        ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.EMAIL_MAX_LENGTH
    )


class UserRestrictedSerializer(UsersSerializer):
    """
    Сериализатор модели юзер для изменения пользователями своих аккаунтов.
    """

    class Meta(UsersSerializer.Meta):
        read_only_fields = ('username', 'email', 'role')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email')
        model = User


class JWTTokenSerializer(serializers.Serializer):
    """Сериализатор запроса JWT токена."""
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[
            username_validation
        ]
    )
