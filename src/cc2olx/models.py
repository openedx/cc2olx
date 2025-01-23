import logging
import os.path
import re
import zipfile
from pathlib import Path
from textwrap import dedent
from typing import Optional

from cc2olx import filesystem
from cc2olx.dataclasses import OlxToOriginalStaticFilePaths
from cc2olx.external.canvas import ModuleMeta
from cc2olx.utils import clean_file_name

logger = logging.getLogger()

MANIFEST = "imsmanifest.xml"

# canvas-cc course settings
COURSE_SETTINGS_DIR = "course_settings"
MODULE_META = "module_meta.xml"
CANVAS_REPORT = "canvas_export.txt"

DIFFUSE_SHALLOW_SECTIONS = False
DIFFUSE_SHALLOW_SUBSECTIONS = True


def is_leaf(container):
    return "identifierref" in container


def has_only_leaves(container):
    return all(is_leaf(child) for child in container.get("children", []))


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
    def __init__(self, cartridge_file, workspace):
        self.cartridge = zipfile.ZipFile(str(cartridge_file))
        self.metadata = None
        self.resources = None
        self.resources_by_id = {}
        self.organizations = None
        self.normalized = None
        self.version = "1.1"
        self.file_path = cartridge_file
        self.directory = None
        self.ns = {}
        # map by identifier from `course_setting/module_meta.xml`
        self.is_canvas_flavor = False
        self.module_meta = {}

        self.olx_to_original_static_file_paths = OlxToOriginalStaticFilePaths()

        self.workspace = workspace

    def __repr__(self):
        filename = os.path.basename(self.file_path)
        text = '<{_class} version="{version}" file="{filename}" />'.format(
            _class=type(self).__name__,
            version=self.version,
            filename=filename,
        )
        return text

    def process_canvas_cc(self, elements):
        """
        Perform canvas cc specific processing.

        Ex: collapse related items when ContextModuleSubHeader is present.
        """

        def collapse_sub_headers(item):
            """
            Recursive helper function to collapse related items under subheader.
            """
            if item.get("children"):
                item_children = []
                # track ContextModuleSubHeader.
                collapse_to = None
                for child in item.get("children", []):
                    # process each child recusively
                    child = collapse_sub_headers(child)

                    meta = self.module_meta.get_item_by_id(child.get("identifier"))
                    if meta and meta.get("content_type") == "ContextModuleSubHeader":
                        # if there is a sub header, track it
                        collapse_to = child
                        # set `children` property for subheader if not set already
                        collapse_to["children"] = collapse_to.get("children", [])
                        item_children.append(collapse_to)
                    else:
                        if collapse_to:
                            # if subheader exists, append consecutive items to it's children property
                            collapse_to["children"].append(child)
                        else:
                            # no subheader, append to item
                            item_children.append(child)

                # reset current item's children property
                item["children"] = item_children
            return item

        elements = [collapse_sub_headers(item) for item in elements]
        return elements

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
        identifier = organization.get("identifier", "org_1")
        # An organization may have 0 or 1 item.
        # We'll treat it as the courseware root.
        course_root = organization.get("children", [])
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

        sections = course_root.get("children", [])

        if self.is_canvas_flavor:
            # If this file exported via canvas-cc, process module meta.
            sections = self.process_canvas_cc(sections)

        normal_course = {
            "children": [],
            "identifier": identifier,
            "structure": "rooted-hierarchy",
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
                            "identifier": "x" * 34,
                            "title": "none",
                            "children": [
                                subsection,
                            ],
                        }
                        for subsection in section.get("children", [])
                    ]
                else:
                    subsections = [
                        {
                            "identifier": "x" * 34,
                            "title": "none",
                            "children": section.get("children", []),
                        },
                    ]
            else:
                subsections = section.get("children", [])
            normal_section = {
                "children": [],
                "identifier": section.get("identifier"),
                "identifierref": section.get("identifierref"),
                "title": section.get("title"),
            }
            if len(subsections) == 1:
                subsect = subsections[0]
                if subsect.get("title", "none") == "none":
                    subsect["title"] = section.get("title", "none")
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
                                "identifier": "x" * 34,
                                "title": unit.get("title", "none"),
                                "children": [
                                    unit,
                                ],
                            }
                            for unit in subsection.get("children", [])
                        ]
                    else:
                        units = [
                            {
                                "identifier": "x" * 34,
                                "title": "none",
                                "children": subsection.get("children", []),
                            },
                        ]
                else:
                    units = subsection.get("children", [])
                normal_subsection = {
                    "children": [],
                    "identifier": subsection.get("identifier"),
                    "identifierref": subsection.get("identifierref"),
                    "title": subsection.get("title"),
                }
                for unit in units:
                    if is_leaf(unit):
                        # Structure is too shallow.
                        # Found leaf at unit level.
                        components = [
                            unit,
                        ]
                    else:
                        components = unit.get("children", [])
                        components = self.flatten(components)
                    normal_unit = {
                        "children": [],
                        "identifier": unit.get("identifier"),
                        "identifierref": unit.get("identifierref"),
                        "title": unit.get("title"),
                    }
                    for component in components:
                        normal_unit["children"].append(component)
                    normal_subsection["children"].append(normal_unit)
                normal_section["children"].append(normal_subsection)
            normal_course["children"].append(normal_section)
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
            children = container.get("children", [])
        output = []
        for child in children:
            if is_leaf(child):
                output.append(child)
            else:
                leaves = self.flatten(child)
                output.extend(leaves)
        return output

    def define_resource(self, idref: Optional[str]) -> dict:
        """
        Define a resource by its identifier.
        """
        resource = self.resources_by_id.get(idref)
        if resource is None and self.is_canvas_flavor:
            module_item_idref = self.module_meta.get_identifierref(idref)
            resource = self.resources_by_id.get(module_item_idref)
        return resource

    def load_manifest_extracted(self):
        manifest = self._extract()

        # load module_meta
        self.is_canvas_flavor = self._check_if_canvas_flavor()
        if self.is_canvas_flavor:
            self.module_meta = self._load_module_meta()

        tree = filesystem.get_xml_tree(manifest)
        root = tree.getroot()
        self._update_namespaces(root)
        self._clean_manifest(root)
        data = self._parse_manifest(root)
        self.metadata = data["metadata"]
        self.organizations = data["organizations"]
        self.resources = data["resources"]
        self.resources_by_id = {r["identifier"]: r for r in self.resources}

        # Keep a map with href -> identifier mapping. Used when processing statics.
        self.resource_id_by_href = {r["href"]: r["identifier"] for r in self.resources if "href" in r}

        self.version = self.metadata.get("schema", {}).get("version", self.version)
        return data

    def get_course_xml(self):
        text = '<course org="{org}" course="{number}" url_name="{run}" />'.format(
            org=self.get_course_org(),
            number=self.get_course_number(),
            run=self.get_course_run(),
        )
        return text

    def get_run_xml(self):
        text = (
            dedent(
                """\
            <course
                display_name="{title}"
                language="{language}"
            >
            </course>\
        """
            )
            .format(
                title=self.get_title(),
                language=self.get_language(),
            )
            .strip()
        )
        return text

    def get_title(self):
        # TODO: Choose a better default course title
        title = self.metadata.get("lom", {}).get("general", {}).get("title") or "Default Course Title"
        return title

    def get_language(self):
        # TODO: ensure the type of language code in the metadata
        title = self.metadata.get("lom", {}).get("general", {}).get("language") or "en"
        return title

    def get_course_org(self):
        # TODO: find a better value for this
        return "org"

    def get_course_number(self):
        # TODO: find a better value for this
        return "number"

    def get_course_run(self):
        # TODO: find a better value for this; lifecycle.contribute_date?
        return "run"

    def build_resource_file_path(self, file_name: str) -> Path:
        """
        Build the resource file path.
        """
        return self.directory / file_name

    def _extract(self):
        path_extracted = filesystem.unzip_directory(self.file_path, self.workspace)
        self.directory = path_extracted
        manifest = path_extracted / MANIFEST
        return manifest

    def _check_if_canvas_flavor(self):
        """
        Checks if the current file is exported from canvas.
        """
        canvas_export_path = self.directory / COURSE_SETTINGS_DIR / CANVAS_REPORT
        return os.path.exists(canvas_export_path)

    def _load_module_meta(self):
        """
        Load module meta from course settings if exists
        """
        module_meta_path = self.directory / COURSE_SETTINGS_DIR / MODULE_META
        module_meta = ModuleMeta(module_meta_path)
        return module_meta

    def _update_namespaces(self, root):
        ns = re.match(r"\{(.*)\}", root.tag).group(1)
        version = re.match(r".*/(imsccv\dp\d)/", ns).group(1)

        self.ns["ims"] = ns
        self.ns["lomimscc"] = "http://ltsc.ieee.org/xsd/{version}/LOM/manifest".format(
            version=version,
        )

    def _parse_manifest(self, node):
        return {
            "metadata": self._parse_metadata(node),
            "organizations": self._parse_organizations(node),
            "resources": self._parse_resources(node),
        }

    def _clean_manifest(self, node):
        """
        Update filepaths in the manifest, as they may contain special characters not recognized by Windows OS.
        When extracting files from the IMSCC file, we rename them to not contain the reserved characters. Therefore
        we also need to update references to the old filenames in the manifest.
        """
        if len(node) == 0:
            return

        for child in node:
            href = child.get("href")
            if href:
                cleaned_name = clean_file_name(href)
                child.set("href", cleaned_name)

            self._clean_manifest(child)

    def _parse_metadata(self, node):
        data = dict()
        metadata = node.find("./ims:metadata", self.ns)
        if metadata is not None:
            data["schema"] = self._parse_schema(metadata)
            data["lom"] = self._parse_lom(metadata)
        return data

    def _parse_schema(self, node):
        schema_name = self._parse_schema_name(node)
        schema_version = self._parse_schema_version(node)
        data = {
            "name": schema_name,
            "version": schema_version,
        }
        return data

    def _parse_schema_name(self, node):
        schema_name = node.find("./ims:schema", self.ns)
        schema_name = schema_name.text
        return schema_name

    def _parse_schema_version(self, node):
        schema_version = node.find("./ims:schemaversion", self.ns)
        schema_version = schema_version.text
        return schema_version

    def _parse_lom(self, node):
        data = dict()
        lom = node.find("lomimscc:lom", self.ns)
        if lom is not None:
            data["general"] = self._parse_general(lom)
            data["lifecycle"] = self._parse_lifecycle(lom)
            data["rights"] = self._parse_rights(lom)
        return data

    def _parse_general(self, node):
        data = {}
        general = node.find("lomimscc:general", self.ns)
        if general is not None:
            data["title"] = self._parse_text(general, "lomimscc:title/lomimscc:string")
            data["language"] = self._parse_text(general, "lomimscc:language/lomimscc:string")
            data["description"] = self._parse_text(general, "lomimscc:description/lomimscc:string")
            data["keywords"] = self._parse_keywords(general)
        return data

    def _parse_text(self, node, lookup):
        text = None
        element = node.find(lookup, self.ns)
        if element is not None:
            text = element.text
        return text

    def _parse_keywords(self, node):
        # TODO: keywords
        keywords = []
        return keywords

    def _parse_rights(self, node):
        data = dict()
        element = node.find("lomimscc:rights", self.ns)
        if element is not None:
            data["is_restricted"] = self._parse_text(
                element,
                "lomimscc:copyrightAndOtherRestrictions/lomimscc:value",
            )
            data["description"] = self._parse_text(
                element,
                "lomimscc:description/lomimscc:string",
            )
            # TODO: cost
        return data

    def _parse_lifecycle(self, node):
        # TODO: role
        # TODO: entity
        data = dict()
        contribute_date = node.find("lomimscc:lifeCycle/lomimscc:contribute/lomimscc:date/lomimscc:dateTime", self.ns)
        text = None
        if contribute_date is not None:
            text = contribute_date.text
        data["contribute_date"] = text
        return data

    def _parse_organizations(self, node):
        org_nodes = node.find("ims:organizations", self.ns)

        if not len(org_nodes):
            org_nodes = []

        data = [self._parse_organization(org_node) for org_node in org_nodes]
        return data

    def _parse_organization(self, node):
        data = {
            "identifier": node.get("identifier"),
            "structure": node.get("structure"),
        }
        children = []
        for item_node in node:
            child = self._parse_item(item_node)
            if len(child):
                children.append(child)
        if len(children):
            data["children"] = children
        return data

    def _parse_item(self, node):
        data = {}
        identifier = node.get("identifier")
        if identifier:
            data["identifier"] = identifier
        identifierref = node.get("identifierref")
        if identifierref:
            data["identifierref"] = identifierref
        title = self._parse_text(node, "ims:title")
        if title:
            data["title"] = title
        children = []
        for child in node:
            child_item = self._parse_item(child)
            if len(child_item):
                children.append(child_item)
        if children and len(children):
            data["children"] = children
        return data

    def _parse_resources(self, node):
        resource_nodes = node.find("ims:resources", self.ns)

        if not len(resource_nodes):
            resource_nodes = []

        data = [self._parse_resource(resource_node) for resource_node in resource_nodes]
        return data

    def _parse_resource(self, node):
        data = {}
        identifier = node.get("identifier")
        if identifier:
            data["identifier"] = identifier
        _type = node.get("type")
        if _type:
            data["type"] = _type
        href = node.get("href")
        if href:
            data["href"] = href
        intended_use = node.get("intended_use")
        if intended_use:
            data["intended_use"] = intended_use
        children = []
        for child in node:
            prefix, has_namespace, postfix = child.tag.partition("}")
            tag = postfix
            if tag == "file":
                child_data = self._parse_file(child)
            elif tag == "dependency":
                child_data = self._parse_dependency(child)
            elif tag == "metadata":
                child_data = self._parse_resource_metadata(child)
            else:
                logger.info("Unsupported Resource Type %s", tag)
                continue
            if child_data:
                children.append(child_data)
        if children and len(children):
            data["children"] = children
        return data

    def _parse_file(self, node):
        href = node.get("href")
        resource = ResourceFile(href)
        return resource

    def _parse_dependency(self, node):
        identifierref = node.get("identifierref")
        resource = ResourceDependency(identifierref)
        return resource

    def _parse_resource_metadata(self, node):
        # TODO: this
        return None
