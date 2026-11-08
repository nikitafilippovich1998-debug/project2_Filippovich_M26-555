import functools
import time


def handle_db_errors(func):
    """Декоратор для перехвата ошибок базы данных."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
            return args[0], "Ошибка"
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return args[0], "Ошибка"
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return args[0], "Ошибка"
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return args[0], "Ошибка"
    return wrapper


def confirm_action(action_name):
    """Декоратор (фабрика) для подтверждения опасных действий."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Спрашиваем подтверждение
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() != 'y':
                print("Операция отменена.")
                # Возвращаем первый аргумент (метаданные или данные таблицы) без изменений, чтобы программа не упала
                return args[0], "Операция отменена."
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Декоратор для измерения времени выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end_time - start_time:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Замыкание для кэширования результатов (например, запросов select)."""
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            print("[КЭШ] Возврат закэшированного результата.")
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
        
    return cache_result