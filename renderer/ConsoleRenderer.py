import sys
from typing import TextIO

from renderer.Renderer import Renderer
from renderer.RenderData import RenderData
from threaddump.Config import Config


class ConsoleRenderer(Renderer):
    def __init__(self, config: Config):
        super().__init__(config)

    def render(self, renderer_data: RenderData):
        # check if the renderer data is valid
        self.check_render_data(renderer_data)

        text_io = self.init_file_object()
        try:
            print(self.render_string(renderer_data), file=text_io)
        finally:
            self.close_file_object(text_io)

    def render_string(self, renderer_data: RenderData) -> str:
        message = ""
        for render_data_for_file in renderer_data.render_data_for_files:
            message += f'---------------------------------------------------\n'
            message += f'File: {render_data_for_file.file}\n'
            message += f'---------------------------------------------------\n'
            message += "\n"
            message += f'Long running threads:\n'
            message += "\n"
            for long_running_thread in render_data_for_file.long_running_threads:
                message += f'\tLong running thread: {str(long_running_thread.thread)} is running for {
                long_running_thread.duration}. First appearance: {
                long_running_thread.first_apparition}. Last appearance: {long_running_thread.last_apparition}\n'

                message += "\tStacktrace:\n"

                for stack_frame in long_running_thread.thread.stacktrace:
                    message += f'\t\t- {str(stack_frame)}\n'

                message += "\n"

            message += "\n"
            message += f'Threads with the same stacktrace:\n'
            message += "\n"
            for thread_dump_with_recurring_threads in render_data_for_file.thread_dumps_with_recurring_threads:
                message += f'\tThread dump date: {thread_dump_with_recurring_threads.thread_dump_date}\n'
                for recurring_thread in thread_dump_with_recurring_threads.threads_with_recurring_stacktrace:
                    message += f'\t\tRecurring threads:\n'
                    for thread in recurring_thread.threads:
                        message += f'\t\t\t- {str(thread)}\n'

                    message += "\t\tStacktrace:\n"
                    for stack_frame in recurring_thread.recurring_stacktrace:
                        message += f'\t\t\t- {str(stack_frame)}\n'

                    message += "\n"

        return message

    def init_file_object(self) -> TextIO:
        return sys.stdout

    def close_file_object(self, file: TextIO):
        pass
