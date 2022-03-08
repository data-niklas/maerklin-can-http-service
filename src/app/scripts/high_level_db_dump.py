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
async def resample_speed_for_loc(session, start, end, loc_id):
    base_query = select(LocomotiveSpeedMessage.timestamp, LocomotiveSpeedMessage.speed) \
        .filter(LocomotiveSpeedMessage.loc_id == loc_id)
    in_interval = (await session.execute( \
        base_query \
            .order_by(asc(LocomotiveSpeedMessage.timestamp)) \
            .filter(LocomotiveSpeedMessage.timestamp >= start) \
            .filter(LocomotiveSpeedMessage.timestamp < end) \
        )).fetchall()
    result_before = (await session.execute( \
        base_query \
            .order_by(desc(LocomotiveSpeedMessage.timestamp)) \
            .filter(LocomotiveSpeedMessage.timestamp < start) \
            .limit(1) \
        )).fetchall()

    number_points = len(in_interval)

    has_before = len(result_before) == 1
    if has_before:
        before = result_before[0]

    total_duration = (end - start).total_seconds()

    if number_points == 0:
        if has_before:
            return before[1] * total_duration
        return 0

    distance_sum = 0

    # First data point; Boundary check
    if has_before:
        previous_value = before[0][1]
    else:
        previous_value = 0

    duration = (in_interval[0][0] - start).total_seconds()
    distance_sum += previous_value * duration


    for i, (timestamp, distance) in enumerate(in_interval):
        if i == number_points - 1:
            next_timestamp = end
        else:
            next_timestamp = in_interval[i + 1][0]
        duration = (next_timestamp - timestamp).total_seconds()
        
        distance_sum += distance * duration

    return distance_sum


async def resample_fuel_for_loc(session, start, end, mfxuid):
    base_query = select(ConfigUsageMessage.timestamp, ConfigUsageMessage.fuelA, ConfigUsageMessage.fuelB, ConfigUsageMessage.sand) \
        .filter(ConfigUsageMessage.mfxuid == mfxuid)
    in_interval = (await session.execute(
        base_query \
            .order_by(asc(ConfigUsageMessage.timestamp)) \
            .filter(ConfigUsageMessage.timestamp >= start) \
            .filter(ConfigUsageMessage.timestamp < end) \
        )).fetchall()
    result_before = (await session.execute( \
        base_query \
            .order_by(desc(ConfigUsageMessage.timestamp)) \
            .filter(ConfigUsageMessage.timestamp < start) \
            .limit(1) \
        )).fetchall()

    in_interval_count = len(in_interval)

    has_before = len(result_before) == 1

    a_fuels = [(point[0], point[1]) for point in in_interval if point[1] is not None]
    b_fuels = [(point[0], point[2]) for point in in_interval if point[2] is not None]
    sands = [(point[0], point[3]) for point in in_interval if point[3] is not None]

    # First data point; Boundary check
    if has_before:
        before = result_before[0]
        before_timestamp = before[0]
        if before[1] is not None:
            a_fuels = [(before_timestamp, before[1])] + a_fuels
        if before[2] is not None:
            b_fuels = [(before_timestamp, before[2])] + a_fuels
        if before[3] is not None:
            sands = [(before_timestamp, before[3])] + sands

    def mean_interval_difference(values):
        ret = 0
        for (timestamp_before, value_before), (timestamp_now, value_now) in zip(values, values[1:]):
            duration = (timestamp_now - timestamp_before).total_seconds()
            ret += (value_now - value_before) / duration
        return ret

    fuel_a_sum = mean_interval_difference(a_fuels)
    fuel_b_sum = mean_interval_difference(b_fuels)
    sand_sum = mean_interval_difference(sands)

    # we calculate n - 1 intervals for n values
    if len(a_fuels) > 1:
        fuel_a_sum /= len(a_fuels) - 1
    if len(b_fuels) > 1:
        fuel_b_sum /= len(b_fuels) - 1
    if len(sands) > 1:
        sand_sum /= len(sands) - 1
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
