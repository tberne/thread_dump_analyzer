import datetime

from threaddump.Stacktrace import Thread, ThreadState, StackFrame, SyncObject, SyncObjectType, ThreadDump
import re
import threaddump.Config as Config


def __should_include__(stacktrace: list[StackFrame], include_patterns: list[str], exclude_patterns: list[str]) -> bool:
    if include_patterns and len(include_patterns) > 0:
        include = False
        for pattern in include_patterns:
            if include:
                break

            for stack_frame in stacktrace:
                if re.match(pattern, str(stack_frame), re.MULTILINE):
                    include = True
                    break

        if not include:
            return False

    if exclude_patterns and len(exclude_patterns) > 0:
        exclude = False
        for pattern in exclude_patterns:
            if exclude:
                break

            for stack_frame in stacktrace:
                if re.match(pattern, str(stack_frame), re.MULTILINE):
                    exclude = True
                    break

        if exclude:
            return False

    return True


class LongRunningThread:
    def __init__(self, thread: Thread, count: int, first_apparition: datetime.datetime,
                 last_apparition: datetime.datetime, duration: datetime.timedelta):

        self.thread = thread
        self.count = count
        self.first_apparition = first_apparition
        self.last_apparition = last_apparition
        self.duration = duration


def find_long_running_threads(tds: list[ThreadDump], *, config: Config) -> list[LongRunningThread]:
    long_running_threads = {}
    include_patterns = config.long_running_threads_include_patterns
    exclude_patterns = config.long_running_threads_exclude_patterns

    for thread_dump in tds:
        for thread in thread_dump.threads:
            if not __should_include__(thread.stacktrace, include_patterns, exclude_patterns):
                continue

            if not thread.thread_id in long_running_threads:
                long_running_threads[thread.thread_id] = {
                    "thread": thread,
                    "count": 1,
                    "first_apparition": thread_dump.date_time,
                    "last_apparition": thread_dump.date_time
                }
            else:
                # thread remain still
                if thread.stacktrace == long_running_threads[thread.thread_id]["thread"].stacktrace:
                    long_running_threads[thread.thread_id]["count"] += 1

                    current_td_date = thread_dump.date_time
                    last_td_date = long_running_threads[thread.thread_id]["last_apparition"]
                    first_td_date = long_running_threads[thread.thread_id]["first_apparition"]

                    if current_td_date > last_td_date:
                        long_running_threads[thread.thread_id]["last_apparition"] = current_td_date

                    if current_td_date < first_td_date:
                        long_running_threads[thread.thread_id]["first_apparition"] = current_td_date

                # thread changed
                else:
                    long_running_threads[thread.thread_id] = {
                        "thread": thread,
                        "count": 1,
                        "first_apparition": thread_dump.date_time,
                        "last_apparition": thread_dump.date_time
                    }

    long_running_threads = [LongRunningThread(
        thread["thread"],
        thread["count"],
        thread["first_apparition"],
        thread["last_apparition"],
        thread["last_apparition"] - thread["first_apparition"]
    ) for thread in long_running_threads.values() if thread["count"] >= config.long_running_threads_threshold]

    return long_running_threads


class ThreadsWithRecurringStacktrace:
    def __init__(self, threads: list[Thread]):
        self.threads = threads
        self.recurring_stacktrace = threads[0].stacktrace


class ThreadDumpsWithRecurringThreads:
    def __init__(self, thread_dump_date: datetime.datetime,
                 threads_with_recurring_stacktrace: list[ThreadsWithRecurringStacktrace]):

        self.thread_dump_date = thread_dump_date
        self.threads_with_recurring_stacktrace = threads_with_recurring_stacktrace


def find_most_recurring_threads(tds: list[ThreadDump], *, config: Config) -> list[ThreadDumpsWithRecurringThreads]:
    if config.debug:
        print("Finding most recurring threads...")

    include_patterns = config.most_recurring_threads_include_patterns
    exclude_patterns = config.most_recurring_threads_exclude_patterns

    recurring_threads = []
    for td in tds:
        recurring_threads_in_td = {}
        for thread in td.threads:
            if not __should_include__(thread.stacktrace, include_patterns, exclude_patterns):
                continue

            # ignore dummy threads
            if config.most_recurring_threads_ignore_dummy_threads and len(thread.stacktrace) == 0:
                if config.debug:
                    print(f"Thread {thread.thread_name} is a dummy thread and, thus, is ignored.")
                continue

            stacktrace_str = "["
            first_stackframe = True
            for stackframe in thread.stacktrace:
                if first_stackframe:
                    first_stackframe = False
                else:
                    stacktrace_str += ", "

                stacktrace_str += str(stackframe)

            stacktrace_str += "]"

            if config.debug:
                print(f"Checking if the stacktrace {stacktrace_str} is already in the recurring threads...")

            if not stacktrace_str in recurring_threads_in_td:
                recurring_threads_in_td[stacktrace_str] = [thread]
            else:
                recurring_threads_in_td[stacktrace_str].append(thread)

        recurring_threads_in_td = [ThreadsWithRecurringStacktrace(threads) for threads in recurring_threads_in_td.values() if len(threads) >= config.most_recurring_threads_threshold]

        if len(recurring_threads_in_td) > 0:
            recurring_threads.append(ThreadDumpsWithRecurringThreads(td.date_time, recurring_threads_in_td))

    return recurring_threads
