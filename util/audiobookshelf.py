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

    def get_audiobookshelf_books(self) -> List[Book]:
        logging.info(
            "Getting currently listening books from Audiobookshelf...")
        # get all libraries
        url = "https://audio.a-wels.de/api/libraries"
        header = {
            "Authorization": "Bearer " + self.token
        }
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise Exception("Error getting libraries: " +
                            str(response.status_code) + " " + response.text)
        librariesJson = response.json()

        library_ids = [library["id"] for library in librariesJson["libraries"]]
        # get all books from all libraries
        books = []
        for id in library_ids:
            url = "https://audio.a-wels.de/api/libraries/"+id+"/items"
            response = requests.get(url, headers=header)
            if response.status_code != 200:
                raise Exception("Error getting books: " +
                                str(response.status_code) + " " + response.text)
            booksJson = response.json()
            # get a list of book ids
            books += [book["id"]
                      for book in booksJson["results"]]

        # remove duplicates
        books = list(dict.fromkeys(books))
        # get progress for each book: (name, progress, finished)
        booksProgress = []
        for book_id in tqdm(books):
            url = "https://audio.a-wels.de/api/items/"+book_id+"?expanded=1&include=progress"
            response = requests.get(url, headers=header)
            if response.status_code != 200:
                raise Exception("Error getting book: " +
                                str(response.status_code) + " " + response.text)
            bookJson = response.json()
            # check if userMediaProgress exists
            if "userMediaProgress" not in bookJson or bookJson["userMediaProgress"] is None:
                continue
            else:
                try:
                    book = Book(bookJson["media"]["metadata"]["title"], str(int(float(bookJson["userMediaProgress"]["progress"])*100)), bookJson["userMediaProgress"]["isFinished"])
                    booksProgress.append(book)
                except Exception as e:
                    logging.error(bookJson)
                    print(e)
                    exit()

        return booksProgress
