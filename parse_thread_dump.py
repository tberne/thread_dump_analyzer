import argparse
import sys
from glob import glob
from threaddump import Stacktrace, Analizer, Config


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

    output_file = None
    original_stdout = sys.stdout
    if config.output_file:
        output_file = open(config.output_file, 'w')
        sys.stdout = output_file

    try:
        tds = {}
        found_files = []

        if len(config.files) == 0:
            print('No files to parse')
            return

        for glob_pattern in config.files:
            found_files += glob(glob_pattern)

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

        for file in tds.keys():
            print(f'Finding long running threads from thread dumps in file: {file}...')

            long_running_threads = Analizer.find_long_running_threads(tds[file], config=config)
            for thread in long_running_threads:
                print(f'File: {file}, Count: {thread["count"]}, First apparition: {thread["first_apparition"]}, Last '
                      f'apparition: {thread["last_apparition"]}, Duration: {thread["duration"]}')
                print(__format_thread__(thread["thread"]))
                print("\n\n")

            print(f'Finding most recurring threads from thread dumps in file: {file}...')

            most_recurring_threads = Analizer.find_most_recurring_threads(tds[file], config=config)
            for thread_dump_date in most_recurring_threads.keys():
                thread_dump_values = most_recurring_threads[thread_dump_date]

                for most_recurring_threads_in_td in thread_dump_values:
                    threads = most_recurring_threads_in_td["threads"]
                    count = most_recurring_threads_in_td["count"]

                    print(f'File: {file}, Thread dump date: {thread_dump_date}, Count of threads repeating the same '
                          f'stacktrace: {count}')
                    for t in threads:
                        print(f"    - {__format_thread__(t, include_stacktrace=False)}")

                    print(f"Stacktrace:")
                    for stackframe in threads[0].stacktrace:
                        print(f'        {str(stackframe)}')

                    print("\n\n")
    finally:
        if output_file:
            sys.stdout = original_stdout
            output_file.close()


if __name__ == '__main__':
    main()

