from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import time
from typing import List

from app.schemas.can import Command
from ..schemas.can_commands import CommandSchema
from ..schemas.can_commands.system import SystemSubcommand, SystemSubcommandSchema
from ..utils.coding import to_int_safe


Base = declarative_base()


class AbstractCANMessage(Base):
    __abstract__ = True
    timestamp = Column(DateTime, primary_key=True)
    timestamp_iso = Column(Integer, primary_key=True)
    hash_value = Column(Integer, primary_key=True)
    response = Column(Boolean, primary_key=True)

    def from_schema(can_message):
        current_date = datetime.now()
        timestamp = current_date
        timestamp_iso = time.mktime(current_date.timetuple())
        hash_value = can_message.hash_value
        response = can_message.response

        return AbstractCANMessage(timestamp=timestamp, timestamp_iso=timestamp_iso, hash_value=hash_value, response=response)


class AbstractLocomotiveMessage(AbstractCANMessage):
    __abstract__ = True
    loc_id = Column(Integer, primary_key=True)

    def from_schema(can_message):
        abstract_message = AbstractCANMessage.from_schema(can_message)
        loc_id = can_message.loc_id
        return AbstractLocomotiveMessage(loc_id=loc_id, **vars(abstract_message))


class LocomotiveSpeedMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_speed'
    speed = Column(Integer, nullable=True)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.LocomotiveSpeed:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        speed = can_message.speed

        return LocomotiveSpeedMessage(speed=speed, **vars(locomotive_message))


class LocomotiveDirectionMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_direction'
    direction = Column(Text, nullable=True)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.LocomotiveDirection:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        direction = None
        if can_message.direction is not None:
            direction = can_message.direction.value

        return LocomotiveDirectionMessage(direction=direction, **vars(locomotive_message))


class LocomotiveFunctionMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_function'
    function = Column(Integer, nullable=False)
    value = Column(Integer)
    function_value = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.LocomotiveFunction:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        function = can_message.function
        value = can_message.value
        function_value = can_message.function_value

        return LocomotiveFunctionMessage(function=function, value=value, function_value=function_value, **vars(locomotive_message))


class SwitchingAccessoriesMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'switching_accessories'
    position = Column(Integer, nullable=False)
    power = Column(Integer, nullable=False)
    value = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SwitchingAccessories:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        position = can_message.position
        power = can_message.power
        value = can_message.value

        return SwitchingAccessoriesMessage(position=position, power=power, value=value, **vars(locomotive_message))


class S88PollingMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 's88_polling'
    module_count = Column(Integer)
    module = Column(Integer)
    state = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.S88Polling:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        module_count = can_message.module_count
        module = can_message.module
        state = can_message.state

        return S88PollingMessage(module_count=module_count, module=module, state=state, **vars(locomotive_message))


class ReadConfigMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'read_config'
    index = Column(Integer, primary_key=True)
    number = Column(Integer, primary_key=True)
    count = Column(Integer)
    value = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.ReadConfig:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        index = can_message.index
        number = can_message.number
        count = can_message.count
        value = can_message.value

        return ReadConfigMessage(index=index, number=number, count=count, value=value, **vars(locomotive_message))


class WriteConfigMessage(AbstractLocomotiveMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'write_config'
    index = Column(Integer, primary_key=True)
    number = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    is_main = Column(Boolean)
    is_multi_byte = Column(Boolean)
    dcc_programming = Column(Text)
    is_write_successful = Column(Boolean)
    is_verify_successful = Column(Boolean)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.WriteConfig:
            return None

        locomotive_message = AbstractLocomotiveMessage.from_schema(can_message)
        index = can_message.index
        number = can_message.number
        value = can_message.value

        is_main = None
        is_multi_byte = None
        dcc_programming = None
        is_write_successful = None
        is_verify_successful = None

        if not can_message.control is None:
            is_main = can_message.control.is_main
            is_multi_byte = can_message.control.is_multi_byte
            dcc_programming = can_message.control.dcc_programming.value

        if not can_message.result is None:
            is_write_successful = can_message.result.is_write_successful
            is_verify_successful = can_message.result.is_verify_successful

        return WriteConfigMessage(index=index, number=number, value=value, is_main=is_main, is_multi_byte=is_multi_byte, dcc_programming=dcc_programming, is_write_successful=is_write_successful, is_verify_successful=is_verify_successful, **vars(locomotive_message))


class AbstractSystemMessage(AbstractCANMessage):
    __abstract__ = True
    id = Column(Integer, primary_key=True)

    def from_schema(can_message):
        abstract_message = AbstractCANMessage.from_schema(can_message)
        id = can_message.id
        return AbstractSystemMessage(id=id, **vars(abstract_message))


class SystemStateMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'system_state'
    state = Column(Text, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        sub_command = can_message.get_subcommand()
        if not sub_command in [SystemSubcommandSchema.SystemStop, SystemSubcommandSchema.SystemGo, SystemSubcommandSchema.SystemHalt]:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)

        state = ""
        if sub_command == SystemSubcommandSchema.SystemStop:
            state = "stop"
        elif sub_command == SystemSubcommandSchema.SystemGo:
            state = "go"
        elif sub_command == SystemSubcommandSchema.SystemHalt:
            state = "halt"
        assert not state == ""

        return SystemStateMessage(state=state, **vars(abstract_message))


class LocomotiveEmergencyStopMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_emergency_stop'

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.LocomotiveEmergencyStop:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)

        return LocomotiveEmergencyStopMessage(**vars(abstract_message))


class LocomotiveCycleStopMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_cycle_stop'

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.LocomotiveCycleStop:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)

        return LocomotiveCycleStopMessage(**vars(abstract_message))


class LocomotiveDataProtocolMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_data_protocol'
    protocol = Column(Text, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.LocomotiveDataProtocol:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        protocol = can_message.protocol.value
        return LocomotiveDataProtocolMessage(protocol=protocol, **vars(abstract_message))


class AccessoryDecoderSwitchingTimeMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'accessory_decoder_switching_time'
    time = Column(Integer, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.AccessoryDecoderSwitchingTime:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        time = can_message.time
        return AccessoryDecoderSwitchingTimeMessage(time=time, **vars(abstract_message))


class MfxFastReadMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'mfx_fast_read'
    mfx_sid = Column(Integer, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.MfxFastRead:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        mfx_sid = can_message.mfx_sid
        return MfxFastReadMessage(mfx_sid=mfx_sid, **vars(abstract_message))


class EnableRailProtocolCommand(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'enable_rail_protocol'
    bitset = Column(Integer, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.EnableRailProtocol:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        bitset = can_message.bitset
        return EnableRailProtocolCommand(bitset=bitset, **vars(abstract_message))


class SetMfxRegisterCounterMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'set_mfx_register_counter'
    counter = Column(Integer, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.SetMfxRegisterCounter:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        counter = can_message.counter
        return SetMfxRegisterCounterMessage(counter=counter, **vars(abstract_message))


class SystemOverloadMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'system_overload'
    channel = Column(Integer, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.SystemOverload:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        channel = can_message.channel
        return SystemOverloadMessage(channel=channel, **vars(abstract_message))


class SystemStatusMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'system_status'
    channel = Column(Integer, nullable=False)
    measured_value = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.SystemStatus:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        channel = can_message.channel
        measured_value = can_message.measured_value
        return SystemStatusMessage(channel=channel, measured_value=measured_value, **vars(abstract_message))


class SetSystemIdentifierMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'set_system_identifier'
    system_id = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.SetSystemIdentifier:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        system_id = can_message.system_id
        return SetSystemIdentifierMessage(system_id=system_id, **vars(abstract_message))


class MfxSeekMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'mfx_seek'

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.MfxSeek:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        return MfxSeekMessage(**vars(abstract_message))


class SystemResetMessage(AbstractSystemMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'system_reset'
    target = Column(Integer, primary_key=True)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.SystemCommand:
            return None
        if not can_message.get_subcommand() == SystemSubcommandSchema.SystemReset:
            return None

        abstract_message = AbstractSystemMessage.from_schema(can_message)
        target = can_message.target
        return SystemResetMessage(target=target, **vars(abstract_message))


class ConfigMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'config'
    config = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)

    def from_schema(abstract_pydantic_message):
        return None

    def from_message(data, length, base_pydantic_message):
        abstract_message = AbstractCANMessage.from_schema(
            base_pydantic_message)
        return ConfigMessage(config=data, length=length, **vars(abstract_message))

class LocomotiveMetricMessage(Base):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_metrics'

    timestamp = Column(DateTime, primary_key=True)
    timestamp_iso = Column(Integer, primary_key=True)
    mfxuid = Column(Integer, primary_key=True)
    loc_id = Column(Integer, primary_key=True)
    fuelA = Column(Integer)
    fuelB = Column(Integer)
    sand = Column(Integer)
    distance = Column(Integer)

    def from_schema(abstract_pydantic_message):
        return None


class ConfigUsageMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'config_usage'
    mfxuid = Column(Integer, primary_key=True)
    maxFuelA = Column(Integer, nullable=True)
    maxFuelB = Column(Integer, nullable=True)
    maxSand = Column(Integer, nullable=True)
    faktorFuelA = Column(Integer, nullable=True)
    fuelA = Column(Integer, nullable=True)
    fuelB = Column(Integer, nullable=True)
    sand = Column(Integer, nullable=True)
    alter = Column(Integer, nullable=True)

    def from_schema(abstract_pydantic_message):
        return None

    def from_message(obj, base_pydantic_message):
        abstract_message = AbstractCANMessage.from_schema(
            base_pydantic_message)
        lok = obj["lok"]
        mfxuid = int(lok["mfxuid"], 0)
        maxFuelA = to_int_safe(lok.get("maxFuelA"))
        maxFuelB = to_int_safe(lok.get("maxFuelB"))
        maxSand = to_int_safe(lok.get("maxSand"))
        faktorFuelA = to_int_safe(lok.get("faktorFuelA"))
        fuelA = to_int_safe(lok.get("fuelA", None))
        fuelB = to_int_safe(lok.get("fuelB", None))
        sand = to_int_safe(lok.get("sand", None))
        alter = to_int_safe(lok.get("alter", None))
        return ConfigUsageMessage(
            mfxuid=mfxuid,
            maxFuelA=maxFuelA,
            maxFuelB=maxFuelB,
            maxSand=maxSand,
            faktorFuelA=faktorFuelA,
            fuelA=fuelA,
            fuelB=fuelB,
            sand=sand,
            alter=alter,
            **vars(abstract_message)
        )


class ConfigLocomotiveMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'config_locomotive'
    name = Column(Text, nullable=False)
    vorname = Column(Text)
    uid = Column(Integer, nullable=False)
    mfxuid = Column(Integer, nullable=False)
    adresse = Column(Integer, nullable=False)
    icon = Column(Text)
    typ = Column(Text, nullable=None)
    sid = Column(Integer)
    symbol = Column(Integer)
    tachomax = Column(Integer)
    vmax = Column(Integer, nullable=False)
    vmin = Column(Integer, nullable=False)
    av = Column(Integer, nullable=True)
    bv = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=False)
    spa = Column(Integer)
    spm = Column(Integer)
    ft = Column(Integer)
    velocity = Column(Integer)
    richtung = Column(Integer)
    mfxtyp = Column(Integer)
    blocks = Column(Text)

    def from_schema(abstract_pydantic_message):
        return None

    def from_message(lok, base_pydantic_message):
        abstract_message = AbstractCANMessage.from_schema(
            base_pydantic_message)
        name = lok["name"]
        vorname = lok.get("vorname", None)
        uid = int(lok["uid"], 0)
        mfxuid = int(lok["mfxuid"], 0)
        adresse = lok["adresse"]
        icon = lok.get("icon", None)
        typ = lok["typ"]
        sid = to_int_safe(lok.get("sid", None))
        symbol = lok.get("symbol", None)
        tachomax = to_int_safe(lok.get("tachomax", None))
        vmax = int(lok["vmax"], 0)
        vmin = int(lok["vmin"], 0)
        av = to_int_safe(lok.get("av", None))
        bv = to_int_safe(lok.get("bv", None))
        volume = lok["volume"]
        spa = lok.get("spa", None) # TODO determine types
        spm = lok.get("spm", None)
        ft = lok.get("ft", None)
        velocity = to_int_safe(lok.get("velocity", None))
        richtung = lok.get("richtung", None)
        mfxtyp = lok.get("mfxtyp", None)
        blocks = lok.get("blocks", None)
        return ConfigLocomotiveMessage(
            name=name,
            vorname=vorname,
            uid=uid,
            mfxuid=mfxuid,
            adresse=adresse,
            icon=icon,
            typ=typ,
            sid=sid,
            symbol=symbol,
            tachomax=tachomax,
            vmax=vmax,
            vmin=vmin,
            av=av,
            bv=bv,
            volume=volume,
            spa=spa,
            spm=spm,
            ft=ft,
            velocity=velocity,
            richtung=richtung,
            mfxtyp=mfxtyp,
            blocks=blocks,
            **vars(abstract_message)
        )


class RequestConfigDataMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'request_config_data'
    filename = Column(Text, nullable=False)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.RequestConfigData:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)
        filename = can_message.filename
        return RequestConfigDataMessage(filename=filename, **vars(abstract_message))


class ParticipantPingMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'participant_ping'
    sender_id = Column(Integer)
    software_version = Column(Integer)
    device_id = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.ParticipantPing:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)

        sender_id = can_message.sender_id
        software_version = can_message.software_version
        device_id = can_message.device_id

        return ParticipantPingMessage(sender_id=sender_id, software_version=software_version, device_id=device_id, **vars(abstract_message))


class LocomotiveDiscoveryMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'locomotive_discovery'
    loc_id = Column(Integer)
    protocol = Column(Text)
    mfx_range = Column(Integer)
    ask_ratio = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.LocomotiveDiscovery:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)

        loc_id = can_message.loc_id
        protocol = ""
        if not can_message.protocol is None:
            protocol = can_message.protocol.value
        mfx_range = can_message.mfx_range
        ask_ratio = can_message.ask_ratio

        return LocomotiveDiscoveryMessage(loc_id=loc_id, protocol=protocol, mfx_range=mfx_range, ask_ratio=ask_ratio, **vars(abstract_message))


class S88EventMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 's88_event'
    device_id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, primary_key=True)
    state_old = Column(Integer)
    state_new = Column(Integer)
    time = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.S88Event:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)

        device_id = can_message.device_id
        contact_id = can_message.contact_id
        state_old = can_message.state_old
        state_new = can_message.state_new
        time = can_message.time

        return S88EventMessage(device_id=device_id, contact_id=contact_id, state_old=state_old, state_new=state_new, time=time, **vars(abstract_message))


class ServiceStatusDataConfigurationMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'service_status_data_configuration'
    device_id = Column(Integer)
    index = Column(Integer)
    count = Column(Integer)
    data = Column(Text)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.ServiceStatusDataConfiguration:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)

        device_id = can_message.device_id
        index = can_message.index
        count = can_message.count
        data = can_message.data

        return ServiceStatusDataConfigurationMessage(device_id=device_id, index=index, count=count, data=data, **vars(abstract_message))


class BootloaderCANBoundMessage(AbstractCANMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'bootloader_can_bound'
    data = Column(Text)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.BootloaderCANBound:
            return None

        abstract_message = AbstractCANMessage.from_schema(can_message)

        data = can_message.data

        return BootloaderCANBoundMessage(data=data, **vars(abstract_message))


class AbstractMfxMessage(AbstractCANMessage):
    __abstract__ = True
    mfx_uid = Column(Integer, primary_key=True)
    mfx_sid = Column(Integer, primary_key=True)

    def from_schema(can_message):
        abstract_message = AbstractCANMessage.from_schema(can_message)
        mfx_uid = can_message.mfx_uid
        mfx_sid = can_message.mfx_sid
        return AbstractMfxMessage(mfx_uid=mfx_uid, mfx_sid=mfx_sid, **vars(abstract_message))


class MfxBindMessage(AbstractMfxMessage):
    __tablename__ = 'mfx_bind'

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.MFXBind:
            return None

        abstract_message = AbstractMfxMessage.from_schema(can_message)

        return MfxBindMessage(**vars(abstract_message))


class MfxVerifyMessage(AbstractMfxMessage):
    __mapper_args__ = {
        'concrete': True
    }
    __tablename__ = 'mfx_verify'
    ask_ratio = Column(Integer)

    def from_schema(can_message):
        if not can_message.get_command() == CommandSchema.MFXVerify:
            return None

        abstract_message = AbstractMfxMessage.from_schema(can_message)
        ask_ratio = can_message.ask_ratio
        return MfxVerifyMessage(ask_ratio=ask_ratio, **vars(abstract_message))
