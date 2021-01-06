import struct
from ctypes import create_string_buffer

def create_radar_VIN_msg(radarId, radarVIN, radarCAN, radarTriggerMessage, useRadar, radarPosition, radarEpasType):
  msg_id = 0x560
  msg_len = 8
  msg = create_string_buffer(msg_len)
  if radarId == 0:
    struct.pack_into('BBBBBBBB', msg, 0, radarId, radarCAN, useRadar + (radarPosition << 1) + (radarEpasType << 3), (radarTriggerMessage >> 8) & 0xFF, radarTriggerMessage & 0xFF, ord(radarVIN[0]), ord(radarVIN[1]), ord(radarVIN[2]))
  if radarId == 1:
    struct.pack_into('BBBBBBBB', msg, 0, radarId, ord(radarVIN[3]), ord(radarVIN[4]), ord(radarVIN[5]), ord(radarVIN[6]), ord(radarVIN[7]), ord(radarVIN[8]), ord(radarVIN[9]))
  if radarId == 2:
    struct.pack_into('BBBBBBBB', msg, 0, radarId, ord(radarVIN[10]), ord(radarVIN[11]), ord(radarVIN[12]), ord(radarVIN[13]), ord(radarVIN[14]), ord(radarVIN[15]), ord(radarVIN[16]))
  return [msg_id, 0, msg.raw, 0]
