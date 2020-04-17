NAMESPACE = {
    'ims': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1',
    'lomimscc': 'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest',
}


def parse_manifest(node):
    data = dict()
    data['metadata'] = parse_metadata(node)
    data['organizations'] = parse_organizations(node)
    return data


def parse_metadata(node):
    data = dict()
    metadata = node.find('./ims:metadata', NAMESPACE)
    if metadata:
        data['schema'] = parse_schema(metadata)
        data['lom'] = parse_lom(metadata)
        # parse_metadata_lom(metadata)
    return data


def parse_schema(node):
    schema_name = parse_schema_name(node)
    schema_version = parse_schema_version(node)
    data = {
        'name': schema_name,
        'version': schema_version,
    }
    return data


def parse_schema_name(node):
    schema_name = node.find('./ims:schema', NAMESPACE)
    schema_name = schema_name.text
    return schema_name


def parse_schema_version(node):
    schema_version = node.find('./ims:schemaversion', NAMESPACE)
    schema_version = schema_version.text
    return schema_version


def parse_lom(node):
    data = dict()
    lom = node.find('lomimscc:lom', NAMESPACE)
    if lom:
        data['general'] = parse_general(lom)
        data['lifecycle'] = parse_lifecycle(lom)
        data['rights'] = parse_rights(lom)
    return data


def parse_general(node):
    data = {}
    general = node.find('lomimscc:general', NAMESPACE)
    if general:
        data['title'] = parse_text(general, 'lomimscc:title/lomimscc:string')
        data['language'] = parse_text(general, 'lomimscc:language/lomimscc:string')
        data['description'] = parse_text(general, 'lomimscc:description/lomimscc:string')
        data['keywords'] = parse_keywords(general)
    return data


def parse_text(node, lookup):
    text = None
    element = node.find(lookup, NAMESPACE)
    if element is not None:
        text = element.text
    return text


def parse_keywords(node):
    # TODO: keywords
    keywords = []
    return keywords


def parse_rights(node):
    data = dict()
    element = node.find('lomimscc:rights', NAMESPACE)
    if element:
        data['is_restricted'] = parse_text(
            element,
            'lomimscc:copyrightAndOtherRestrictions/lomimscc:value'
        )
        data['description'] = parse_text(
            element,
            'lomimscc:description/lomimscc:string'
        )
        # TODO: cost
    return data


def parse_lifecycle(node):
    # TODO: role
    # TODO: entity
    data = dict()
    contribute_date = node.find('lomimscc:lifeCycle/lomimscc:contribute/lomimscc:date/lomimscc:dateTime', NAMESPACE)
    text = None
    if contribute_date is not None:
        text = contribute_date.text
    data['contribute_date'] = text
    return data


def parse_organizations(node):
    data = []
    element = node.find('ims:organizations', NAMESPACE) or []
    data = [
        parse_organization(org_node)
        for org_node in element
    ]
    return data


def parse_organization(node):
    data = {}
    data['identifier'] = node.get('identifier')
    data['structure'] = node.get('structure')
    children = []
    for item_node in node:
        child = parse_item(item_node)
        if len(child):
            children.append(child)
    if len(children):
        data['children'] = children
    return data


def parse_item(node):
    data = {}
    identifier = node.get('identifier')
    if identifier:
        data['identifier'] = identifier
    identifierref = node.get('identifierref')
    if identifierref:
        data['identifierref'] = identifierref
    title = parse_text(node, 'ims:title')
    if title:
        data['title'] = title
    children = []
    for child in node:
        child_item = parse_item(child)
        if len(child_item):
            children.append(child_item)
    if children and len(children):
        data['children'] = children
    return data
