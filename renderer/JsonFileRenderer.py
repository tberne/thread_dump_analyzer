from renderer.FileRenderer import FileRenderer
import json
from renderer.RenderData import RenderData, RenderDataForFile, ThreadDumpsWithRecurringThreads, LongRunningThread
from threaddump.Analizer import StackFrame


def __render_stacktrace__(stacktrace: list[StackFrame]) -> str:
    message = "\"stacktrace\": ["
    for stack_frame in stacktrace:
        message += f'"{str(stack_frame)}",'

    if len(stacktrace) > 0:
        message = message[:-1]

    message += "]"
    return message


def __render_long_running_thread__(long_running_thread: LongRunningThread) -> str:
    message = "{"
    message += f'"thread": "{str(long_running_thread.thread)}",'
    message += f'"duration": "{long_running_thread.duration}",'
    message += f'"first_apparition": "{long_running_thread.first_apparition}",'
    message += f'"last_apparition": "{long_running_thread.last_apparition}",'
    message += __render_stacktrace__(long_running_thread.thread.stacktrace)
    message += "}"
    return message


def __render_long_running_threads__(long_running_threads: list[LongRunningThread]) -> str:
    message = '"long_running_threads":['
    first = True
    for long_running_thread in long_running_threads:
        if not first:
            message += ","
        message += __render_long_running_thread__(long_running_thread)
        first = False

    message += "]"
    return message


def __render_thread_dump_recurring_threads__(
        thread_dump_with_recurring_threads: ThreadDumpsWithRecurringThreads) -> str:
    message = f'"{thread_dump_with_recurring_threads.thread_dump_date}":{{'
    message += f'"threads":['
    first = True
    for recurring_thread in thread_dump_with_recurring_threads.threads_with_recurring_stacktrace:
        if not first:
            message += ","
        message += "{"
        message += f'"recurring_threads":['
        first_recurring_thread = True
        for thread in recurring_thread.threads:
            if not first_recurring_thread:
                message += ","
            message += f'"{str(thread)}"'
            first_recurring_thread = False
        message += "],"
        message += __render_stacktrace__(recurring_thread.recurring_stacktrace)
        message += "}"
        first = False
    message += "]"
    message += "}"
    return message


def __render_thread_dumps_with_recurring_threads__(
        thread_dumps_with_recurring_threads: list[ThreadDumpsWithRecurringThreads]) -> str:
    message = '"thread_dumps_with_recurring_threads": {'
    first = True
    for thread_dump_with_recurring_threads in thread_dumps_with_recurring_threads:
        if not first:
            message += ","
        message += __render_thread_dump_recurring_threads__(thread_dump_with_recurring_threads)
        first = False

    message += "}"
    return message


def __render_data_for_file__(render_data_for_file: RenderDataForFile) -> str:
    message = f'"{render_data_for_file.file}": {{'
    message += __render_long_running_threads__(render_data_for_file.long_running_threads)
    message += ","
    message += __render_thread_dumps_with_recurring_threads__(render_data_for_file.thread_dumps_with_recurring_threads)
    message += "}"
    return message


class JsonFileRenderer(FileRenderer):
    def __init__(self, config):
        super().__init__(config)

    def render_string(self, renderer_data) -> str:
        message = "{"
        first = True
        for render_data_for_file in renderer_data.render_data_for_files:
            if not first:
                message += ","

            message += __render_data_for_file__(render_data_for_file)
            first = False

        message += "}"
        return message
