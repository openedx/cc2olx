import os.path
import re
import tarfile
from textwrap import dedent
import zipfile

from cc2olx import filesystem
from cc2olx.settings import collect_settings
from cc2olx.settings import MANIFEST


DIFFUSE_SHALLOW_SECTIONS = False
DIFFUSE_SHALLOW_SUBSECTIONS = True


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


def is_leaf(container):
    return 'identifierref' in container


def has_only_leaves(container):
    return all(is_leaf(child) for child in container.get('children', []))


def pprint(level, key, value, count=0):
    text = "{spaces}|--> {key}({count}) {value} {title}".format(
        spaces='    '*level,
        key=key,
        value=value['identifier'],
        count=count,
        title=value.get('title', 'none'),
    )
    print(text)


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
        self.normalized = None
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
        run_file = "course/{run}.xml".format(run=self.get_course_run())
        self.write_xml(self.get_run_xml(), course_directory, run_file)
        output_filename = self.directory + '.tar.gz'
        with tarfile.open(output_filename, 'w:gz') as tar:
            tar.add(course_directory, arcname=os.path.basename(course_directory))

    def normalize(self):
        organizations = self.organizations
        count_organizations = len(organizations)
        if count_organizations == 0:
            # This is allowed by the spec.
            # But what do we do?
            # Should we build course content out of resources?
            # -> Mock a flattened section/subsection hierarchy?
            # -> Create a custom course tab(s)?
            # -> Dump links on the about page?
            organization = None
        elif count_organizations == 1:
            # This is allowed by the spec.
            organization = organizations[0]
        else:
            # This is _NOT_ allowed by the spec.
            # We could fall over, but let's just take the first...
            organization = organizations[0]
        if not organization:
            return
        identifier = organization.get('identifier', 'org_1')
        structure = organization.get('structure', 'rooted-hierarchy')
        # An organization may have a title element.
        title = None
        # An organization may have 0 or 1 item.
        # We'll treat it as the courseware root.
        course_root = organization.get('children', [])
        # Question: Does it have it have identifier="LearningModules"?
        count_root = len(course_root)
        if count_root == 0:
            # What to do?
            course_root = None
        elif count_root == 1:
            course_root = course_root[0]
        else:
            # What to do?
            # For now, just take the first.
            course_root = course_root[0]
        if not course_root:
            return
        sections = course_root.get('children', [])
        print(
            "course({count})".format(
                count=len(sections),
            )
        )
        normal_course = {
            'children': [],
            'identifier': identifier,
            'structure': 'rooted-hierarchy',
        }
        for section in sections:
            if is_leaf(section):
                # Structure is too shallow.
                # Found leaf at section level.
                subsections = [
                    section,
                ]
            elif has_only_leaves(section):
                # Structure is too shallow.
                # Found only leaves inside section.
                if DIFFUSE_SHALLOW_SECTIONS:
                    subsections = [
                        {
                            'identifier': 'x'*34,
                            'title': 'none',
                            'children': [
                                subsection,
                            ],
                        }
                        for subsection in section.get('children', [])
                    ]
                else:
                    subsections = [
                        {
                            'identifier': 'x'*34,
                            'title': 'none',
                            'children': section.get('children', []),
                        },
                    ]
            else:
                subsections = section.get('children', [])
            pprint(0, 'section', section, len(subsections))
            normal_section = {
                'children': [],
                'identifier': section.get('identifier'),
                'identifierref': section.get('identifierref'),
            }
            for subsection in subsections:
                if is_leaf(subsection):
                    # Structure is too shallow.
                    # Found leaf at subsection level.
                    units = [
                        subsection,
                    ]
                elif has_only_leaves(subsection):
                    # Structure is too shallow.
                    # Found only leaves inside subsection.
                    if DIFFUSE_SHALLOW_SUBSECTIONS:
                        units = [
                            {
                                'identifier': 'x'*34,
                                'title': 'none',
                                'children': [
                                    unit,
                                ],
                            }
                            for unit in subsection.get('children', [])
                        ]
                    else:
                        units = [
                            {
                                'identifier': 'x'*34,
                                'title': 'none',
                                'children': subsection.get('children', []),
                            },
                        ]
                else:
                    units = subsection.get('children', [])
                pprint(1, 'subsection', subsection, len(units))
                normal_subsection = {
                    'children': [],
                    'identifier': subsection.get('identifier'),
                    'identifierref': subsection.get('identifierref'),
                }
                for unit in units:
                    if is_leaf(unit):
                        # Structure is too shallow.
                        # Found leaf at unit level.
                        components = [
                            unit,
                        ]
                    else:
                        components = unit.get('children', [])
                        components = self.flatten(components)
                    pprint(2, 'unit', unit, len(components))
                    normal_unit = {
                        'children': [],
                        'identifier': unit.get('identifier'),
                        'identifierref': unit.get('identifierref'),
                    }
                    for component in components:
                        pprint(3, 'component', component)
                        normal_unit['children'].append(component)
                    normal_subsection['children'].append(normal_unit)
                normal_section['children'].append(normal_subsection)
            normal_course['children'].append(normal_section)
        self.normalized = normal_course
        return normal_course

    def flatten(self, container):
        if is_leaf(container):
            return container
        if isinstance(container, list):
            children = container
        else:
            # Structure is too deep.
            # Flatten into current unit?
            # Found non-leaf at component level
            children = container.get('children', [])
        output = []
        for child in children:
            if is_leaf(child):
                output.append(child)
            else:
                leaves = self.flatten(child)
                output.extend(leaves)
        return output

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

    def get_run_xml(self):
        text = dedent("""\
            <course
                display_name="{title}"
                language="{language}"
            >
            </course>\
        """).format(
            title=self.get_title(),
            language=self.get_language(),
        ).strip()
        return text

    def get_title(self):
        # TODO: Choose a better default course title
        title = self.metadata.get('lom', {}).get('general', {}).get('title') or 'Default Course Title'
        return title

    def get_language(self):
        # TODO: ensure the type of language code in the metadata
        title = self.metadata.get('lom', {}).get('general', {}).get('language') or 'en'
        return title

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
