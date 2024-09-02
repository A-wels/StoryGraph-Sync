import logging
import config
import requests
from thefuzz import process


class StoryGraphSyncer:
    session = ""
    csrf_token = ""
    token = ""
    currently_reading = []
    post_values = []

    def __init__(self):
        # get tokens
        if self.token == "":
            self.get_tokens()
        # get currently reading books
        self.get_currently_reading()

    def get_tokens(self):
        logging.info("Logging into StoryGraph")
        # get storygraph session
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html, application/xhtml+xml'

        }
        response = requests.get(
            "https://app.thestorygraph.com/users/sign_in", headers=headers)
        self.session = response.cookies["_storygraph_session"]

        # get csrf token: content of <meta name="csrf-token" content="TOKEN">
        self.csrf_token = response.text.split(
            '<meta name="csrf-token" content="')[1].split('"')[0]

        # get login token by POST to login page
        headers = {
            'Host': 'app.thestorygraph.com',
            # Include the full Cookie value
            'Cookie': '_storygraph_session='+self.session,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://app.thestorygraph.com/users/sign_in',
            'Origin': 'https://app.thestorygraph.com',
            'Dnt': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'same-origin',
            'Sec-Fetch-Site': 'same-origin',
            'Te': 'trailers'
        }
        data = {
            'authenticity_token': self.csrf_token,
            'user[email]': config.email,
            'user[password]': config.password,
            'user[remember_me]': '1',
            'return_to': ''
        }
        response = requests.post(
            'https://app.thestorygraph.com/users/sign_in', headers=headers, data=data, allow_redirects=False)

        token = response.cookies["remember_user_token"]
        self.token = token
        logging.error("Error getting token")

    def sync(self, books):
        # try to match books with currently reading books by comparing titles. Get best match
        current_books = []
        for book in self.currently_reading:
            current_books.append(book[1])
        for book in books:
            # get best match
            best_match = process.extractOne(book.name, current_books)
            logging.info("Trying to match " + book.name)
            if best_match[1] >= 70:
                # if match is good enough, add book to currently reading
                logging.info("Matched " + book.name + " with " + best_match[0])
                # get id of book: first value in self.currently_reading
                id = ""
                for c in self.currently_reading:
                    if c[1] == best_match[0]:
                        id = c[0]
                        break

                # get post values for book
                post_values = []
                for p in self.post_values:
                    if p[0] == id:
                        post_values = p
                        # if post values are empty: book has not been started yet.
                        if (len(post_values) == 0):
                            post_values = [0, 0, 0, 0]
                        break
                # send post to storygraph
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://app.thestorygraph.com/currently-reading/alex_reads_',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Csrf-Token': self.csrf_token,
                    'Origin': 'https://app.thestorygraph.com',
                    'DNT': '1',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Connection': 'keep-alive',
                }
                cookies = {"remember_user_token": self.token,
                           "_storygraph_session": self.session}

                url = "https://app.thestorygraph.com/update-progress"
                if (len(post_values) == 0):
                    post_values = [0, 0, 0, 0]
                data = {
                    "read_status[progress_minutes]": "",
                    "read_status[progress_number]": str(int(book.progress)),
                    "read_status[progress_type]": "percentage",
                    "read_status[last_reached_pages]": post_values[1],
                    "read_status[book_num_of_pages]": post_values[2],
                    "read_status[last_reached_percent]": post_values[3],
                    "book_id": id,
                    "commit": "Save"
                }

                response = requests.post(
                    url, headers=headers, data=data, cookies=cookies)
                if (response.status_code == 200):
                    logging.info("Successfully updated " + book.name)
                    logging.info("New Progress: " + str(book.progress) + "%\n")
                else:
                    logging.error("Error updating " + book.name)

                # set book to read if progress is 100%
                if (int(book.progress) == 100 or book.isFinished):
                    logging.info("Finished " + book.name)
                    data = {
                        "book_id": id,
                        "status": "read",
                    }
                    url = "https://app.thestorygraph.com/update-status"
                    response = requests.post(
                        url, headers=headers, data=data, cookies=cookies)
                    if (response.status_code == 200):
                        logging.info("Successfully set " +
                                     book.name + " to read")

            else:
                logging.info("No match found.\n")

                # Print the response from the server

    def get_currently_reading(self):
        # get currently reading books
        currently_reading = []
        cookies = {"remember_user_token": self.token}
        currently_reading = requests.get("https://app.thestorygraph.com/currently-reading/alex_reads_", cookies=cookies).content.decode("utf-8")
        # get values for post request
        post_values = self.get_post_values(currently_reading)
        # all books are in a <a href="/books/{random-id}"> BOOK-TITLE </a> tag. Get the BOOK-TITLE
        currently_reading_books = currently_reading.split(
            '<a href="/books/')[1:]
        # remove all elements at uneven indices
        currently_reading_books = [currently_reading_books[i]
                                   for i in range(len(currently_reading_books)) if i % 2 != 0]
        for i in range(len(currently_reading_books)):

            id = currently_reading_books[i].split('"')[0]
            name = currently_reading_books[i].split('">')[
                1].split('</a>')[0]

            currently_reading_books[i] = (id, name)

        # remove duplicates
        currently_reading_books = list(dict.fromkeys(currently_reading_books))

        self.post_values = post_values
        self.currently_reading = currently_reading_books

    def get_post_values(self, response):
        # result entry consists of four values: book-id, read_status[last_reached_pages], read_status[book_num_of_pages], read_status[last_reached_percent]
        results = []
        result_entry = []

        for line in response.split("\n"):
            if 'name="book_id" id="book_id' in line:
                # if it does, add the previous result entry to results
                if len(result_entry) == 4:
                    results.append(result_entry)
                # reset result entry
                result_entry = []
                # get book-id
                bid = line.split(
                    "value=")[1].split('"')[1]
                if not bid in result_entry:
                    result_entry.append(bid)
            # check if the line contains the read_status[last_reached_pages]: name="read_status[last_reached_pages]"
            if "name=\"read_status[last_reached_pages]" in line:
                # get read_status[last_reached_pages]
                result_entry.append(line.split('value="')[1].split('"')[0])
            # check if the line contains the read_status[book_num_of_pages]: name="read_status[book_num_of_pages]"
            if "name=\"read_status[book_num_of_pages]" in line:
                # get read_status[book_num_of_pages]
                result_entry.append(line.split('value="')[1].split('"')[0])
            # check if the line contains the read_status[last_reached_percent]: name="read_status[last_reached_percent]"
            if "name=\"read_status[last_reached_percent]" in line:
                # get read_status[last_reached_percent]
                result_entry.append(line.split('value="')[1].split('"')[0])

        # remove duplicates: Detect by first entry of result entry. DOnt use dict
        results = [results[i]
                   for i in range(len(results)) if results[i][0] != results[i-1][0]]

        return results
