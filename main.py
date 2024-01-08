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
    syncer.sync(books)
    print("[{}] GOING BACK TO SLEEP....".format(time.strftime("%H:%M:%S")))


if __name__ == '__main__':
    main()
