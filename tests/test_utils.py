from cc2olx.utils import clean_from_cdata


class TestXMLCleaningFromCDATA:
    """
    Test XML string cleaning from CDATA sections.
    """

    def test_cdata_containing_html_is_cleaned_successfully(
        self,
        cdata_containing_html: str,
        expected_cleaned_cdata_containing_html: str,
    ) -> None:
        """
        Test if CDATA tags are removed from HTML while their content is kept.

        Args:
            cdata_containing_html (str): HTML that contains CDATA tags.
            expected_cleaned_cdata_containing_html (str): Expected HTML after
                successful cleaning.
        """
        actual_cleaned_cdata_containing_html = clean_from_cdata(cdata_containing_html)

        assert actual_cleaned_cdata_containing_html == expected_cleaned_cdata_containing_html

    def test_html_without_cdata_remains_the_same_after_cleaning(self, html_without_cdata: str) -> None:
        """
        Test if HTML that doesn't contain CDATA tags remains the same.

        Args:
            html_without_cdata (str): HTML that doesn't contains CDATA tags.
        """
        actual_cleaned_html_without_cdata = clean_from_cdata(html_without_cdata)

        assert actual_cleaned_html_without_cdata == html_without_cdata
