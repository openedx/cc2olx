from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

LOG_FORMAT = "{%(filename)s:%(lineno)d} - %(message)s"

CUSTOM_BLOCKS_CONTENT_PROCESSORS = [
    "cc2olx.content_processors.PDFContentProcessor",
]

# It is used to specify content processors applied to Common Cartridge
# resources. The processors are iterated over in turn, find out whether they
# can process a resource and provide a parsed result if succeeded. The
# iteration is stopped if the processor returns parsed result, otherwise the
# execution flow is passed to the next processor. Thus, the processors' order
# is important: the specific processors should be placed first, the fallback
# ones - at the end.
CONTENT_PROCESSORS = [
    *CUSTOM_BLOCKS_CONTENT_PROCESSORS,
    "cc2olx.content_processors.VideoContentProcessor",
    "cc2olx.content_processors.LtiContentProcessor",
    "cc2olx.content_processors.QtiContentProcessor",
    "cc2olx.content_processors.AssignmentContentProcessor",
    "cc2olx.content_processors.DiscussionContentProcessor",
    "cc2olx.content_processors.HtmlContentProcessor",
]

# It is used to modify the generated OLX node from a Common Cartridge resource.
# Post processors are called sequentially, so the next post processors work
# with nodes modified by the previous one. It means that the order is important,
CONTENT_POST_PROCESSORS = ["cc2olx.content_post_processors.StaticLinkPostProcessor"]

USE_I18N = False
USE_TZ = False
