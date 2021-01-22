import csv


class LinkFileReader:
    """
    This class is responsible to read the csv file that is provided and generates
    a map of link to the row where this link belongs to.

    +---------------------------------------------------------------------------------------------+--------+-------------+  # noqa: E501
    |                                     External Video Link                                     | Edx Id | Youtube Id  |
    +---------------------------------------------------------------------------------------------+--------+-------------+
    | https://cdnapisec.kaltura.com/p/32/sp/43/playManifest/entryId/bzh/format/url/protocol/https | 45edio | onRUvL2SBG8 |
    +---------------------------------------------------------------------------------------------+--------+-------------+


    Here either Edx Id or Youtube Id is required. If both are given Edx Id takes priority.

    """

    def __init__(self, file_path):
        """
        Args:
            file_path ([str]): Link map file path.
        """
        self.file_path = file_path
        self.link_header = "External Video Link"

    def get_link_map(self):
        """
        This function helps to create a map of link URL with the rows fo the
        csv file.

        Returns:
            [Dict[str, Dict]]: Map of link with the corresponding row
        """
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
        with open(self.file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader]
        return rows
