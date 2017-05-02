import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from typing import List

from openstacktenantcleaner.common import get_absolute_path_relative_to
from openstacktenantcleaner._sqlalchemy._models import SqlAlchemyModel
from openstacktenantcleaner._sqlalchemy.tracking import SqlTracker
from openstacktenantcleaner.configuration import parse_configuration, Configuration, LoggingConfiguration
from openstacktenantcleaner.planning import create_clean_up_plans, create_human_explanation, execute_plans
from openstacktenantcleaner.tracking import Tracker

# TODO: these should be configurable
MAX_LOG_FILE_SIZE_IN_BYTES = 100 * 1024 * 1024
BACKUP_LOG_COUNT = 3

# XXX: __name__ here is set to "__main__", therefore cannot use _logger = logging.getLogger(__name__)
_logger = logging.getLogger(".".join(__file__.split(os.path.sep)[-2:]).rstrip(".py"))

_global_run_counter = 0


class _CliConfiguration():
    """
    CLI configuration.
    """
    def __init__(self, dry_run: bool=False, configuration_location: str=None, run_once: bool=False):
        self.dry_run = dry_run
        self.configuration_location = configuration_location
        self.run_once = run_once


def _parse_arguments(argument_list: List[str]) -> _CliConfiguration:
    """
    Parse the given CLI arguments.
    :return: CLI arguments
    """
    parser = ArgumentParser(description="OpenStack Tenant Cleanup")
    parser.add_argument("-d", "--dry-run", default=False, action="store_true", help="runs but does not delete anything")
    parser.add_argument("-s", "--single-run", default=False, action="store_true", help="run once then stop")
    parser.add_argument("config", metavar="configuration_location", type=str, help="location of the configuration file")
    arguments = parser.parse_args(argument_list)
    return _CliConfiguration(arguments.dry_run, arguments.config, arguments.single_run)


def _configure_logging(logging_configuration: LoggingConfiguration):
    """
    Configures logging using the given configuration.
    :param logging_configuration: the logging configuration
    """
    # XXX: There must be a cleaner way of getting the package name. `__package__ is None`
    logger = logging.getLogger(__file__.split(os.path.sep)[-2])

    file_handler = RotatingFileHandler(logging_configuration.location, maxBytes=MAX_LOG_FILE_SIZE_IN_BYTES,
                                       backupCount=BACKUP_LOG_COUNT)
    file_handler.setLevel(logging_configuration.level)
    logger.addHandler(file_handler)

    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.DEBUG)


def run(configuration: Configuration, tracker: Tracker, dry_run: bool):
    """
    Run the cleanup.
    :param configuration: cleanup configuration
    :param tracker: OpenStack item history tracker
    :param dry_run: whether to run without actually deleting anything
    """
    global _global_run_counter
    _global_run_counter += 1
    _logger.info(f"Starting run cycle {_global_run_counter}...")

    try:
        plans = create_clean_up_plans(configuration, tracker, dry_run=dry_run)
        _logger.info(create_human_explanation(plans))
        execute_plans(plans, configuration.general_configuration.max_simultaneous_deletes)
    except Exception as e:
        _logger.error(e)
        raise


def run_periodically(configuration: Configuration, tracker: Tracker, dry_run: bool):
    """
    Runs the cleanup periodically.
    :param configuration: cleanup configuration
    :param tracker: OpenStack item history tracker
    :param dry_run: whether to run without actually deleting anything
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(run, args=(configuration, tracker, dry_run),
                      trigger="interval", seconds=configuration.general_configuration.run_period.total_seconds(),
                      coalesce=True, max_instances=1, next_run_time=datetime.now())
    scheduler.start()


def main():
    """
    Entry-point.
    """
    cli_configuration = _parse_arguments(sys.argv[1:])
    _logger.debug(f"CLI configuration: {cli_configuration}")
    configuration = parse_configuration(cli_configuration.configuration_location)
    _configure_logging(configuration.general_configuration.logging_configuration)
    _logger.debug(f"Program configuration: {configuration}")

    tracking_database = configuration.general_configuration.tracking_database
    if not os.path.isabs(tracking_database):
        tracking_database = get_absolute_path_relative_to(tracking_database, cli_configuration.configuration_location)
    if not os.path.exists(tracking_database):
        _logger.info(f"Creating tracking database: {tracking_database}")
        engine = create_engine(f"sqlite:///{tracking_database}")
        SqlAlchemyModel.metadata.create_all(bind=engine)

    tracker = SqlTracker(f"sqlite:///{tracking_database}")

    execute = run if cli_configuration.run_once else run_periodically
    execute(configuration, tracker, cli_configuration.dry_run)


if __name__ == "__main__":
    main()
