NAMESPACE = {
    'ims': 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1',
    'lomimscc': 'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest',
}


class ResourceFile:
    def __init__(self, href):
        self.href = href

    def __repr__(self):
        return "<ResourceFile href={href} />".format(
            href=self.href,
	)


class ResourceDependency:
    def __init__(self, identifierref):
        self.identifierref = identifierref

    def __repr__(self):
        return "<ResourceDependency identifierref={identifierref} />".format(
            identifierref=self.identifierref,
	)


def parse_manifest(node):
    data = dict()
    data['metadata'] = parse_metadata(node)
    data['organizations'] = parse_organizations(node)
    data['resources'] = parse_resources(node)
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


def parse_resources(node):
    data = []
    element = node.find('ims:resources', NAMESPACE) or []
    data = [
        parse_resource(sub_element)
        for sub_element in element
    ]
    return data


def parse_resource(node):
    data = {}
    identifier = node.get('identifier')
    if identifier:
        data['identifier'] = identifier
    _type = node.get('type')
    if _type:
        data['type'] = _type
    href = node.get('href')
    if href:
        data['href'] = href
    intended_use = node.get('intended_use')
    if intended_use:
        data['intended_use'] = intended_use
    children = []
    for child in node:
        prefix, has_namespace, postfix = child.tag.partition('}')
        tag = postfix
        if tag == 'file':
            child_data = parse_file(child)
        elif tag == 'dependency':
            child_data = parse_dependency(child)
        elif tag == 'metadata':
            child_data = parse_resource_metadata(child)
        else:
            print('UNSUPPORTED RESOURCE TYPE', tag)
            continue
        if child_data:
            children.append(child_data)
    if children and len(children):
        data['children'] = children
    return data


def parse_file(node):
    data = dict()
    href = node.get('href')
    resource = ResourceFile(href)
    return resource


def parse_dependency(node):
    data = dict()
    identifierref = node.get('identifierref')
    resource = ResourceDependency(identifierref)
    return resource


def parse_resource_metadata(node):
    # TODO: this
    return None
