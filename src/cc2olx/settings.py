from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

LOG_FORMAT = "{%(filename)s:%(lineno)d} - %(message)s"

CONTENT_PROCESSORS = [
    "cc2olx.content_processors.VideoContentProcessor",
    "cc2olx.content_processors.LtiContentProcessor",
    "cc2olx.content_processors.QtiContentProcessor",
    "cc2olx.content_processors.DiscussionContentProcessor",
    "cc2olx.content_processors.HtmlContentProcessor",
]

USE_I18N = False
USE_TZ = False
