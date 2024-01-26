from util.book import Book


def test_book_creation():
    book = Book("Sample Book - Author", 50)
    assert book.name == "Sample Book"
    assert book.author == "Author"
    assert book.progress == 50
    assert not book.isFinished


def test_book_creation_without_author():
    book = Book("Another Book", 25)
    assert book.name == "Another Book"
    assert book.author == ""
    assert book.progress == 25
    assert not book.isFinished


def test_book_str_representation():
    book = Book("Test Book - Tester", 75, True)
    expected_str = "Test Book by Tester 75% True"
    assert str(book) == expected_str


def test_book_100_percent_not_finished():
    book = Book("Test Book - Tester", 100, isFinished=False)
    assert book.isFinished
