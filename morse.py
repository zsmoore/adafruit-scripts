import board
import time
import neopixel
import digitalio

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.raw_text_packet import RawTextPacket

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_debouncer import Debouncer

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

button_a = digitalio.DigitalInOut(board.BUTTON_A)
button_b = digitalio.DigitalInOut(board.BUTTON_B)
button_a.switch_to_input(pull=digitalio.Pull.DOWN)
button_b.switch_to_input(pull=digitalio.Pull.DOWN)
button_a = Debouncer(button_a)
button_b = Debouncer(button_b)

switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)

YELLOW = (255, 150, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLANK = (0, 0, 0)

alphabet = [
    [.75, 2],            #a
    [2, .75, .75, .75],  #b
    [2, .75, 2, .75],    #c
    [2, .75, .75],       #d
    [.75],               #e
    [.75, .75, 2, .75],  #f
    [2, 2, .75],         #g
    [.75, .75, .75, .75],#h
    [.75, .75],          #i
    [.75, 2, 2, 2],      #j
    [2, .75, 2],         #k
    [.75, 2, .75, .75],  #l
    [2, 2],              #m
    [2, .75],            #n
    [2, 2, 2],           #o
    [.75, 2, 2, .75],    #p
    [2, 2, .75, 2],      #q
    [.75, 2, .75],       #r
    [.75, .75, .75],     #s
    [2],                 #t
    [.75, .75, 2],       #u
    [.75, .75, .75, 2],  #v
    [.75, 2, 2],         #w
    [2, .75, .75, 2],    #x
    [2, .75, 2, 2],      #y
    [2, 2, .75, .75]     #z
]


def get_word(uart_server):
    packet = Packet.from_stream(uart_server)
    if isinstance(packet, RawTextPacket):
        return packet.text.decode('utf-8')

def connect():
    ble.start_advertising(advertisement)
    while not ble.connected:
        print('not connected')
        time.sleep(1)
        pass
    ble.stop_advertising()

def read_morse():
    word = None
    while ble.connected:
        if uart_server.in_waiting:
            word = get_word(uart_server)
            if word is not None:
                return word

def get_morse_arr(word):
    word = word.lower()
    arr = []
    for ch in word:
        index = ord(ch) - 97
        arr.append(alphabet[index])
    return arr


def flash_pixels_and_wait_input(morse_arr):
    while True:
        if switch.value:
            res = capture_input(morse_arr)
            if res:
                pixels.fill(BLANK)
                pixels.show()
                return
        time.sleep(1)
        for arr in morse_arr:
            for pulse in arr:
                pixels.fill(YELLOW)
                pixels.show()
                time.sleep(pulse)
                pixels.fill(BLANK)
                pixels.show()
                time.sleep(.2)
            time.sleep(2)


def capture_input(morse_arr):
    pixels.fill(BLUE)
    pixels.show()
    inputs = []
    while True:
        button_a.update()
        button_b.update()
        if not switch.value:
            flat = [item for sub_list in morse_arr for item in sub_list]
            print('guessed ' + ', '.join([str(i) for i in inputs]))
            print('flat ' + ', '.join([str(i) for i in flat]))
            if flat == inputs:
                pixels.fill(GREEN)
                pixels.show()
                time.sleep(3)
                return True
            else:
                pixels.fill(RED)
                pixels.show()
                time.sleep(3)
                return False 
        if button_a.rose:
            inputs.append(.75)
        elif button_b.rose:
            inputs.append(2)


def begin_morse(word):
    morse_arr = get_morse_arr(word)
    flash_pixels_and_wait_input(morse_arr)


def main():
    connect()
    while True:
        word = read_morse()
        begin_morse(word)


main()



