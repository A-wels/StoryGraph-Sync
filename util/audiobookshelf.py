import logging
import requests
from typing import List
from tqdm import tqdm
import config
from util.book import Book


class AudioBookShelfSyncer:
    token = ""

    def __init__(self):
        self.token = config.AUDIOBOOKSHELF_TOKEN

    def get_libraries(self) -> List[str]:
        """
        Get all libraries from Audiobookshelf.
        :return List of libraries.
        """
        logging.info("Getting libraries from Audiobookshelf...")
        url = "https://audio.a-wels.de/api/libraries"
        header = {
            "Authorization": "Bearer " + self.token
        }
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise Exception("Error getting libraries: " + str(response.status_code) + " " + response.text)
        librariesJson = response.json()
        return [library["id"] for library in librariesJson["libraries"]]

    def get_books_from_library(self, library_id: str) -> List[str]:
        """
        Get all books from a library.
        :param library_id: Library id.
        :return List of books from a library.
        """
        logging.info("Getting books from library " + library_id + "...")
        url = "https://audio.a-wels.de/api/libraries/" + library_id + "/items"
        header = {
            "Authorization": "Bearer " + self.token
        }
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise Exception("Error getting books: " + str(response.status_code) + " " + response.text)
        booksJson = response.json()
        return list(dict.fromkeys([book["id"]
                                   for book in booksJson["results"]]))

    def get_progress(self, book_id: str) -> (str, str, bool):
        """
        Get progress of a book.
        :param book_id: Book id.
        :return: (name, progress, finished)
        """
        url = "https://audio.a-wels.de/api/items/" + \
            book_id + "?expanded=1&include=progress"
        header = {
            "Authorization": "Bearer " + self.token
        }
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise Exception("Error getting book: " + str(response.status_code) + " " + response.text)
        bookJson = response.json()
        # check if userMediaProgress exists
        if "userMediaProgress" not in bookJson:
            return (None, None, None)
        else:
            return (bookJson["media"]["metadata"]["title"],
                    str(int(
                        float(bookJson["userMediaProgress"]["progress"]) * 100)),
                    bookJson["userMediaProgress"]["isFinished"])

    def get_audiobookshelf_books(self) -> List[Book]:
        """
        Get all books from Audiobookshelf.
        :return List of books from Audiobookshelf.
        """

        # get all libraries
        library_ids = self.get_libraries()
        # get all books from all libraries
        books = []
        for library_id in library_ids:
            books += self.get_books_from_library(library_id)
        # get progress for each book: (name, progress, finished)
        booksProgress = []
        for id in tqdm(books):
            progress = self.get_progress(id)
            booksProgress.append(Book(progress[0], progress[1], progress[2]))
        return booksProgress
