import paramiko

class HeatPump():
    def __init__(self, ip, user, key):
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file("./id_rsa_rpi")
        self.client.connect(ip, username=user, pkey=pkey)

    @property
    def is_on(self):
        pass

    @property
    def is_defrosting(self):
        # hhpwatts = $(ssh hhpmonpi tail -n1 house_heat_pump_ct_readings.log |cut -d',' -f5)
        pass

if __name__ == "__main__":
    ip = "192.168.1.9"
    key = "./id_rsa_rpi"
    user = "pi"
    hp = HeatPump(ip, user, key)
    stdin, _stdout,_stderr = hp.client.exec_command('tail -n1 house_heat_pump_ct_readings.log')
    # hp.client.exec_command("df")
    print(_stdout.read().decode())
    hp.client.close()