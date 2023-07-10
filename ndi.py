import sys
import gi
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

deviceMonitor = None
monitorBus = None
monitorMsg = None
devices = []

deviceMonitor = Gst.DeviceMonitor.new()
deviceMonitor.add_filter(None, Gst.caps_from_string('application/x-ndi'))
monitorBus = deviceMonitor.get_bus()

def start_device_monitor():
    deviceMonitor.start()
    while 1:
        monitorMsg = monitorBus.timed_pop_filtered(0, Gst.MessageType.DEVICE_ADDED)
        if monitorMsg:
            devices.append(monitorMsg.parse_device_added().get_display_name())
        else:
            break
    
def stop_device_monitor():
    deviceMonitor.stop()

def get_devices():
    return deviceMonitor.get_devices()
