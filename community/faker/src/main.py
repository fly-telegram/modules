#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.

import faker
import random


async def fake_cmd(self):
    fake = faker.Faker()

    first_name = fake.first_name()
    last_name = fake.last_name()

    age = random.randint(10, 100)

    country = fake.country()
    address = fake.address()
    zip_code = fake.zipcode()

    email = fake.email()
    number = fake.phone_number()

    await self.message.edit(
        "<b>✨ generated information</b>\n"
        f"<b>name</b>: <code>{last_name} {first_name}</b>\n"
        f"<b>age</b>: <code>{age}</b>\n"
        f"<b>country</b>: <code>{country}</b>\n"
        f"<b>address</b>: <code>{address}</b>\n"
        f"<b>ZIP-code</b>: <code>{zip_code}</b>\n"
        f"<b>email</b>: <code>{email}</b>\n"
        f"<b>number</b>: <code>{number}</b>\n"
    )
