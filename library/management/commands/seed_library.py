from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random

from library.models import Author, Publisher, Genre, Book


class Command(BaseCommand):
    help = "Seeds the database with test data (authors, publishers, genres, thousands of books)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--books",
            type=int,
            default=5000,
            help="How many books to generate (default: 5000)"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()
        book_count = options["books"]

        self.stdout.write("Clearing existing data...")
        Book.objects.all().delete()
        Author.objects.all().delete()
        Publisher.objects.all().delete()
        Genre.objects.all().delete()

        # ------------------------------
        # 1. Authors
        # ------------------------------
        self.stdout.write("Creating base authors...")

        base_authors = [
            ("J.K.", "Rowling", "UK", 1965),
            ("J.R.R.", "Tolkien", "UK", 1892),
            ("Stephen", "King", "USA", 1947),
            ("Isaac", "Asimov", "USA", 1920),
            ("George", "Orwell", "UK", 1903),
            ("Agatha", "Christie", "UK", 1890),
            ("Ernest", "Hemingway", "USA", 1899),
            ("Mark", "Twain", "USA", 1835),
            ("Frank", "Herbert", "USA", 1920),
            ("Arthur", "Clarke", "UK", 1917),
        ]

        authors = []
        for first, last, country, year in base_authors:
            authors.append(Author.objects.create(
                first_name=first,
                last_name=last,
                country=country,
                birth_year=year
            ))

        # Generate extra random authors
        self.stdout.write("Creating random authors...")
        for _ in range(25):
            authors.append(Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                country=fake.country(),
                birth_year=random.randint(1850, 2000)
            ))

        # ------------------------------
        # 2. Publishers
        # ------------------------------
        self.stdout.write("Creating publishers...")

        publishers = [
            Publisher.objects.create(name="Bloomsbury", city="London", established_year=1986),
            Publisher.objects.create(name="Penguin Books", city="New York", established_year=1935),
            Publisher.objects.create(name="HarperCollins", city="New York", established_year=1989),
            Publisher.objects.create(name="Vintage", city="London", established_year=1990),
            Publisher.objects.create(name="Macmillan", city="Berlin", established_year=1869),
        ]

        # ------------------------------
        # 3. Genres
        # ------------------------------
        self.stdout.write("Creating genres...")

        genre_names = [
            "Fantasy", "Horror", "Sci-Fi", "Drama", "Romance", "Thriller",
            "Detective", "Adventure", "Biography", "History", "Philosophy"
        ]
        genres = [Genre.objects.create(name=name) for name in genre_names]

        # ------------------------------
        # 4. Generate many Books
        # ------------------------------
        self.stdout.write(f"Generating {book_count} books...")
        books_to_create = []

        for _ in range(book_count):
            books_to_create.append(Book(
                title=fake.sentence(nb_words=4),
                publication_year=random.randint(1900, 2025),
                pages=random.randint(80, 1500),
                price=round(random.uniform(50, 300), 2),
                author=random.choice(authors),
                publisher=random.choice(publishers),
            ))

        # bulk_create — for speed
        books = Book.objects.bulk_create(books_to_create, batch_size=1000)

        # ------------------------------
        # 5. Assign genres (M2M)
        # ------------------------------
        self.stdout.write("Assigning genres to books...")

        for book in books:
            # 1–3 genres randomly
            book.genres.add(*random.sample(genres, random.randint(1, 3)))

        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))
