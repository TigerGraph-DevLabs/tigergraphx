import time

class TestBaseGraph:
    @staticmethod
    def time_execution(func, func_name: str):
        start_time = time.perf_counter()
        result = func()  # Call the function directly
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Time taken to execute {func_name}: {elapsed_time:.6f} seconds")
        return result
