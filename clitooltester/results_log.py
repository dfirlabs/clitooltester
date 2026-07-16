"""Results log."""

from datetime import datetime


class ResultsLog:
    """Results log."""

    def __init__(self, path):
        """Initializes a results log.

        Args:
          path (str): path of the log file.
        """
        super().__init__()
        self._path = path

    def _FormatDuration(self, nanoseconds):
        """Formats a duration.

        Args:
          nanoseconds (int): duration in nanosecond.

        Returns:
          str: formatted duration.
        """
        if nanoseconds < 1_000:
            return f"{nanoseconds:d} ns"

        if nanoseconds < 1_000_000:
            microseconds = nanoseconds / 1_000
            return f"{microseconds:.2f} µs"

        if nanoseconds < 1_000_000_000:
            milliseconds = nanoseconds / 1_000_000
            return f"{milliseconds:.2f} ms"

        seconds = nanoseconds / 1_000_000_000
        return f"{seconds:.4f} sec"

    def Write(self, test_results):
        """Writes test results to a log file.

        Args:
          test_results (list[TestResult]): test results.
        """
        first_test_result = min(test_results, key=lambda result: result.start_time)
        last_test_result = max(test_results, key=lambda result: result.end_time)

        with open(self._path, "w", encoding="utf-8") as file_object:
            timestamp = first_test_result.start_time / 1_000_000_000
            date_time = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            file_object.write(f"Started at: {date_time:s}\n")

            for result in sorted(
                test_results, key=lambda result: result.sequence_number
            ):
                if result.exit_code == 0:
                    status = "ok"
                else:
                    status = "FAILED"

                duration = self._FormatDuration(result.end_time - result.start_time)
                file_object.write(
                    f"{result.sequence_number:d}. {result.description:s}: {status:s} "
                    f"({duration:s})\n"
                )

            timestamp = last_test_result.end_time / 1_000_000_000
            date_time = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            file_object.write(f"Ended at: {date_time:s}\n")
