import argparse
import sys
from glob import glob
from threaddump import Stacktrace, Analizer, Config
from renderer.RenderData import RenderData, RenderDataForFile
from renderer.ConsoleRenderer import ConsoleRenderer
from renderer.FileRenderer import FileRenderer
from renderer.JsonFileRenderer import JsonFileRenderer
from renderer.HtmlRenderer import HtmlRenderer

def __format_thread__(thread: Stacktrace.Thread, *, include_stacktrace=True) -> str:
    ret_value = f'Thread: {thread.thread_name} ({thread.thread_id}) - State: {thread.thread_state}'

    if include_stacktrace:
        for stackframe in thread.stacktrace:
            ret_value += f'\n    {stackframe.clazz}.{stackframe.method}'
            if stackframe.source_code_location:
                ret_value += f'({stackframe.source_code_location})'

    return ret_value


def main():
    parser = argparse.ArgumentParser(description='Parse thread dump')
    parser.add_argument('-c', type=str, help='Config file', nargs='?', default="td.cfg.yml")
    args = parser.parse_args()

    print(f'Parsing thread dumps with config file: {args.c}')

    config = Config.Config(args.c)

    tds = {}
    found_files = []

    if len(config.files) == 0:
        print('No files to parse')
        return

    for glob_pattern in config.files:
        found_files += [a.replace("\\", "/") for a in glob(glob_pattern)]

    if config.debug:
        print(f'Found files: {found_files}')

    for file in found_files:
        tds[file] = []

        if config.debug:
            print(f'Parsing file: {file}')

        for stacktrace in Stacktrace.parse_thread_dump_file(file, config=config):
            tds[file].append(stacktrace)

        if config.debug:
            print(f'Parsed {len(tds[file])} thread dumps from file {file}')

    render_data = RenderData([])
    for file in tds.keys():
        print(f'Finding long running threads from thread dumps in file: {file}...')
        long_running_threads = Analizer.find_long_running_threads(tds[file], config=config)
        most_recurring_threads = Analizer.find_most_recurring_threads(tds[file], config=config)
        render_data.render_data_for_files.append(RenderDataForFile(file, most_recurring_threads,
                                                                   long_running_threads))

    # renders the output
    renderer_type = config.renderer_type
    renderer = None

    match renderer_type:
        case "console":
            renderer = ConsoleRenderer(config)
        case "file":
            renderer = FileRenderer(config)
        case "json":
            renderer = JsonFileRenderer(config)
        case "html":
            renderer = HtmlRenderer(config)
        case _:
            print(f'Unknown renderer type: {renderer_type}')
            sys.exit(1)

    renderer.render(render_data)


if __name__ == '__main__':
    main()

