import functools
import threading
import time
import os
from rich import print as rprint

# ------------------------------
# retry decorator
# ------------------------------

# 定义线程局部变量
retry_ctx = threading.local()

def except_handler(error_msg, retry=0, delay=1, default_return=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retry + 1):
                retry_ctx.current_retry = i  # 设置当前重试次数
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    rprint(f"[red]{error_msg}: {e}, retry: {i + 1}/{retry}[/red]")
                    if i == retry:
                        if default_return is not None:
                            return default_return
                        raise last_exception
                    time.sleep(delay * (2 ** i))
        return wrapper
    return decorator


# ------------------------------
# check file exists decorator
# ------------------------------

def check_file_exists(file_path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if os.path.exists(file_path):
                rprint(f"[yellow]⚠️ File <{file_path}> already exists, skip <{func.__name__}> step.[/yellow]")
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    @except_handler("function execution failed", retry=3, delay=1)
    def test_function():
        raise Exception("test exception")
    test_function()
