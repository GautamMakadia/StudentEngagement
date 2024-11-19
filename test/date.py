from datetime import datetime
from pprint import pprint

current = datetime.now()

print(current.date().__str__())
print(current.strftime("%A, %d %b %Y"))

print(f"{current.hour} hours, {current.minute} minute"  )