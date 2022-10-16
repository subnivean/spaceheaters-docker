from datetime import datetime
import paramiko

class Reading():
    def __init__(self, record, channel):
        self.record = record
        self.channel = channel
        self.datetimestr = self.record.split()[0]
        self.datetime = datetime.fromisoformat(self.datetimestr.split('.')[0])
        self.amps = float(self.record.split()[self.channel])

    @property
    def timedelta(self):
        return (datetime.now() - self.datetime).seconds


class HeatPump():
    def __init__(self, which, ip, user="pi", key="./id_rsa_rpi", channel=4):
        """Connect to a Raspberry Pi that is reading
        heat pump current settings via a XXX HAT to
        get useful data about the heat pump state.
        """
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file("./id_rsa_rpi")
        self.client.connect(ip, username=user, pkey=pkey)
        self.channel = channel
        self.which = which

    @property
    def is_on(self):
        pass

    def get_last_reading(self):
        cmd = f"tail -n1 {self.which}_heat_pump_ct_readings.log"
        stdin, _stdout, _stderr = self.client.exec_command(cmd)
        reading = Reading(_stdout.read().decode(), self.channel)
        return reading

    @property
    def is_defrosting(self):
        # hhpwatts = $(ssh hhpmonpi tail -n1 house_heat_pump_ct_readings.log |cut -d',' -f5)
        pass

if __name__ == "__main__":
    which = 'house'
    ip = "192.168.1.9"
    hp = HeatPump(which, ip)