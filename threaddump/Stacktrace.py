import enum
import datetime
import re
from threaddump.Config import Config


class SyncObjectType(enum.Enum):
    ELIMINATED = 1
    LOCKED = 2
    PARKING_TO_WAIT_FOR = 3
    WAITING_ON = 4
    WAITING_TO_LOCK = 5
    WAITING_TO_RE_LOCK = 6


class SyncObject:
    def __init__(self, sync_object_type: SyncObjectType, clazz: str, object_id: str | None):
        self.__clazz = clazz
        self.__object_id = object_id
        self.__sync_object_type = sync_object_type

    @property
    def sync_object_type(self):
        return self.__sync_object_type

    @property
    def clazz(self):
        return self.__clazz

    @property
    def object_id(self):
        return self.__object_id

    def __str__(self):
        return f'{self.sync_object_type} on <{self.object_id}> (a {self.clazz})'

    def __eq__(self, other):
        return (
                self.__class__ == other.__class__ and
                self.sync_object_type == other.sync_object_type and
                self.clazz == other.clazz and
                self.object_id == other.object_id
        )

    def __hash__(self) -> int:
        return hash((self.sync_object_type, self.clazz, self.object_id))


class StackFrame:
    def __init__(self, clazz: str, method: str, source_code_location: str | None, sync_object: SyncObject | None):
        self.__clazz = clazz
        self.__method = method
        self.__source_code_location = source_code_location
        self.__syncObject = sync_object

    @property
    def clazz(self) -> str:
        return self.__clazz

    @property
    def method(self) -> str:
        return self.__method

    @property
    def source_code_location(self) -> str | None:
        return self.__source_code_location

    @property
    def sync_object(self) -> SyncObject | None:
        return self.__syncObject

    @sync_object.setter
    def sync_object(self, sync_object: SyncObject | None):
        self.__syncObject = sync_object

    def __str__(self):
        if not self.source_code_location:
            return f'{self.clazz}.{self.method}'
        else:
            return f'{self.clazz}.{self.method}({self.source_code_location})'

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, StackFrame):
            return False

        other_stack_frame: StackFrame = __value

        return (
                self.clazz == other_stack_frame.clazz and
                self.method == other_stack_frame.method and
                self.source_code_location == other_stack_frame.source_code_location and
                self.sync_object == other_stack_frame.sync_object
        )

    def __hash__(self) -> int:
        return hash((self.clazz, self.method, self.source_code_location, self.sync_object))


class ThreadState(enum.Enum):
    RUNNABLE = 1
    WAITING = 2
    TIMED_WAITING = 3
    BLOCKED = 4


class Thread:
    def __init__(self, thread_id: str, thread_name: str, thread_state: ThreadState | None, daemon: bool, priority: int,
                 os_priority: int, cpu_time: float | None, elapsed_time: float | None, stacktrace: list[StackFrame]):
        self.__thread_id = thread_id
        self.__thread_name = thread_name
        self.__thread_state = thread_state
        self.__stacktrace = stacktrace
        self.__daemon = daemon
        self.__priority = priority
        self.__os_priority = os_priority
        self.__cpu_time = cpu_time
        self.__elapsed_time = elapsed_time

    @property
    def thread_id(self) -> str:
        return self.__thread_id

    @property
    def thread_name(self) -> str:
        return self.__thread_name

    @property
    def thread_state(self) -> ThreadState:
        return self.__thread_state

    @property
    def stacktrace(self) -> list[StackFrame]:
        return self.__stacktrace

    @property
    def daemon(self) -> bool:
        return self.__daemon

    @property
    def priority(self) -> int:
        return self.__priority

    @property
    def os_priority(self) -> int:
        return self.__os_priority

    @property
    def cpu_time(self) -> float | None:
        return self.__cpu_time

    @property
    def elapsed_time(self) -> float | None:
        return self.__elapsed_time

    @thread_state.setter
    def thread_state(self, thread_state: ThreadState):
        self.__thread_state = thread_state

    def __str__(self):
        return f"Thread {self.thread_id} ({self.thread_name})"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Thread):
            return False

        # cast to Thread to avoid type errors
        __value: Thread

        return (
                self.__class__ == __value.__class__ and
                self.thread_id == __value.thread_id and
                self.thread_name == __value.thread_name and
                self.thread_state == __value.thread_state and
                self.stacktrace == __value.stacktrace and
                self.daemon == __value.daemon

            # NEVER compare these values because they may change between dumps
            # and
            # self.priority == __value.priority and
            # self.os_priority == __value.os_priority

            # NEVER compare these values because they are always different
            # and
            # self.cpu_time == __value.cpu_time and
            # self.elapsed_time == __value.elapsed_time
        )

    def __hash__(self) -> int:
        return hash((self.thread_id, self.thread_name, self.thread_state, self.stacktrace, self.daemon, self.priority,
                     self.os_priority, self.cpu_time, self.elapsed_time))


class ThreadDump:
    def __init__(self, threads: list[Thread], date_time: datetime.datetime):
        self.__threads = threads
        self.__date_time = date_time

    @property
    def threads(self) -> list[Thread]:
        return self.__threads

    @property
    def date_time(self) -> datetime.datetime:
        return self.__date_time

    def __str__(self):
        return f"ThreadDump at {self.date_time}"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ThreadDump):
            return False

        # cast to ThreadDump to avoid type errors
        __value: ThreadDump

        return (
                self.__class__ == __value.__class__ and
                self.threads == __value.threads and
                self.date_time == __value.date_time
        )

    def __hash__(self) -> int:
        return hash((self.threads, self.date_time))


def parse_duration(duration_str: str) -> float | None:
    if not duration_str or duration_str.strip() == '':
        return None

    # duration comes in formats 0.00s, 0.00ms, 0.00us, 0.00ns etc
    duration_match = re.match(r'^(\d+\.\d+)([a-z]+)$', duration_str)
    duration = float(duration_match.group(1))
    unit = duration_match.group(2)

    if unit == 's':
        return duration * 1000
    elif unit == 'ms':
        return duration
    elif unit == 'us':
        return duration / 1000
    elif unit == 'ns':
        return duration / 1000000
    else:
        raise ValueError(f"Invalid duration unit: {unit}")


def parse_thread_dump_file(file_path: str, *, config: Config) -> list[ThreadDump]:
    stacktraces = []
    if config.debug:
        print(f'Parsing file: {file_path}')
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_stack_trace = None
        current_thread = None
        for i in range(len(lines)):
            line = lines[i]

            if config.debug:
                print(f'Parsing line {i}: {line}')

            # parse new stack trace
            new_stack_trace = parse_stack_trace(line)
            if new_stack_trace:
                # create new stack trace
                current_stack_trace = new_stack_trace
                stacktraces.append(current_stack_trace)
                if config.debug:
                    print(f'New thread dump found: {current_stack_trace.date_time}')

                continue

            # parse thread
            thread = parse_thread(line)
            if thread:
                # sanity (must be inside a stack trace)
                if not current_stack_trace:
                    raise Exception(f'Thread {thread.thread_id} found outside of stack trace')

                if config.debug:
                    print(f'New thread found: {thread.thread_name} ({thread.thread_id})')

                # next line must be a thread state line
                next_line = lines[i + 1]
                thread_state = parse_thread_state(next_line)
                if not thread_state:
                    raise Exception(f'Thread state not found for thread {thread.thread_id}')

                thread.thread_state = thread_state

                # add thread to stack trace
                current_stack_trace.threads.append(thread)
                current_thread = thread

                # must increment i to skip the next line
                i += 1

                if config.debug:
                    print(f'Thread state: {thread_state}')

                continue

            # parse stack frame
            stack_frame = parse_stack_frame(line)
            if stack_frame:
                # sanity (must be inside a thread)
                if not current_thread:
                    raise Exception(f'Stack frame found outside of thread! Line {i}: {line}')

                current_thread.stacktrace.append(stack_frame)

                # check if next line is a sync object
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    sync_object = parse_sync_object(next_line)
                    if sync_object:
                        stack_frame.sync_object = sync_object
                        i += 1

                continue

            # ignore empty lines
            if line.strip() == '':
                continue

            # ignore other lines
            if config.debug:
                print(f'Ignored line: {line}')

    return stacktraces


def parse_stack_trace(line) -> ThreadDump | None:
    stack_trace_date_time_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$', line)
    if stack_trace_date_time_match:
        return ThreadDump([], datetime.datetime.strptime(stack_trace_date_time_match.group(1), '%Y-%m-%d %H:%M:%S'))
    else:
        return None


def parse_thread(line) -> Thread | None:
    thread_match = re.match(
        r'^"(.+)"\s+#\d+(\s+daemon)?\s+prio=(\d+)\s+os_prio=(\d+) +(cpu=([^ ]+) +)?(elapsed=([^ ]+) +)?tid=([^ ]+).*$',
        line,
        re.MULTILINE)

    # parse thread
    if thread_match:
        thread_name = thread_match.group(1)
        daemon = thread_match.group(2) is not None
        priority = int(thread_match.group(3))
        os_priority = int(thread_match.group(4))
        cpu_time = parse_duration(thread_match.group(6))
        elapsed_time = parse_duration(thread_match.group(8))
        thread_id = thread_match.group(9)
        return Thread(thread_id, thread_name, None, daemon, priority, os_priority, cpu_time, elapsed_time, [])
    else:
        return None


def parse_thread_state(line) -> ThreadState | None:
    thread_state_match = re.match(r'^\s*java\.lang\.Thread\.State: (\S+).*$', line)
    if thread_state_match:
        return ThreadState[thread_state_match.group(1)]
    else:
        return None


def parse_stack_frame(line) -> StackFrame | None:
    stack_frame_match = re.match(r'^\s+at ([^ ]+)\.([^ ]+)\(([^)]+)\).*$', line)
    if stack_frame_match:
        clazz = stack_frame_match.group(1)
        method = stack_frame_match.group(2)
        source_code_location = stack_frame_match.group(3)
        return StackFrame(clazz, method, source_code_location, None)
    else:
        return None


def parse_sync_object(line) -> SyncObject | None:
    sync_object_match = re.match(r'\s+-\s+([^<]+)<([^>]+)>\s*(\(a\s+([^)]+)\)).*?', line)
    if sync_object_match:
        sync_object_type_str = sync_object_match.group(1).strip()
        sync_object_id = sync_object_match.group(2).strip()
        sync_object_class = sync_object_match.group(4).strip()

        if sync_object_id.casefold() == 'no object reference available':
            sync_object_id = None

        match sync_object_type_str.casefold():
            case 'eliminated':
                sync_object_type = SyncObjectType.ELIMINATED
            case 'locked':
                sync_object_type = SyncObjectType.LOCKED
            case 'parking to wait for':
                sync_object_type = SyncObjectType.PARKING_TO_WAIT_FOR
            case 'waiting on':
                sync_object_type = SyncObjectType.WAITING_ON
            case 'waiting to lock':
                sync_object_type = SyncObjectType.WAITING_TO_LOCK
            case 'waiting to re-lock in wait()':
                sync_object_type = SyncObjectType.WAITING_TO_RE_LOCK
            case _:
                raise ValueError(f'Invalid sync object type: {sync_object_type_str}')

        return SyncObject(sync_object_type, sync_object_class, sync_object_id)
    else:
        return None
