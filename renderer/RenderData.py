from threaddump.Analizer import ThreadDumpsWithRecurringThreads, LongRunningThread


class RenderDataForFile:
    def __init__(self, file: str, thread_dumps_with_recurring_threads: list[ThreadDumpsWithRecurringThreads],
                 long_running_threads: list[LongRunningThread]):
        self.thread_dumps_with_recurring_threads = thread_dumps_with_recurring_threads
        self.long_running_threads = long_running_threads
        self.file = file


class RenderData:
    def __init__(self, render_data_for_files: list[RenderDataForFile]):
        self.render_data_for_files = render_data_for_files
