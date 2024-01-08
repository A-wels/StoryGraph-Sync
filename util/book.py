class Book:
    name = ""
    author = ""
    storygraph_id = ""
    storygraph_last_percent_read = 0
    storygraph_last_page_read = 0
    storygraph_total_pages = 0
    pages = 0
    progress = 0.

    def __init__(self, name, progress):
        if (" - " in name):
            self.name = name.split(" - ")[:-1][0]
            self.author = name.split(" - ")[-1]
        else:
            self.name = name
            self.author = ""
        self.progress = progress

    # make book object printable

    def __str__(self):
        return self.name + " by " + self.author + " " + str(self.progress) + "%"
