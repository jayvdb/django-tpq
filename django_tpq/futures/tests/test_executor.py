from django.core.management import call_command
from django.test import TransactionTestCase

from futures.decorators import future
from futures.models import FutureStat


@future()
def foo(a, b):
    return a + b


# We use TransactionTestCase to ensure our queue is visible to another
# connection/thread/process.
class TestExecutor(TransactionTestCase):
    """
    Test executor command.

    Basically a full-stack test. We declare a future using our decorator, write
    it to an actual queue, execute it with the Django management command, then
    verify the result. We also check that stats are properly updated for the
    future.
    """
    def test_command(self):
        # Queue up a future.
        r = foo.async(3, 9)

        # Execute it.
        call_command('futures_executor', restart=False, workers=1, limit=1)

        # Make sure our function was called.
        self.assertEqual(12, r.result())

        stat = FutureStat.objects.get(name=foo.name)
        self.assertEqual(1, stat.total)
        self.assertEqual(0, stat.running)
