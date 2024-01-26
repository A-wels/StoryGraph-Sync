from unittest.mock import patch
from util.moonplus import get_moonplus_books
from typing import List
from util.book import Book


@patch('util.moonplus._download_from_nextcloud')
@patch('os.path.exists')
@patch('os.makedirs')
def test_get_moonplus_books(mock_makedirs, mock_exists,
                            mock_download_from_nextcloud):
    cache_path = "tests/files"

    # Mock the os.path.exists and os.makedirs methods
    mock_exists.return_value = False
    mock_makedirs.return_value = None

    # Mock the _download_from_nextcloud function
    mock_download_from_nextcloud.return_value = None

    # get books
    books: List[Book] = get_moonplus_books(cache_path)

    assert isinstance(books, list)
    assert len(books) == 2
    assert not books[0].isFinished
    assert books[1].isFinished
    assert books[0].progress == 0.6
    assert books[1].progress == 100
    assert books[0].name == "Der Herr Der Ringe"
    assert books[1].name == "Die Kinder des Wüstenplaneten"
