from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

from .utils import year_validate


class Category(models.Model):
    """Модель категорий"""

    name = models.TextField(
        blank=False,
        unique=True,
        max_length=32
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров"""

    name = models.CharField(
        blank=False,
        unique=True,
        max_length=32
    )
    slug = models.SlugField(
        max_length=25,
        unique=True,
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений, к которым пишут отзывы"""

    name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Название'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=(year_validate,)
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='title',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        through_fields=('title', 'genre'),
        verbose_name='Жанр'
    )

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель отношения Произведение-Жанр"""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )


class Review(models.Model):
    """Модель отзывов на произведения"""

    id = models.AutoField(primary_key=True)
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.PROTECT,
        related_name='reviews',
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='author_reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1,
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        unique_together = ('title', 'author',)

    def __str__(self):
        return self.text


class Comments(models.Model):
    """Модель комментариев к отзывам"""

    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(
        Review,
        verbose_name='Комментарий',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
