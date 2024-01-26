from unittest.mock import MagicMock, patch

from util.audiobookshelf import AudioBookShelfSyncer
from util.book import Book
from typing import List


@patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value={
    "libraries": [
        {
            "id": "35zsfasdf4"
        },
        {
            "id": "36234123123"
        }
    ]
})))
def test_get_libraries(mock_get):
    syncer = AudioBookShelfSyncer()
    libraries: List[str] = syncer.get_libraries()
    assert isinstance(libraries, list)
    assert len(libraries) == 2
    assert libraries[0] == "35zsfasdf4"
    assert libraries[1] == "36234123123"


@patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value={
    "results": [
        {
            "id": "bookid1"
        },
        {
            "id": "bookid2"
        }
    ]
})))
def test_get_Library_books(mock_get):
    library_ids = ["35zsfasdf4", "36234123123"]
    syncer = AudioBookShelfSyncer()
    books: List[str] = syncer.get_books_from_library(library_ids[0])
    assert isinstance(books, list)
    assert len(books) == 2
    assert books[0] == "bookid1"
    assert books[1] == "bookid2"


@patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value={
    "media": {
        "metadata": {
            "title": "bookName1"
        }
    },
    "userMediaProgress": {
        "progress": "0.5",
        "isFinished": False
    }
})))
def test_get_progress(mock_get):
    syncer = AudioBookShelfSyncer()
    book_id = "bookid1"
    name, progress, finished = syncer.get_progress(book_id)
    assert name == "bookName1"
    assert progress == "50"
    assert finished is False


@patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value={
    "media": {
        "metadata": {
            "title": "bookName1"
        }
    },
})))
def test_non_existing_progress(mock_get):
    syncer = AudioBookShelfSyncer()
    book_id = "bookid1"
    name, progress, finished = syncer.get_progress(book_id)
    assert name is None
    assert progress is None
    assert finished is None


def test_get_audiobookshelf_books():
    syncer = AudioBookShelfSyncer()
    syncer.get_libraries = MagicMock(return_value=["libraryid1", "libraryid2"])
    syncer.get_books_from_library = MagicMock(
        return_value=["bookid1", "bookid2"])
    syncer.get_progress = MagicMock(return_value=("bookName1", "50", False))

    books: List[Book] = syncer.get_audiobookshelf_books()
    assert isinstance(books, list)
    assert isinstance(books[0], Book)
    assert len(books) == 4
    assert books[0].name == "bookName1"
    assert books[0].progress == "50"
    assert books[0].isFinished is False
    assert books[1].name == "bookName1"
    assert books[1].progress == "50"
    assert books[1].isFinished is False


@patch('requests.get', return_value=MagicMock(status_code=401, text="This is the error text for unauthorized"))
def test_get_progress_unauthorized(mock_get):
    syncer = AudioBookShelfSyncer()
    book_id = "bookid1"
    try:
        syncer.get_progress(book_id)
    except Exception as e:
        assert str(
            e) == "Error getting book: 401 This is the error text for unauthorized"


@patch('requests.get', return_value=MagicMock(status_code=401, text="This is the error text for unauthorized"))
def test_get_books_from_library_unauthorized(mock_get):
    syncer = AudioBookShelfSyncer()
    library_id = "libraryid1"
    try:
        syncer.get_books_from_library(library_id)
    except Exception as e:
        assert str(
            e) == "Error getting books: 401 This is the error text for unauthorized"


@patch('requests.get', return_value=MagicMock(status_code=401, text="This is the error text for unauthorized"))
def test_get_libraries_unauthorized(mock_get):
    syncer = AudioBookShelfSyncer()
    try:
        syncer.get_libraries()
    except Exception as e:
        assert str(
            e) == "Error getting libraries: 401 This is the error text for unauthorized"
