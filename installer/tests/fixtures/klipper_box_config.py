# Reduced excerpt of QIDI Max 4 firmware 01.01.07.01 /home/qidi/klipper/klippy/extras/box_config.py.
# Klipper is distributed under GNU GPLv3. The live file uses CRLF line endings.
import configparser
import configfile

class Boxconfig:
    def build_config(self, name, num, module, config):
        fileconfig = configparser.ConfigParser()
        section_name = name

        fileconfig.add_section(section_name)
        if module == 'heater_generic':
            for key in ("heater_pin", "sensor_type", "min_temp", "max_temp", "target_max_temp"):
                fileconfig.set(section_name, key, config.get(key + "_" + str(module)))
        access_tracking = {}
        fake_cfg = configfile.ConfigWrapper(
            self.printer, fileconfig, access_tracking, section_name
        )
        return fake_cfg

def load_config_prefix(config):
    return Boxconfig(config)
