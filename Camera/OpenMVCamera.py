import serial
import time
import struct


class OpenMVCamera():

    def __init__(self, com):
        self.picture = None
        self.fps = None
        self.size = None
        self.frame = 0
        self.serial = serial.Serial(com, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                    xonxoff=False, rtscts=False, stopbits=serial.STOPBITS_ONE, timeout=None,
                                    dsrdtr=True)
        self.serial.setDTR(True)  # dsrdtr is ignored on Windows.
        self.serial.write(b'wledd')
        self.contrast = round(4/7,2)
        self.brightness= round(4/7,2)
        self.saturation= round(4/7,2)

    def photo(self):
        start_time = time.time()
        self.serial.write(b'photo')
        size = struct.unpack('<L', self.serial.read(4))[0]
        self.serial.flush()
        self.picture = self.serial.read(size)
        self.fps = 1/(time.time()-start_time)
        self.frame=self.frame+1
        return self.picture

    def format(self,size):
        self.size = size
        if size=='40x30':
            self.serial.write(b'q4vga')
        elif size=='80x60':
            self.serial.write(b'q3vga')
        elif size == '160x120':
            self.serial.write(b'q2vga')
        elif size == '320*240':
            self.serial.write(b'q1vga')
        elif size == '640x480':
            self.serial.write(b'q0vga')
        else:
            print('Picture format not supported')
            self.size=b'ERROR'

    def flip(self,vertical_or_horizontal):
        if vertical_or_horizontal==b'vertical':
            self.serial.write(b'vflip')
        elif vertical_or_horizontal==b'horizontal':
            self.serial.write(b'hflip')

    def save(self,name):
        with open(name+'_'+str(self.frame)+'.jpg', 'wb+') as f:
            f.write(self.picture)

    def led(self, color):
        self.serial.write(b'ledr0')
        self.serial.write(b'ledg0')
        self.serial.write(b'ledb0')
        self.serial.write(b'ledi0')
        if color == b'red':
            self.serial.write(b'ledr1')
        elif color == b'green':
            self.serial.write(b'ledg1')
        elif color == b'blue':
            self.serial.write(b'ledb1')
        elif color == b'pink':
            self.serial.write(b'ledr1')
            self.serial.write(b'ledb1')
        elif color == b'cyan':
            self.serial.write(b'ledg1')
            self.serial.write(b'ledb1')
        elif color == b'yellow':
            self.serial.write(b'ledr1')
            self.serial.write(b'ledg1')
        elif color == b'white':
            self.serial.write(b'ledr1')
            self.serial.write(b'ledg1')
            self.serial.write(b'ledb1')

    def flash(self, color, time_ms):
        self.led(color)
        time.sleep(time_ms/1000)
        self.led(b'off')

    def contrast(self, fraction):
        fraction = max(min(fraction,0),1)
        current_code = round(self.contrast*7,0)
        next_code = round(fraction*7,0)
        while next_code>current_code:
            self.serial.write(b'ctrt+')
            current_code = current_code+1
        while next_code < current_code:
            self.serial.write(b'ctrt-')
            current_code = current_code-1
        self.contrast = round(current_code/7,2)

    def brightness(self, fraction):
        fraction = max(min(fraction,0),1)
        current_code = round(self.brightness*7,0)
        next_code = round(fraction*7,0)
        while next_code > current_code:
            self.serial.write(b'brgt+')
            current_code = current_code+1
        while next_code<current_code:
            self.serial.write(b'brgt-')
            current_code = current_code-1
        self.brightness = round(current_code/7,2)

    def saturation(self, fraction):
        fraction = max(min(fraction,0),1)
        current_code = round(self.saturation*7,0)
        next_code = round(fraction*7,0)
        while next_code > current_code:
            self.serial.write(b'satr+')
            current_code = current_code+1
        while next_code<current_code:
            self.serial.write(b'satr-')
            current_code = current_code-1
        self.saturation = round(current_code/7,2)

    def close(self):
        self.serial.write(b'wlede')
        self.serial.close()


if __name__ == '__main__':
    camera1 = OpenMVCamera('COM3')
    camera1.format('640x480')
    camera1.led(b'green')
    time.sleep(1)
    camera1.flash(b'white',100)
    time.sleep(0.5)
    camera1.flash(b'white', 100)
    time.sleep(0.5)
    camera1.flash(b'white', 100)
    time.sleep(0.5)
    for i in range(100):
        camera1.photo()
        print(camera1.fps)
    camera1.save('my_picture')
    camera1.close()