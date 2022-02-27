import asyncio
import zlib
import websockets
from datetime import datetime, timedelta
import time

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import asc, desc
from sqlalchemy.future import select

from config_wrapper import get_settings

from app.schemas.can import CANMessage as PydanticCANMessage
from app.models.can_message import Base, ConfigMessage, ConfigUsageMessage, ConfigLocomotiveMessage, LocomotiveMetricMessage, LocomotiveSpeedMessage
from app.models.can_message_converter import registered_models, convert_to_model
from app.services.high_level_can_recv.converter import type_map as pydantic_type_map
from app.schemas.can_commands import CommandSchema
from app.services.high_level_can.helper import parse_config

settings = get_settings()

HOST = settings.can_receiver_host
PORT = settings.can_receiver_port

DB = settings.high_level_db_dump_database

engine = create_async_engine(
    DB, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def parse_message(message):
    t = message[:message.find("{")]
    payload = message[len(t):]
    clas = pydantic_type_map[t]  # hacky
    abstract_message = clas.parse_raw(payload)
    return abstract_message


async def dump_model(session, abstract_model):
    session.add(abstract_model)
    await session.commit()


async def dump(session, pydantic_abstract_message):
    print("Dumping message")
    abstract_model = convert_to_model(pydantic_abstract_message)
    assert abstract_model is not None
    await dump_model(session, abstract_model)


async def save_usage_message(session, obj, pydantic_abstract_message):
    await dump_model(session, ConfigUsageMessage.from_message(obj, pydantic_abstract_message))


async def save_locomotive_message(session, obj, pydantic_abstract_message):
    for lok in obj["lokomotive"]:
        if not isinstance(lok, dict) or lok.get("name") is None:
            continue # skip empty entries
        await dump_model(session, ConfigLocomotiveMessage.from_message(lok, pydantic_abstract_message))


CONFIG_MESSAGE_DICT = {
    "[verbrauch]": save_usage_message,
    "[lokomotive]": save_locomotive_message
}


async def get_next_config_stream(session, connection):
    async for message in connection:
        pydantic_abstract_message = await parse_message(message)
        if not pydantic_abstract_message.get_command() == CommandSchema.ConfigDataStream:
            await dump(session, pydantic_abstract_message)
            continue
        return pydantic_abstract_message


async def get_next_config_stream_timeout(session, connection):
    try:
        return await asyncio.wait_for(get_next_config_stream(session, connection), 1)
    except Exception as e:
        print(f"{e}")
        return None


async def init_db():
    async with engine.begin() as conn:
        for model in registered_models:
            await conn.run_sync(model.metadata.create_all)
    


async def save_config_message(session, data, length, pydantic_abstract_message):
    _, config_obj = parse_config(data)

    for message_type in CONFIG_MESSAGE_DICT:
        if message_type in config_obj:
            obj = config_obj[message_type]
            await CONFIG_MESSAGE_DICT[message_type](session, obj, pydantic_abstract_message)

    # also save to normal ConfigMessage
    await dump_model(session, ConfigMessage.from_message(data, length, pydantic_abstract_message))

async def process_config_stream(session, websocket, pydantic_abstract_message):
    if pydantic_abstract_message.file_length is None:
        return
    length = pydantic_abstract_message.file_length
    received_count = 0
    received_data = ""
    while received_count < length:
        next_message = await get_next_config_stream_timeout(session, websocket)
        if next_message is None:
            break
        data = next_message.data
        if not isinstance(data, str):
            break
        if received_count > 0:
            received_data += " "
        received_count += 8
        received_data += data

    data = bytes.fromhex(received_data)[:length]
    try:
        data = zlib.decompress(data[4:])
    except Exception as e:
        pass
    try:
        data = data.decode("utf-8")
    except Exception as e:
        pass

    await save_config_message(session, data, length, pydantic_abstract_message)


# Calculates 'distance points' = duration (in s) * speed
async def resample_speed_for_loc(session, filter_after, filter_before, loc_id):
    base_query = select(LocomotiveSpeedMessage.timestamp, LocomotiveSpeedMessage.speed).filter(LocomotiveSpeedMessage.loc_id == loc_id)
    results_after = (await session.execute(base_query.order_by(asc(LocomotiveSpeedMessage.timestamp)).filter(LocomotiveSpeedMessage.timestamp >= filter_after).filter(LocomotiveSpeedMessage.timestamp < filter_before))).fetchall()
    result_before = (await session.execute(base_query.order_by(desc(LocomotiveSpeedMessage.timestamp)).filter(LocomotiveSpeedMessage.timestamp < filter_after).limit(1))).fetchall()

    results_after_count = len(results_after)

    has_before = len(result_before) == 1

    total_duration = (filter_before - filter_after).total_seconds()

    if results_after_count == 0:
        if has_before:
            return result_before[0][1] * total_duration
        return 0

    distance_sum = 0

    # First data point; Boundary check
    if has_before:
        previous_value = result_before[0][1]
    else:
        previous_value = results_after[0][1]

    duration = (results_after[0][0] - filter_after).total_seconds()
    distance_sum += previous_value * duration


    for i in range(0, results_after_count):
        if i == results_after_count - 1:
            duration = (filter_before - results_after[i][0]).total_seconds()
        else:
            duration = (results_after[i + 1][0] - results_after[i][0]).total_seconds()
        
        distance_sum += results_after[i][1] * duration

    return distance_sum


# TODO check if attributes are nullable
async def resample_fuel_for_loc(session, filter_after, filter_before, mfxuid):
    base_query = select(ConfigUsageMessage.timestamp, ConfigUsageMessage.fuelA, ConfigUsageMessage.fuelB, ConfigUsageMessage.sand).filter(ConfigUsageMessage.mfxuid == mfxuid)
    results_after = (await session.execute(base_query.order_by(asc(ConfigUsageMessage.timestamp)).filter(ConfigUsageMessage.timestamp >= filter_after).filter(ConfigUsageMessage.timestamp < filter_before))).fetchall()
    result_before = (await session.execute(base_query.order_by(desc(ConfigUsageMessage.timestamp)).filter(ConfigUsageMessage.timestamp < filter_after).limit(1))).fetchall()

    results_after_count = len(results_after)

    has_before = len(result_before) == 1

    total_duration = (filter_before - filter_after).total_seconds()

    if results_after_count == 0:
        return 0, 0, 0

    def default_0(value):
        if value is None:
            return 0
        return value

    def fuel_a_at(index):
        return default_0(results_after[index][1])

    def fuel_b_at(index):
        return default_0(results_after[index][2])

    def sand_at(index):
        return default_0(results_after[index][3])

    fuel_a_sum = 0
    fuel_b_sum = 0
    sand_sum = 0

    # First data point; Boundary check
    if has_before:
        previous_a_value = default_0(result_before[0][1])
        previous_b_value = default_0(result_before[0][2])
        previous_sand_value = default_0(result_before[0][3])
    else:
        previous_a_value = fuel_a_at(0)
        previous_b_value = fuel_b_at(0)
        previous_sand_value = sand_at(0)

    duration = (results_after[0][0] - filter_after).total_seconds()
    fuel_a_sum += (fuel_a_at(0) - previous_a_value) / duration
    fuel_b_sum += (fuel_b_at(0) - previous_b_value) / duration
    sand_sum += (sand_at(0) - previous_sand_value) / duration


    for i in range(1, results_after_count):
        duration = (results_after[i][0] - results_after[i - 1][0]).total_seconds()
        
        fuel_a_sum += (fuel_a_at(i) - fuel_a_at(i - 1)) / duration
        fuel_b_sum += (fuel_b_at(i) - fuel_b_at(i - 1)) / duration
        sand_sum += (sand_at(i) - sand_at(i - 1)) / duration

    fuel_a_sum /= results_after_count
    fuel_b_sum /= results_after_count
    sand_sum /= results_after_count
    return fuel_a_sum, fuel_b_sum, sand_sum


async def resample(session, start, end):
    loc_ids = (await session.execute(select(ConfigLocomotiveMessage.uid, ConfigLocomotiveMessage.mfxuid))).fetchall()
    loc_ids = set((t[0], t[1]) for t in loc_ids) # deduplicate
    for (loc_id, mfxuid) in loc_ids:
        distance = await resample_speed_for_loc(session, start, end, loc_id)
        fuel_a, fuel_b, sand = await resample_fuel_for_loc(session, start, end, mfxuid)

        timestamp_iso = time.mktime(end.timetuple())
        await dump_model(session, \
            LocomotiveMetricMessage(timestamp=end, timestamp_iso=timestamp_iso, mfxuid=mfxuid, loc_id=loc_id, fuelA=fuel_a, fuelB=fuel_b, sand=sand, distance=distance))


async def start_resampler():
    last = datetime.now()
    resample_interval = settings.high_level_db_dump_resample_interval
    resample_delta = timedelta(seconds = resample_interval)
    async with SessionLocal() as session:
        while True:
            now = datetime.now()
            elapsed_seconds = (now - last).seconds
            if now < last or elapsed_seconds < resample_interval:
                remaining = resample_interval - (now - last).seconds
                print(f"sleeping {remaining}s")
                await asyncio.sleep(remaining)
                continue
            start = last
            end = last + resample_delta
            await resample(session, start, end)
            last = end


async def start_websocket_listener():
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        async with SessionLocal() as session:
            print("connected")
            async for message in websocket:
                print(message)
                pydantic_abstract_message = await parse_message(message)
                print(pydantic_abstract_message.get_command())
                if pydantic_abstract_message.get_command() == CommandSchema.ConfigDataStream:
                    await process_config_stream(session, websocket, pydantic_abstract_message)
                else:
                    await dump(session, pydantic_abstract_message)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    loop.create_task(start_resampler())
    loop.create_task(start_websocket_listener())
    loop.run_forever()

if __name__ == "__main__":
    main()
