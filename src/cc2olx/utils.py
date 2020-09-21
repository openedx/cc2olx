""" Utility functions for cc2olx"""


def element_builder(xml_doc):
    """
    Given a document returns a function to build xml elements.

    Args:
        xml_doc (xml.dom.minidom.Document)

    Returns:
        element (func)
    """

    def element(name, children, attributes=None):
        """
        An utility to help build xml tree in a managable way.

        Args:
            name (str) - tag name
            children (str|list|xml.dom.minidom.Element)
            attributes (dict)

        Returns:
            elem (xml.dom.minidom.Element)
        """

        elem = xml_doc.createElement(name)

        # set attributes if exists
        if attributes is not None and isinstance(attributes, dict):
            [elem.setAttribute(key, val) for key, val in attributes.items()]

        # set children if exists
        if children is not None:
            if isinstance(children, list) or isinstance(children, tuple):
                [elem.appendChild(c) for c in children]
            elif isinstance(children, str):
                elem.appendChild(xml_doc.createTextNode(children))
            else:
                elem.appendChild(children)

        return elem

    return element
