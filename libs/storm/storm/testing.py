from fixtures import Fixture

from storm.tracer import BaseStatementTracer, install_tracer, remove_tracer


class CaptureTracer(BaseStatementTracer, Fixture):
    """Trace SQL statements appending them to a C{list}.

    Example:

        with CaptureTracer() as tracer:
            # Run queries
        print tracer.queries  # Print the queries that have been run

    @note: This class requires the fixtures package to be available.
    """

    def __init__(self):
        super(CaptureTracer, self).__init__()
        self.queries = []

    def setUp(self):
        super(CaptureTracer, self).setUp()
        install_tracer(self)
        self.addCleanup(remove_tracer, self)

    def _expanded_raw_execute(self, conn, raw_cursor, statement):
        """Save the statement to the log."""
        self.queries.append(statement)
