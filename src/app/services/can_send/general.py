from fastapi import APIRouter

from ...utils.communication import send_can_message
from app.schemas.can_commands.general import *
from .helper import create_endpoint


router = APIRouter()
create_endpoint(router, "participant_ping", ParticipantPingCommand)
create_endpoint(router, "locomotive_discovery", LocomotiveDiscoveryCommand)
create_endpoint(router, "s88_event", S88EventCommand)
create_endpoint(router, "request_config_data", RequestConfigDataCommand)
create_endpoint(router, "service_status_data_configuration", ServiceStatusDataConfigurationCommand)
create_endpoint(router, "bootloader_can_bound", BootloaderCANBoundCommand)