from typing import List, Type

from django.conf import settings
from django.utils.module_loading import import_string

from cc2olx.content_post_processors import AbstractContentPostProcessor


def load_content_post_processor_types() -> List[Type[AbstractContentPostProcessor]]:
    """
    Load content post processor types.
    """
    return [import_string(processor_path) for processor_path in settings.CONTENT_POST_PROCESSORS]
