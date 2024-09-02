import argparse
import logging
from util import storygraph, moonplus, audiobookshelf
import schedule
import time


def main():
    # get arguments: Path to moon+ reader cache files, storygraph username and password
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='path to moon+ reader cache files',
                        # default="/home/alex/Nextcloud/Apps/Books/.Moon+/Cache", nargs='?')
                        default="./Cache", nargs='?')
    parser.add_argument('-i', '--interval', help='sync interval in hours',
                        default=2, nargs='?')
    parser.add_argument('--loglevel', help='log level',
                        default="INFO", nargs='?')
    # bool: use audiobookshelf and moonplus? Default true
    parser.add_argument('--audiobookshelf', action='store_false')
    parser.add_argument('--moonplus', action='store_false')

    args = parser.parse_args()
    logging.basicConfig(
        level=args.loglevel, format='[INFO] [%(asctime)s]: %(message)s', datefmt='%H:%M:%S')

    schedule.every(args.interval).hours.do(task, args)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


def task(args):
    logging.info("Syncing....")
    # get books from audiobookshelf
    books = []
    if (args.audiobookshelf):
        audiobookshelfSync = audiobookshelf.AudioBookShelfSyncer()
        # add all audiobooks to book list
        try:
            audiobooks = audiobookshelfSync.get_audiobookshelf_books()
        except:
            audiobooks = []
            logging.error("Could not get progress from audiobookshelf")
        for book in audiobooks:
            books.append(book)
    if (args.moonplus):
        # get list of books from moon+ reader cache files
        try:
            moonbooks = moonplus.get_moonplus_books(args.path)
        except:
            moonbooks = []
            logging.error('Could not get progress from moonplus')
            logging.exception('')
        for book in moonbooks: 
            books.append(book)

    # login to storygraph to prepare sync
    syncer = None
    try:
     syncer = storygraph.StoryGraphSyncer()
    except:
        logging.error("Could not connect to TheStoryGraph. Going back to sleep.")
        return

    # combine books from moon+ reader and audiobookshelf

    changedBooks = []
    # try to read previous books from cache
    # cache format: bookname progress finished
    try:
        with open(args.path + "/books.txt", "r") as f:
            for line in f:
                for b in books:
                    progress = float(line.split(" ")[-2].split("%")[0])
                    finished = line.endswith("True\n")
                    if line.strip().startswith(b.name) and (float(b.progress) != progress or b.isFinished != finished):
                        changedBooks.append(b)
    except FileNotFoundError:
        logging.info("No cache file found. Using all books.")
        changedBooks = books
    except Exception as e:
        logging.error("Error reading cache file: {}".format(e))
    if len(changedBooks) == 0:
        logging.info("No Changes")
    else:
        syncer.sync(changedBooks)
    # write books to cache
    with open(args.path + "/books.txt", "w") as f:
        for b in books:
            f.write(str(b) + "\n")
    logging.info("GOING BACK TO SLEEP....")


if __name__ == '__main__':
    main()
