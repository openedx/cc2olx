import xmlformatter

formatter = xmlformatter.Formatter(compress=True, encoding_output="UTF-8")


def format_xml(xml):
    return formatter.format_string(xml)
