import requests
import time


def get_all_devices():
    all_devices = requests.get(base_url + '/ZWaveAPI/Data/0', auth=(username, password)).json()
    # without auth, omit the last parameter
    # all_devices = requests.get(base_url + '/ZWaveAPI/Data/0')

    # clean up
    all_devices = all_devices['devices']
    # remove the Z-Way controller from the device list
    all_devices.pop('1')

    return all_devices


def set_value(device, instance, value):
    # turn it on (255) or off (0)
    url_to_call = (device_url + '.Set(' + str(value) + ')').format(device, instance, switch_binary)
    requests.get(url_to_call, auth=(username, password))


def get_values(device, instance, command_class):
    # get data from the multilevel class
    url_to_call = device_url.format(device, instance, command_class)
    # info from devices is in the response
    return requests.get(url_to_call, auth=(username, password)).json()


def main():
    # get all the associated z-wave devices
    all_devices = get_all_devices()

    # search for devices to be "operated", in this case power outlets, temperature, and motion sensors
    for device_key in all_devices:
        # iterate over device instances
        for instance in all_devices[device_key]['instances']:
            # search for the SwitchBinary (37) command class, i.e., power outlets
            if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
                print('Turning on device %s...' % device_key)
                set_value(device_key, instance, 255)
            # search for the SensorMultilevel (49) command class, e.g., for temperature
            if sensor_multi in all_devices[device_key]['instances'][instance]['commandClasses']:
                # debug
                print('Device %s is a sensor multilevel' % device_key)
                response = get_values(device_key, instance, sensor_multi)
                # 1: temperature, 3: luminosity, 5: humidity (numbers must be used as strings)
                val = response['data']['1']['val']['value']
                unit_of_measure = response['data']['1']['scaleString']['value']
                print('The temperature is ' + str(val) + unit_of_measure)
            # search for the SensorBinary (48) command class, e.g., for motion
            if sensor_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
                # debug
                print('Device %s is a sensor binary' % device_key)
                # get motion
                response = get_values(device_key, instance, sensor_binary)
                val = response['data']['1']['level']['value']
                print('Motion: ' + str(val))

    # reverse count to off
    for i in range(0, 10):
        time.sleep(1)
        print(10 - i)

    # search for power outlets, again
    for device_key in all_devices:
        # iterate over device instances
        for instance in all_devices[device_key]['instances']:
            # search for the SwitchBinary (37) command class, i.e., power outlets
            if switch_binary in all_devices[device_key]['instances'][instance]['commandClasses']:
                print('Turning off device %s...' % device_key)
                set_value(device_key, instance, 0)


if __name__ == '__main__':

    # the base url
    base_url = 'http://192.168.0.202:8083'

    # login credentials, to be replaced with the right ones
    # N.B. authentication may be disabled from the configuration of the 'Z-Wave Network Access' app
    # from the website available at 'base_url'
    username = 'admin'
    password = 'admin'

    # "prototype" and base URL for getting/setting device properties
    device_url = base_url + '/ZWaveAPI/Run/devices[{}].instances[{}].commandClasses[{}]'

    # some useful command classes
    switch_binary = '37'
    sensor_binary = '48'
    sensor_multi = '49'

    main()
