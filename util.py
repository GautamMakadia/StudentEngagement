import datetime


def log(route: str, error):
    print(f"<=== exception in {route} ===> ")
    print(error)
    print(f"<=== exception in {route} ===> ")

def get_date(x: int) -> datetime.date:
    x /= 1000
    return datetime.date.fromtimestamp(x)