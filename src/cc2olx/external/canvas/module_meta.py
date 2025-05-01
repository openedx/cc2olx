from cc2olx import filesystem
from cc2olx.logging import build_console_logger

console_logger = build_console_logger(__name__)


class ModuleMeta:
    def __init__(self, path):
        console_logger.info("Initializing module meta for Canvas flavored CC.")
        self.tree = filesystem.get_xml_tree(path)
        self.root = self.tree.getroot()
        self._init_modules()
        self._init_items()

    def _init_modules(self):
        """
        Extract all the <module> tags from module_meta
        """
        modules = {}
        for module in self.root.findall("module"):
            if module.attrib.get("identifier"):
                modules[module.attrib.get("identifier")] = module
        self.modules = modules

    def _init_items(self):
        """
        Extract all the <item> from modules
        """
        module_items = {}
        items = self.root.findall(".//{*}item")
        for item in items:
            if item.attrib.get("identifier"):
                module_items[item.attrib["identifier"]] = {
                    "title": getattr(item.find("./{*}title"), "text", None),
                    "content_type": item.find("./{*}content_type").text,
                    "identifierref": getattr(item.find("./{*}identifierref"), "text", None),
                    # ContextExternalTool type has url property
                    "url": getattr(item.find("./{*}url"), "text", None),
                }
        self.items = module_items

    def _get_item_data(self, identifier, content_type):
        """
        Returns the item data if item exists and the content_type
        matches given content_type.
        """
        item = self.items.get(identifier)
        if item and item["content_type"] == content_type:
            return item

    def get_external_tool_item_data(self, identifier):
        """
        Returns the item data if item exists and content_type is
        ContextExternalTool
        """
        return self._get_item_data(identifier, "ContextExternalTool")

    def get_item_by_id(self, identifier):
        """
        Get a module item given the identifier.
        """
        return self.items.get(identifier)

    def get_identifierref(self, identifier):
        """
        Get a item identifierref from identifier.
        """
        return self.items.get(identifier, {}).get("identifierref")

    def get_module_by_id(self, identifier):
        """
        Get a module from module identifier
        """
        return self.modules.get("identifier")
