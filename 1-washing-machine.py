import time
import random
import json
import asyncio
import aiomqtt
import os
import sys
from enum import Enum

student_id = "6310301028"


class MachineStatus(Enum):
    pressure = round(random.uniform(2000, 3000), 2)
    temperature = round(random.uniform(25.0, 40.0), 2)
    #
    # add more machine status
    #


class MachineMaintStatus(Enum):
    filter = random.choice(["clear", "clogged"])
    noise = random.choice(["quiet", "noisy"])
    #
    # add more maintenance status
    #


class WashingMachine:
    def __init__(self, serial):
        self.MACHINE_STATUS = 'OFF'
        self.SERIAL = serial


async def publish_message(w, client, app, action, name, value):
    print(f"{time.ctime()} - [{w.SERIAL}] {name}:{value}")
    await asyncio.sleep(2)
    payload = {
        "action": "get",
        "project": student_id,
        "model": "model-01",
        "serial": w.SERIAL,
        "name": name,
        "value": value
    }
    print(
        f"{time.ctime()} - PUBLISH - [{w.SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cd/{app}/{action}/{student_id}/model-01/{w.SERIAL}", payload=json.dumps(payload))


async def CoroWashingMachine(w, client):
    # washing coroutine
    while True:
        wait_next = round(10*random.random(), 2)
        print(
            f"{time.ctime()} - [{w.SERIAL}] Waiting to start... {wait_next} seconds.")
        await asyncio.sleep(wait_next)
        if w.MACHINE_STATUS == 'OFF':
            continue
        if w.MACHINE_STATUS == 'ON':

            await publish_message(w, client, "app", "get", "STATUS", "START")

            await publish_message(w, client, "app", "get", "LID", "OPEN")

            await publish_message(w, client, "app", "get", "STATUS", "CLOSE")

 # random status
            status = random.choice(list(MachineStatus))
            await publish_message(w, client, "app", "get", status.name, status.value)

            await publish_message(w, client, "app", "get",  "STATUS", "FINISHED")

# random maintance
            maint = random.choice(list(MachineMaintStatus))
            await publish_message(w, client, "app", "get", maint.name, maint.value)
            if (maint.name == 'noise' and maint.value == 'noisy'):
                w.MACHINE_STATUS = 'OFF'

            await publish_message(w, client, "app", "get",  "STATUS", "STOPPED")

            await publish_message(w, client, "app", "get",  "STATUS", "POWER OFF")
            w.MACHINE_STATUS = 'OFF'


async def listen(w, client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cd/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cd/hw/set/{student_id}/model-01/{w.SERIAL}"):
                # set washing machine status
                print(
                    f"{time.ctime} -- MQTT -- [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']})")
                w.MACHINE_STATUS = 'ON'


async def main():
    w = WashingMachine(serial='SN-001')
    async with aiomqtt.Client("test.mosquitto.org") as client:
        await asyncio.gather(listen(w, client), CoroWashingMachine(w, client))

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())

# <built-in function ctime> -- MQTT -- [SN-001]:power => ON)
# <built-in function ctime> -- MQTT -- [SN-001]:power => ON)
# Wed Aug 30 14:53:03 2023 - [SN-001] STATUS:START
# Wed Aug 30 14:53:05 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 14:53:05 2023 - [SN-001] LID:OPEN
# Wed Aug 30 14:53:07 2023 - PUBLISH - [SN-001] - LID > OPEN
# Wed Aug 30 14:53:07 2023 - [SN-001] STATUS:CLOSE
# Wed Aug 30 14:53:09 2023 - PUBLISH - [SN-001] - STATUS > CLOSE
# Wed Aug 30 14:53:09 2023 - [SN-001] pressure:2723.53
# Wed Aug 30 14:53:11 2023 - PUBLISH - [SN-001] - pressure > 2723.53
# Wed Aug 30 14:53:11 2023 - [SN-001] STATUS:FINISHED
# Wed Aug 30 14:53:13 2023 - PUBLISH - [SN-001] - STATUS > FINISHED
# Wed Aug 30 14:53:13 2023 - [SN-001] noise:noisy
# Wed Aug 30 14:53:15 2023 - PUBLISH - [SN-001] - noise > noisy
# Wed Aug 30 14:53:15 2023 - [SN-001] STATUS:STOPPED
# Wed Aug 30 14:53:17 2023 - PUBLISH - [SN-001] - STATUS > STOPPED
# Wed Aug 30 14:53:17 2023 - [SN-001] STATUS:POWER OFF
# Wed Aug 30 14:53:19 2023 - PUBLISH - [SN-001] - STATUS > POWER OFF
# Wed Aug 30 14:53:19 2023 - [SN-001] Waiting to start... 4.65 seconds.
# Wed Aug 30 14:53:24 2023 - [SN-001] Waiting to start... 1.86 seconds.
# <built-in function ctime> -- MQTT -- [SN-001]:power => ON)
# Wed Aug 30 14:53:26 2023 - [SN-001] STATUS:START
# Wed Aug 30 14:53:28 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 14:53:28 2023 - [SN-001] LID:OPEN
# Wed Aug 30 14:53:30 2023 - PUBLISH - [SN-001] - LID > OPEN
# Wed Aug 30 14:53:30 2023 - [SN-001] STATUS:CLOSE
# Wed Aug 30 14:53:32 2023 - PUBLISH - [SN-001] - STATUS > CLOSE
# Wed Aug 30 14:53:32 2023 - [SN-001] pressure:2723.53
# Wed Aug 30 14:53:34 2023 - PUBLISH - [SN-001] - pressure > 2723.53
# Wed Aug 30 14:53:34 2023 - [SN-001] STATUS:FINISHED
# Wed Aug 30 14:53:36 2023 - PUBLISH - [SN-001] - STATUS > FINISHED
# Wed Aug 30 14:53:36 2023 - [SN-001] noise:noisy
# Wed Aug 30 14:53:38 2023 - PUBLISH - [SN-001] - noise > noisy
# Wed Aug 30 14:53:38 2023 - [SN-001] STATUS:STOPPED
# Wed Aug 30 14:53:40 2023 - PUBLISH - [SN-001] - STATUS > STOPPED
# Wed Aug 30 14:53:40 2023 - [SN-001] STATUS:POWER OFF
# Wed Aug 30 14:53:42 2023 - PUBLISH - [SN-001] - STATUS > POWER OFF
# Wed Aug 30 14:53:42 2023 - [SN-001] Waiting to start... 1.83 seconds.
# Wed Aug 30 14:53:44 2023 - [SN-001] Waiting to start... 1.03 seconds.
# Wed Aug 30 14:53:45 2023 - [SN-001] Waiting to start... 0.12 seconds.
# Wed Aug 30 14:53:45 2023 - [SN-001] Waiting to start... 9.57 seconds.
# Wed Aug 30 14:53:54 2023 - [SN-001] Waiting to start... 5.15 seconds.
# Wed Aug 30 14:53:59 2023 - [SN-001] Waiting to start... 4.24 seconds.
# Wed Aug 30 14:54:04 2023 - [SN-001] Waiting to start... 2.22 seconds.
# Wed Aug 30 14:54:06 2023 - [SN-001] Waiting to start... 4.63 seconds.
# Wed Aug 30 14:54:11 2023 - [SN-001] Waiting to start... 7.89 seconds.
# Wed Aug 30 14:54:19 2023 - [SN-001] Waiting to start... 0.85 seconds.
# Wed Aug 30 14:54:19 2023 - [SN-001] Waiting to start... 5.53 seconds.
# Wed Aug 30 14:54:25 2023 - [SN-001] Waiting to start... 6.41 seconds.
# Wed Aug 30 14:54:31 2023 - [SN-001] Waiting to start... 8.9 seconds.
# Wed Aug 30 14:54:40 2023 - [SN-001] Waiting to start... 7.21 seconds.
# Wed Aug 30 14:54:47 2023 - [SN-001] Waiting to start... 3.61 seconds.
# Wed Aug 30 14:54:51 2023 - [SN-001] Waiting to start... 0.5 seconds.
# Wed Aug 30 14:54:52 2023 - [SN-001] Waiting to start... 1.27 seconds.
# Wed Aug 30 14:54:53 2023 - [SN-001] Waiting to start... 6.06 seconds.
# Wed Aug 30 14:54:59 2023 - [SN-001] Waiting to start... 9.27 seconds.
# Wed Aug 30 14:55:08 2023 - [SN-001] Waiting to start... 2.77 seconds.
# Wed Aug 30 14:55:11 2023 - [SN-001] Waiting to start... 6.27 seconds.
# Wed Aug 30 14:55:17 2023 - [SN-001] Waiting to start... 9.8 seconds.
# Wed Aug 30 14:55:27 2023 - [SN-001] Waiting to start... 1.75 seconds.
# Wed Aug 30 14:55:29 2023 - [SN-001] Waiting to start... 1.8 seconds.
