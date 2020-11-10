import csv


class LinkFileReader:
    """
        This class is responsible to read the csv file that is provided and generates
        a map of link to the row where this link belongs to.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.link_header = 'Kaltura URL'

    def get_link_map(self):
        link_map = {}
        rows = self._read_csv_file()
        for row in rows:
            link = row[self.link_header]
            link_map[link] = row
        return link_map

    def _read_csv_file(self):
        """
        Reads a csv file as a list of dictionary

        Returns:
            [List[Dict]]: List of dictionary with each header
        """
        with open(self.file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]
        return rows
