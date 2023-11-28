import logging


class AbstractCommand:

    def __init__(self, arg_parser):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def run(self, args):
        self.args = args
        if self.args.verbose:
            self.logger.setLevel(logging.DEBUG)
