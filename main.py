from nicegui import ui
import sys
import gi
import subprocess
import socket

gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib


# initialize GStreamer
Gst.init(sys.argv[1:])

import ndi

ndi.start_device_monitor()
devices = {x: x.get_display_name() for x in ndi.get_devices()}


def play_source():
    pipeline = Gst.parse_launch(
        f'ndisrc ndi-name="{select1.value.get_properties().get_value("ndi-name")}" url-address={select1.value.get_properties().get_value("url-address")} ! ndisrcdemux name=demux   demux.video ! queue ! videoconvert ! autovideosink  demux.audio ! queue ! audioconvert ! autoaudiosink'
    )
    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()
    if not bus:
        return
    msg = bus.timed_pop_filtered(
        Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS
    )
    if not msg:
        return
    log.push(msg.parse_error())
    pipeline.set_state(Gst.State.NULL)


def start_output():
    sourceDemux = (f'ndisrc ndi-name="{select1.value.get_properties().get_value("ndi-name")}" '
        f'url-address={select1.value.get_properties().get_value("url-address")} ! '
        'ndisrcdemux name=demux')
    
    videoEncode = ('demux.video ! queue ! videoconvert ! x264enc '
                    f'bitrate={bitrate.value} sliced-threads=true speed-preset=fast tune=zerolatency ! '
                    'h264parse config-interval=-1 ! h264timestamper ! rtph264pay pt=97 ! '
                     'udpsink host=127.0.0.1 port=5000')
    audioEncode = ('demux.audio ! queue ! audioconvert ! faac ! aacparse ! rtpmp4gpay pt=98 ! '
                    'udpsink host=127.0.0.1 port=5002')

    pipelineDescription = f'{sourceDemux} {videoEncode} {audioEncode}'
    try:
        global pipeline
        pipeline = Gst.parse_launch(pipelineDescription)
        pipeline.set_state(Gst.State.PLAYING)
    except GLib.GError as e:
        log.push(str(e))

    global ristSender
    ristSender = subprocess.Popen([
        'ristsender',
        '-i',
        'udp://@127.0.0.1:5000?stream-id=1000,udp://@127.0.0.1:5002?stream-id=2000',
        '-o',
        f'rist://{ristHost.value}:{ristPort.value}?timing-mode=2'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    startButton.disable()
    stopButton.enable()

def stop_output():
    pipeline.set_state(Gst.State.NULL)
    ristSender.terminate()
    startButton.enable()
    stopButton.disable()

with ui.row().classes("grid gap-4 grid-cols-2 grid-rows-1 w-full"):
    with ui.card().tight().props("flat bordered square").classes("w-full"):
        with ui.card_section():
            select1 = ui.select(devices, label="NDI Source")
        with ui.card_section():
            ui.button(icon="play_circle", on_click=play_source)
    with ui.card().tight().props("flat bordered square").classes("w-full"):
        with ui.card_section():
            ristHost = ui.input(label="RIST Host", value='127.0.0.1')
            ristPort = ui.input(label="RIST Port", value='6000')
            bitrate = ui.input(label="Bitrate kbit/sec", value='5000')
        with ui.card_section():
            startButton = ui.button(icon="live_tv", on_click=start_output)
            stopButton = ui.button(icon="stop", on_click=stop_output)
ui.label("Log")
log = ui.log(max_lines=10).classes("w-full")

ui.run(native=True, title="NDI RIST Encoder")
