import csv

from django.core.management import BaseCommand

from reviews.models import User, GenreTitle, Categories, Genre, Title, Review
from reviews.models import Comments

from .paths import USERS_PATH, CATEGORY_PATH, GENRE_PATH, TITLES_PATH
from .paths import GENRE_TITLE_PATH, REVIEW_PATH, COMMENTS_PATH

CSV_PATH = 'static/data/'


class Command(BaseCommand):
    """Класс загрузки данных в базу данных из csv файла"""

    help = "Loading data from csv file"

    def handle(self, *args, **options):

        with open(USERS_PATH, 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )

        with open(CATEGORY_PATH, 'r',
                  encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Categories.objects.get_or_create(
                    name=row['name'],
                    slug=row['slug']
                )

        with open(GENRE_PATH, 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Genre.objects.get_or_create(
                    name=row['name'],
                    slug=row['slug']
                )

        with open(TITLES_PATH, 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Title.objects.get_or_create(
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category']
                )

        with open(GENRE_TITLE_PATH) as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                GenreTitle.title = GenreTitle.objects.get(id=row['title_id'])
                GenreTitle.genre = GenreTitle.objects.get(id=row['genre_id'])

        with open(REVIEW_PATH, 'r', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Review.objects.get_or_create(
                    id=row['id'],
                    title=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )

        with open(COMMENTS_PATH, 'r',
                  encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            for row in dict_reader:
                Comments.objects.get_or_create(
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                )

        self.stdout.write(self.style.SUCCESS('Database loaded successfully!'))
