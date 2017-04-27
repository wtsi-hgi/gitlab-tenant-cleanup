import logging
import os
import sys
from argparse import ArgumentParser

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from typing import List

from openstacktenantcleanup._sqlalchemy._models import SqlAlchemyModel
from openstacktenantcleanup._sqlalchemy.tracking import SqlTracker
from openstacktenantcleanup.configuration import parse_configuration, Configuration
from openstacktenantcleanup.planning import create_clean_up_plans, create_human_explanation, execute_plans
from openstacktenantcleanup.tracking import Tracker

_logger = logging.getLogger(__name__)


class CliConfiguration():
    """
    TODO
    """
    def __init__(self, dry_run: bool=False, config_location: str=None, run_once: bool=False):
        self.dry_run = dry_run
        self.config_location = config_location
        self.run_once = run_once


def parse_arguments(argument_list: List[str]) -> CliConfiguration:
    """
    TODO
    :return: 
    """
    parser = ArgumentParser(description="OpenStack Tenant Cleanup")
    parser.add_argument("-d", "--dry-run", default=False, action="store_true", help="Runs but does not delete anything")
    parser.add_argument("-s", "--single-run", default=False, action="store_true", help="Run once then stop")
    parser.add_argument("-c", "--config", type=str, help="Location of the configuration file")
    arguments = parser.parse_args(argument_list)
    return CliConfiguration(arguments.dry_run, arguments.config, arguments.single_run)


def run(configuration: Configuration, tracker: Tracker, dry_run: bool):
    """
    TODO
    :param configuration: 
    :param tracker: 
    :param dry_run: 
    :return: 
    """
    plans = create_clean_up_plans(configuration, tracker, dry_run=dry_run)
    _logger.info(create_human_explanation(plans))
    execute_plans(plans, configuration.general_configuration.max_simultaneous_deletes)

    print(create_human_explanation(plans))


def main():
    """
    TODO
    :return: 
    """
    cli_configuration = parse_arguments(sys.argv[1:])
    _logger.debug(f"CLI configuration: {cli_configuration}")
    configuration = parse_configuration(cli_configuration.config_location)
    _logger.debug(f"Program configuration: {configuration}")

    tracking_database = configuration.general_configuration.tracking_database
    if not os.path.exists(tracking_database):
        _logger.info(f"Creating tracking database: {tracking_database}")
        engine = create_engine(f"sqlite:///{tracking_database}")
        SqlAlchemyModel.metadata.create_all(bind=engine)

    tracker = SqlTracker(f"sqlite:///{tracking_database}")

    def job():
        run(configuration, tracker, cli_configuration.dry_run)

    if cli_configuration.run_once:
        job()
    else:
        scheduler = BlockingScheduler()
        scheduler.add_job(job, "interval", seconds=configuration.general_configuration.run_period.total_seconds())



if __name__ == "__main__":
    main()