import logging

from cc2olx.settings import collect_settings


if __name__ == '__main__':
    settings = collect_settings()
    logging.basicConfig(**settings['logging_config'])
    logger = logging.getLogger()
    for input_file in settings['input_files']:
        logger.info("Processing file: %s", input_file)
