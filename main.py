import argparse
from util import book, storygraph, moonplus
import schedule
import time


def main():
    # get arguments: Path to moon+ reader cache files, storygraph username and password
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to moon+ reader cache files',
                        # default="/home/alex/Nextcloud/Apps/Books/.Moon+/Cache", nargs='?')
                        default="./Cache", nargs='?')
   # parser.add_argument('path', help='path to moon+ reader cache files')

    # parser.add_argument('username', help='storygraph username')
   # parser.add_argument('password', help='storygraph password')
    args = parser.parse_args()
    syncer = storygraph.StoryGraphSyncer()

    schedule.every().hour.do(task, args, syncer)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


def task(args, syncer):
    # get list of books from moon+ reader cache files
    print("[{}] SYNCING....".format(time.strftime("%H:%M:%S")))

    books = moonplus.get_moonplus_books(
        args.path)
    changedBooks = []
    # try to read previous books from cache
    try:
        with open(args.path + "/books.txt", "r") as f:
            for line in f:
                for b in books:
                    progress = float(line.split(" ")[-1].split("%")[0])
                    if line.strip().startswith(b.name) and b.progress != progress:
                        changedBooks.append(b)
    except FileNotFoundError:
        print("No cache file found. Using all books.")
        changedBooks = books
    except Exception as e:
        print("Error reading cache file: {}".format(e))
        exit(1)

    syncer.sync(changedBooks)
    # write books to cache
    with open(args.path + "/books.txt", "w") as f:
        for b in books:
            f.write(str(b) + "\n")
    print("[{}] GOING BACK TO SLEEP....".format(time.strftime("%H:%M:%S")))


if __name__ == '__main__':
    main()
