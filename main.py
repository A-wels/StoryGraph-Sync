import argparse
from util import book, storygraph, moonplus


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

    # get list of books from moon+ reader cache files
    books = moonplus.get_moonplus_books(
        args.path)
    syncer.sync(books)


if __name__ == '__main__':
    main()
