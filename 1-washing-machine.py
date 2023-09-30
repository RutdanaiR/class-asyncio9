import os
import time
import random
import json
import asyncio
import aiomqtt
import sys, os
from enum import Enum

student_id = "6310301028"

class MachineStatus(Enum):
    pressure = round(random.uniform(2000,3000), 2)
    temperature = round(random.uniform(25.0,40.0), 2)
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
                "action"    : "get",
                "project"   : student_id,
                "model"     : "model-01",
                "serial"    : w.SERIAL,
                "name"      : name,
                "value"     : value
            }
    print(f"{time.ctime()} - PUBLISH - [{w.SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{w.SERIAL}"
                        , payload=json.dumps(payload))

async def CoroWashingMachine(w, client):
    # washing coroutine
    while True:
        wait_next = round(10*random.random(),2)
        print(f"{time.ctime()} - [{w.SERIAL}] Waiting to start... {wait_next} seconds.")
        await asyncio.sleep(wait_next)
        if w.MACHINE_STATUS == 'OFF' :
            continue
        if w.MACHINE_STATUS == 'ON' :

            await publish_message(w,client,"app","get","STATUS","START")

            await publish_message(w,client,"app","get","LTD","OPEN")
            
            await publish_message(w,client,"app","get","LTD","CLOSE")
            
            status = random.choice(list(MachineStatus))
            await publish_message(w,client,"app","get",status.name,status.value)
            await publish_message(w,client,"app","get","STATUS","FINISHD")
         
            maint = random.choice(list(MachineMaintStatus))
            await publish_message(w,client,"app","get",status.name,status.value)
            if (maint.name == 'noise'and maint.value == 'noisy'):
                w.MACHINE_STATUS = "OFF"
                continue
            await publish_message(w,client,"app","get","STATUS","STOPPED")
            
            await publish_message(w,client,"app","get","STATUS","POWER OFF")
            w.MACHINE_STATUS = "OFF"


async def listen(w, client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}"):
                print(f"{time.ctime()} -MQTT-[{m_decode['serial']}]:{m_decode['name']}=>{m_decode['value']}")
                w.MACHINE_STATUS = 'ON'

async def main():
    W1 = WashingMachine(serial='SN-001')
    async with aiomqtt.Client("test.mosquitto.org") as client:
            await asyncio.gather(listen(W1,client),CoroWashingMachine(W1,client))



if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())

# Wed Aug 30 15:09:59 2023 - [SN-001] Waiting to start... 7.46 seconds.
# Wed Aug 30 15:10:05 2023 -MQTT-[SN-001]:POWER=>ON
# Wed Aug 30 15:10:06 2023 - [SN-001] STATUS:START
# Wed Aug 30 15:10:08 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 15:10:08 2023 - [SN-001] LTD:OPEN
# Wed Aug 30 15:10:10 2023 - PUBLISH - [SN-001] - LTD > OPEN
# Wed Aug 30 15:10:10 2023 - [SN-001] LTD:CLOSE
# Wed Aug 30 15:10:12 2023 - PUBLISH - [SN-001] - LTD > CLOSE
# Wed Aug 30 15:10:12 2023 - [SN-001] pressure:2440.32
# Wed Aug 30 15:10:14 2023 - PUBLISH - [SN-001] - pressure > 2440.32
# Wed Aug 30 15:10:14 2023 - [SN-001] STATUS:FINISHD
# Wed Aug 30 15:10:16 2023 - PUBLISH - [SN-001] - STATUS > FINISHD
# Wed Aug 30 15:10:16 2023 - [SN-001] pressure:2440.32
# Wed Aug 30 15:10:18 2023 - PUBLISH - [SN-001] - pressure > 2440.32
# Wed Aug 30 15:10:18 2023 - [SN-001] STATUS:STOPPED
# Wed Aug 30 15:10:20 2023 - PUBLISH - [SN-001] - STATUS > STOPPED
# Wed Aug 30 15:10:20 2023 - [SN-001] STATUS:POWER OFF
# Wed Aug 30 15:10:22 2023 - PUBLISH - [SN-001] - STATUS > POWER OFF
# Wed Aug 30 15:10:22 2023 - [SN-001] Waiting to start... 0.69 seconds.
# Wed Aug 30 15:10:23 2023 - [SN-001] Waiting to start... 7.38 seconds.
# Wed Aug 30 15:10:30 2023 - [SN-001] Waiting to start... 6.0 seconds.
# Wed Aug 30 15:10:36 2023 - [SN-001] Waiting to start... 9.01 seconds.
# Wed Aug 30 15:10:45 2023 - [SN-001] Waiting to start... 9.96 seconds.
       