
import logging
import os
from util.book import Book
import config
from nextcloud import NextCloud


def get_moonplus_books(path):

    # create cache folder if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # get list of files from nextcloud
    _download_from_nextcloud(path)
    # get list of books from moon+ reader cache files. Each book has a .po file at the path
    books = []
    for f in os.listdir(path):
        if f.endswith('.po'):
            # .po files have name format: title.format.po
            name = f.split('.')[0]
            # get progress from .po file: Progress in percent after : in first line
            with open(os.path.join(path, f), 'r') as file:
                progress = float(file.readline().split(':')[1].split('%')[0])

           # check if a book is already in the list. If so, update progress if it is higher
            found = False
            for b in books:
                if b.name == name:
                    found = True
                    if b.progress < progress:
                        b.progress = progress
            if not found:
                books.append(Book(name, progress))
    return books


def _download_from_nextcloud(cache_path):
    logging.info("Downloading from Nextcloud...")
    with NextCloud(endpoint=config.NEXTCLOUD_URL, user=config.NEXTCLOUD_USERNAME,
                   password=config.NEXTCLOUD_PASSWORD) as nxc:
        folderpath = "Apps/Books/.Moon+/Cache"
        # remove all po files from cache folder
        for f in os.listdir(cache_path):
            if (f.endswith(".po")):
                os.remove(cache_path + "/" + f)

        # get list of files from nextcloud
        folders = nxc.list_folders(folderpath)
        for f in folders.data:
            if (f.href.endswith('.po')):
                # Format: /remote.php/dav/files/alex/Apps/Books/.Moon+/Cache/Alice_de.epub.po
                # Format to: Apps/Books/.Moon+/Cache/Alice_de.epub.po
                href = f.href.split('/remote.php/dav/files/alex/')[1]
                # Get the filename
                # Download the file
                logging.info("Downloading " + href + "...")
                nxc.download_file(href, cache_path, overwrite=True)
