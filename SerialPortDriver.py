from PyQt5.QtSerialPort import QSerialPortInfo
import serial

class SP():

    def __init__(self):
        self.connection = serial.Serial(parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=0.1,
                                        xonxoff=False)

    def get_available_ports(self):
        ports = QSerialPortInfo.availablePorts()
        portsName = [p.portName() for p in ports]
        # discriptions = [p.description() for p in ports]
        # return dict(zip(portsName, discriptions))
        return portsName

    def open_port(self, port_name):
        if not self.connection.isOpen():
            try:
                self.connection.setPort(port_name)
                self.connection.open()
                return True
            except Exception:
                print("Could not open port " + port_name)
                return False
        else:
            return True

    def close_port(self):
        if self.connection.isOpen():
            self.connection.close()

    def is_open(self):
        return self.connection.isOpen()

    def write(self, data):
        return self.connection.write(data)

    def read(self, len_data):
        return self.connection.read(len_data)

    def available_byte_in_port(self):
        return self.connection.inWaiting()



if __name__ == '__main__':

    sp = SP()
    print(sp.get_available_ports())
    if sp.open_port('COM2'):
        print(sp.write(bytes([0, 0x0E, 3])))
        print(sp.read(3))
        sp.close_port()

