import inspect
import logging
import re


class CustomHandler(logging.Handler):
    def emit(self, record):
        frames = inspect.stack()

        for f in frames:
            if f.function == record.funcName:
                frame = f
                break
        else:
            frame = frames[6]

        if "self" in frame.frame.f_locals:
            # instance method
            class_name = frame.frame.f_locals["self"].__class__.__name__
            method_name = frame.function
            spacing_before_exec = " " * (34 - len(class_name) - len(method_name))
            log_exec_str = f"\033[96m{class_name}\033[0m.\033[92m{method_name}\033[0m"
        elif "cls" in frame.frame.f_locals:
            # class method
            class_name = frame.frame.f_locals["cls"].__name__
            method_name = frame.function
            spacing_before_exec = " " * (34 - len(class_name) - len(method_name))
            log_exec_str = f"\033[96m{class_name}\033[0m.\033[92m{method_name}\033[0m"
        elif frame.function != "<module>":
            # function
            function_name = frame.function
            spacing_before_exec = " " * (34 - len(function_name))
            log_exec_str = f"\033[92m{function_name}\033[0m"
        else:
            # root
            spacing_before_exec = " " * (34 - 4)
            log_exec_str = "\033[92mroot\033[0m"

        name = re.sub(r"^letusc\.", ".", record.name)
        spacing_before_name = " " * (19 - len(name))
        format_str = f"%(asctime)s {self.colorize_level(record.levelno)} {spacing_before_name}{name} [{spacing_before_exec}{log_exec_str}] %(message)s"
        log_format = logging.Formatter(format_str)
        print(log_format.format(record))

    def colorize_level(self, level: int):
        no_color = "\033[0m"
        colors = {
            logging.DEBUG: "\033[33m",  # Yellow
            logging.INFO: "\033[34m",  # Blue
            logging.WARNING: "\033[35m",  # Magenta
            logging.ERROR: "\033[31m",  # Red
            logging.CRITICAL: "\033[41m",  # Red background
        }
        spacing = " " * (8 - len(logging.getLevelName(level)))
        return f"[{colors.get(level, no_color)}{spacing}{logging.getLevelName(level)}{no_color}]"


class CustomLogger(logging.Logger):
    @property
    def full(self) -> str:
        frames = inspect.stack()
        frame = frames[1] # 1 is the caller of this function

        if "self" in frame.frame.f_locals:
            class_name = frame.frame.f_locals["self"].__class__.__name__
            method_name = frame.function
            return f"{class_name}.{method_name}"
        elif "cls" in frame.frame.f_locals:
            class_name = frame.frame.f_locals["cls"].__name__
            method_name = frame.function
            return f"{class_name}.{method_name}"
        elif frame.function != "<module>":
            function_name = frame.function
            return f"{function_name}"
        else:
            return f"root"

    def c(self, code: str) -> str:
        frames = inspect.stack()
        frame = frames[1] # 1 is the caller of this function

        if "self" in frame.frame.f_locals:
            class_name = frame.frame.f_locals["self"].__class__.__name__
            method_name = frame.function
            return f"{class_name}.{method_name}:{code}"
        elif "cls" in frame.frame.f_locals:
            class_name = frame.frame.f_locals["cls"].__name__
            method_name = frame.function
            return f"{class_name}.{method_name}:{code}"
        elif frame.function != "<module>":
            function_name = frame.function
            return f"{function_name}:{code}"
        else:
            return f"root:{code}"


logging.setLoggerClass(CustomLogger)


def get_logger(name: str) -> CustomLogger:
    logger = logging.getLogger(name)
    if not isinstance(logger, CustomLogger):
        logger = CustomLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(CustomHandler())
    return logger
