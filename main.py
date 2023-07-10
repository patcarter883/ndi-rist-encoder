from nicegui import ui
import sys
import gi
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

# initialize GStreamer
Gst.init(sys.argv[1:])

import ndi

ndi.start_device_monitor()
devices = {x:x.get_display_name() for x in ndi.get_devices()}

def play_source():
    pipeline = Gst.parse_launch(f'ndisrc ndi-name="{select1.value.get_properties().get_value("ndi-name")}" url-address={select1.value.get_properties().get_value("url-address")} ! ndisrcdemux name=demux   demux.video ! queue ! videoconvert ! autovideosink  demux.audio ! queue ! audioconvert ! autoaudiosink')
    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS
    )
    log.push(msg.parse_error())
    pipeline.set_state(Gst.State.NULL)

def start_output():
    pipeline = Gst.parse_launch(f'ndisrc ndi-name="{select1.value.get_properties().get_value("ndi-name")}" url-address={select1.value.get_properties().get_value("url-address")} ! ndisrcdemux name=demux   demux.video ! queue ! videoconvert ! autovideosink  demux.audio ! queue ! audioconvert ! autoaudiosink')
    pipeline.set_state(Gst.State.PLAYING)


with ui.row().classes('grid gap-4 grid-cols-2 grid-rows-1 w-full'):
    with ui.card().tight().props('flat bordered square').classes('w-full'):
        with ui.card_section():
            select1 = ui.select(devices ,label="NDI Source")
        with ui.card_section():
            ui.button(icon='play',on_click=play_source)
    with ui.card().tight().props('flat bordered square').classes('w-full'):
        with ui.card_section():
            ui.input(label='RIST URL')

ui.label('Log')
log = ui.log(max_lines=10).classes('w-full')

ui.run(native=True, title='NDI RIST Encoder')