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


def parse_manifest(node, ns):
    data = dict()
    data['metadata'] = parse_metadata(node, ns)
    data['organizations'] = parse_organizations(node, ns)
    data['resources'] = parse_resources(node, ns)
    return data


def parse_metadata(node, ns):
    data = dict()
    metadata = node.find('./ims:metadata', ns)
    if metadata:
        data['schema'] = parse_schema(metadata, ns)
        data['lom'] = parse_lom(metadata, ns)
        # parse_metadata_lom(metadata)
    return data


def parse_schema(node, ns):
    schema_name = parse_schema_name(node, ns)
    schema_version = parse_schema_version(node, ns)
    data = {
        'name': schema_name,
        'version': schema_version,
    }
    return data


def parse_schema_name(node, ns):
    schema_name = node.find('./ims:schema', ns)
    schema_name = schema_name.text
    return schema_name


def parse_schema_version(node, ns):
    schema_version = node.find('./ims:schemaversion', ns)
    schema_version = schema_version.text
    return schema_version


def parse_lom(node, ns):
    data = dict()
    lom = node.find('lomimscc:lom', ns)
    if lom:
        data['general'] = parse_general(lom, ns)
        data['lifecycle'] = parse_lifecycle(lom, ns)
        data['rights'] = parse_rights(lom, ns)
    return data


def parse_general(node, ns):
    data = {}
    general = node.find('lomimscc:general', ns)
    if general:
        data['title'] = parse_text(general, 'lomimscc:title/lomimscc:string', ns)
        data['language'] = parse_text(general, 'lomimscc:language/lomimscc:string', ns)
        data['description'] = parse_text(general, 'lomimscc:description/lomimscc:string', ns)
        data['keywords'] = parse_keywords(general, ns)
    return data


def parse_text(node, lookup, ns):
    text = None
    element = node.find(lookup, ns)
    if element is not None:
        text = element.text
    return text


def parse_keywords(node, ns):
    # TODO: keywords
    keywords = []
    return keywords


def parse_rights(node, ns):
    data = dict()
    element = node.find('lomimscc:rights', ns)
    if element:
        data['is_restricted'] = parse_text(
            element,
            'lomimscc:copyrightAndOtherRestrictions/lomimscc:value',
            ns,
        )
        data['description'] = parse_text(
            element,
            'lomimscc:description/lomimscc:string',
            ns,
        )
        # TODO: cost
    return data


def parse_lifecycle(node, ns):
    # TODO: role
    # TODO: entity
    data = dict()
    contribute_date = node.find('lomimscc:lifeCycle/lomimscc:contribute/lomimscc:date/lomimscc:dateTime', ns)
    text = None
    if contribute_date is not None:
        text = contribute_date.text
    data['contribute_date'] = text
    return data


def parse_organizations(node, ns):
    data = []
    element = node.find('ims:organizations', ns) or []
    data = [
        parse_organization(org_node, ns)
        for org_node in element
    ]
    return data


def parse_organization(node, ns):
    data = {}
    data['identifier'] = node.get('identifier')
    data['structure'] = node.get('structure')
    children = []
    for item_node in node:
        child = parse_item(item_node, ns)
        if len(child):
            children.append(child)
    if len(children):
        data['children'] = children
    return data


def parse_item(node, ns):
    data = {}
    identifier = node.get('identifier')
    if identifier:
        data['identifier'] = identifier
    identifierref = node.get('identifierref')
    if identifierref:
        data['identifierref'] = identifierref
    title = parse_text(node, 'ims:title', ns)
    if title:
        data['title'] = title
    children = []
    for child in node:
        child_item = parse_item(child, ns)
        if len(child_item):
            children.append(child_item)
    if children and len(children):
        data['children'] = children
    return data


def parse_resources(node, ns):
    data = []
    element = node.find('ims:resources', ns) or []
    data = [
        parse_resource(sub_element, ns)
        for sub_element in element
    ]
    return data


def parse_resource(node, ns):
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
            child_data = parse_file(child, ns)
        elif tag == 'dependency':
            child_data = parse_dependency(child, ns)
        elif tag == 'metadata':
            child_data = parse_resource_metadata(child, ns)
        else:
            print('UNSUPPORTED RESOURCE TYPE', tag)
            continue
        if child_data:
            children.append(child_data)
    if children and len(children):
        data['children'] = children
    return data


def parse_file(node, ns):
    data = dict()
    href = node.get('href')
    resource = ResourceFile(href)
    return resource


def parse_dependency(node, ns):
    data = dict()
    identifierref = node.get('identifierref')
    resource = ResourceDependency(identifierref)
    return resource


def parse_resource_metadata(node, ns):
    # TODO: this
    return None
