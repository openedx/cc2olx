import os.path
import re
import tarfile
import zipfile

from cc2olx import filesystem
from cc2olx.settings import collect_settings
from cc2olx.settings import MANIFEST


OLX_DIRECTORIES = [
    'about',
    'assets',
    'chapter',
    'course',
    'html',
    'info',
    'policies',
    'problem',
    'sequential',
    'static',
    'vertical',
]


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


class Cartridge:
    def __init__(self, cartridge_file):
        self.cartridge = zipfile.ZipFile(cartridge_file)
        self.metadata = None
        self.resources = None
        self.organizations = None
        self.version = '1.1'
        self.file_path = cartridge_file
        self.directory = None
        self.ns = {}

    def __repr__(self):
        filename = os.path.basename(self.file_path)
        text = '<{_class} version="{version}" file="{filename}" />'.format(
            _class=type(self).__name__,
            version=self.version,
            filename=filename,
        )
        return text

    def serialize(self):
        output_directory = self.directory + '-olx'
        course_directory = os.path.join(output_directory, 'course')
        for directory in OLX_DIRECTORIES:
            subdirectory = os.path.join(course_directory, directory)
            filesystem.create_directory(subdirectory)
        self.write_xml(self.get_course_xml(), course_directory, 'course.xml')
        output_filename = self.directory + '.tar.gz'
        with tarfile.open(output_filename, 'w:gz') as tar:
            tar.add(course_directory, arcname=os.path.basename(course_directory))

    def write_xml(self, text, output_base, output_file):
        text += '\n'
        output_path = os.path.join(output_base, output_file)
        with open(output_path, 'w') as output:
            output.write(text)

    def get_course_xml(self):
        text = '<course org="{org}" course="{number}" url_name="{run}" />'.format(
            org=self.get_course_org(),
            number=self.get_course_number(),
            run=self.get_course_run(),
        )
        return text

    def get_course_org(self):
        # TODO: find a better value for this
        return 'org'

    def get_course_number(self):
        # TODO: find a better value for this
        return 'number'

    def get_course_run(self):
        # TODO: find a better value for this; lifecycle.contribute_date?
        return 'run'

    def _extract(self):
        settings = collect_settings()
        workspace = settings['workspace']
        path_extracted = filesystem.unzip_directory(self.file_path, workspace)
        self.directory = path_extracted
        manifest = os.path.join(path_extracted, MANIFEST)
        return manifest

    def _update_namespaces(self, root):
        ns = re.match('\{(.*)\}', root.tag).group(1)
        version = re.match('.*/(imsccv\dp\d)/', ns).group(1)
        self.ns['ims'] = ns
        self.ns['lomimscc'] = "http://ltsc.ieee.org/xsd/{version}/LOM/manifest".format(
            version=version,
        )

    def load_manifest_extracted(self):
        manifest = self._extract()
        tree = filesystem.get_xml_tree(manifest)
        root = tree.getroot()
        self._update_namespaces(root)
        data = self.parse_manifest(root)
        self.metadata = data['metadata']
        self.organizations = data['organizations']
        self.resources = data['resources']
        self.version = self.metadata.get('schema', {}).get('version', self.version)
        return data

    def parse_manifest(self, node):
        data = dict()
        data['metadata'] = self.parse_metadata(node)
        data['organizations'] = self.parse_organizations(node)
        data['resources'] = self.parse_resources(node)
        return data

    def parse_metadata(self, node):
        data = dict()
        metadata = node.find('./ims:metadata', self.ns)
        if metadata:
            data['schema'] = self.parse_schema(metadata)
            data['lom'] = self.parse_lom(metadata)
        return data

    def parse_schema(self, node):
        schema_name = self.parse_schema_name(node)
        schema_version = self.parse_schema_version(node)
        data = {
            'name': schema_name,
            'version': schema_version,
        }
        return data

    def parse_schema_name(self, node):
        schema_name = node.find('./ims:schema', self.ns)
        schema_name = schema_name.text
        return schema_name

    def parse_schema_version(self, node):
        schema_version = node.find('./ims:schemaversion', self.ns)
        schema_version = schema_version.text
        return schema_version

    def parse_lom(self, node):
        data = dict()
        lom = node.find('lomimscc:lom', self.ns)
        if lom:
            data['general'] = self.parse_general(lom)
            data['lifecycle'] = self.parse_lifecycle(lom)
            data['rights'] = self.parse_rights(lom)
        return data

    def parse_general(self, node):
        data = {}
        general = node.find('lomimscc:general', self.ns)
        if general:
            data['title'] = self.parse_text(general, 'lomimscc:title/lomimscc:string')
            data['language'] = self.parse_text(general, 'lomimscc:language/lomimscc:string')
            data['description'] = self.parse_text(general, 'lomimscc:description/lomimscc:string')
            data['keywords'] = self.parse_keywords(general)
        return data

    def parse_text(self, node, lookup):
        text = None
        element = node.find(lookup, self.ns)
        if element is not None:
            text = element.text
        return text

    def parse_keywords(self, node):
        # TODO: keywords
        keywords = []
        return keywords

    def parse_rights(self, node):
        data = dict()
        element = node.find('lomimscc:rights', self.ns)
        if element:
            data['is_restricted'] = self.parse_text(
                element,
                'lomimscc:copyrightAndOtherRestrictions/lomimscc:value',
            )
            data['description'] = self.parse_text(
                element,
                'lomimscc:description/lomimscc:string',
            )
            # TODO: cost
        return data

    def parse_lifecycle(self, node):
        # TODO: role
        # TODO: entity
        data = dict()
        contribute_date = node.find(
            'lomimscc:lifeCycle/lomimscc:contribute/lomimscc:date/lomimscc:dateTime',
            self.ns
        )
        text = None
        if contribute_date is not None:
            text = contribute_date.text
        data['contribute_date'] = text
        return data

    def parse_organizations(self, node):
        data = []
        element = node.find('ims:organizations', self.ns) or []
        data = [
            self.parse_organization(org_node)
            for org_node in element
        ]
        return data

    def parse_organization(self, node):
        data = {}
        data['identifier'] = node.get('identifier')
        data['structure'] = node.get('structure')
        children = []
        for item_node in node:
            child = self.parse_item(item_node)
            if len(child):
                children.append(child)
        if len(children):
            data['children'] = children
        return data

    def parse_item(self, node):
        data = {}
        identifier = node.get('identifier')
        if identifier:
            data['identifier'] = identifier
        identifierref = node.get('identifierref')
        if identifierref:
            data['identifierref'] = identifierref
        title = self.parse_text(node, 'ims:title')
        if title:
            data['title'] = title
        children = []
        for child in node:
            child_item = self.parse_item(child)
            if len(child_item):
                children.append(child_item)
        if children and len(children):
            data['children'] = children
        return data

    def parse_resources(self, node):
        data = []
        element = node.find('ims:resources', self.ns) or []
        data = [
            self.parse_resource(sub_element)
            for sub_element in element
        ]
        return data

    def parse_resource(self, node):
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
                child_data = self.parse_file(child)
            elif tag == 'dependency':
                child_data = self.parse_dependency(child)
            elif tag == 'metadata':
                child_data = self.parse_resource_metadata(child)
            else:
                print('UNSUPPORTED RESOURCE TYPE', tag)
                continue
            if child_data:
                children.append(child_data)
        if children and len(children):
            data['children'] = children
        return data

    def parse_file(self, node):
        data = dict()
        href = node.get('href')
        resource = ResourceFile(href)
        return resource

    def parse_dependency(self, node):
        data = dict()
        identifierref = node.get('identifierref')
        resource = ResourceDependency(identifierref)
        return resource

    def parse_resource_metadata(self, node):
        # TODO: this
        return None
