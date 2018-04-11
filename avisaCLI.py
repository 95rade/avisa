import sys
import time
import json
import logging
import argparse
import pprint
import threading
import uuid
import requests


class Logger(object):
    """
        Description :  Class that creates an log instance
    """

    # Initialize logging object
    def __init__(self, module_name, log_level="DEBUG"):
        logging.basicConfig(level=log_level)
        self.logman = logging.getLogger(module_name)

    # Function to pass info level messages to logging
    def info(self, message):
        self.logman.info(message)

    # Function to pass debug level messages to logging
    def debug(self, message):
        self.logman.debug(message)

    # Function to pass warn level messages to logging
    def warn(self, message):
        self.logman.warn(message)

    # Function to pass error level messages to logging
    def error(self, message):
        self.logman.error(message)

    # Function to pass critical level messages to logging
    def critical(self, message):
        self.logman.critical(message)


def exceptions_handler(fun):
    """
        Description : method decorator to bind exceptions handling to a method
        return : return same output of the decorated function
    """

    def exceptions_wrapper(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception as exception_var:
            ex_type, exception_info, trace_back = sys.exc_info()
            template = "'{0} ' occurred. \n{1!r}"
            message = template.format(ex_type, exception_var.args)
            print (message)
        return fun(*args, **kwargs)

    return exceptions_wrapper


class HTTPClient(object):
    """
        Description : HTTP Client to handle http request and responses
        return : statusCode, <json> response
    """

    # Initialize with the api's host name and timeout
    def __init__(self, api_host, timeout=5):
        self.api_host = "http://" + api_host
        self.timeout = timeout
        self.log = Logger(self.__class__.__name__)

    # executes http post call with the given data. data should be a json object
    @exceptions_handler
    def post(self, api, data=None):
        if data is None:
            req = requests.post(self.api_host + "/" + api, timeout=self.timeout)
        else:
            req = requests.post(self.api_host + "/" + api, data=json.dumps(data, ensure_ascii=False),
                                timeout=self.timeout)

        if req.status_code == 200:
            self.log.debug(
                "HTTP POST to : {}, response code : {} , \nresponse : {}".format(self.api_host + "/" + api,
                                                                                 req.status_code,
                                                                                 pprint.pformat(req.json())))
        else:
            self.log.warn("HTTP POST to : {} response code : {}, \n data : {} \n response : {}".format(
                self.api_host + "/" + api, req.status_code, pprint.pformat(data), pprint.pformat(req.json())))

        return {"response_code": req.status_code, "response": req.json()}

    # executes http get call with the given data. data should be a json object
    @exceptions_handler
    def get(self, api, data=None):
        if data is None:
            req = requests.get(self.api_host + "/" + api, timeout=self.timeout)
        else:
            req = requests.get(self.api_host + "/" + api, data=json.dumps(data, ensure_ascii=False),
                               timeout=self.timeout)
        if req.status_code == 200:
            self.log.debug("HTTP GET to : {},response code : {} , \nresponse : {}".format(self.api_host + "/" + api,
                                                                                          req.status_code,
                                                                                          pprint.pformat(
                                                                                              req.json())))
        else:
            self.log.warn(
                "HTTP GET to : {} response code : {}, \ndata : {} \nresponse : {}".format(self.api_host + "/" + api,
                                                                                          req.status_code,
                                                                                          pprint.pformat(data),
                                                                                          pprint.pformat(
                                                                                              req.json())))
        return {"response_code": req.status_code, "response": req.json()}

    # executes http put call with the given data. data should be a json object
    @exceptions_handler
    def put(self, api, data=None):
        if data is None:
            req = requests.put(self.api_host + "/" + api, timeout=self.timeout)
        else:
            req = requests.put(self.api_host + "/" + api, data=json.dumps(data, ensure_ascii=False),
                               timeout=self.timeout)
        if req.status_code == 200:
            self.log.debug(
                "HTTP PUT to : {}, response code : {} , \nresponse : {}".format(self.api_host + "/" + api,
                                                                                req.status_code,
                                                                                pprint.pformat(req.json())))
        else:
            self.log.warn(
                "HTTP PUT to : {} response code : {}, \ndata : {} \nresponse : {}".format(self.api_host + "/" + api,
                                                                                          req.status_code,
                                                                                          pprint.pformat(data),
                                                                                          pprint.pformat(
                                                                                              req.json())))
        return {"response_code": req.status_code, "response": req.json()}

    # executes http delete call with the given data. data should be a json object
    @exceptions_handler
    def delete(self, api, data=None):
        if data is None:
            req = requests.delete(self.api_host + "/" + api)
        else:
            req = requests.delete(self.api_host + "/" + api, data=json.dumps(data, ensure_ascii=False),
                                  timeout=self.timeout)
        if req.status_code == 200:
            self.log.debug(
                "HTTP DELETE to : {}, response code : {} ,\nresponse : {}".format(self.api_host + "/" + api,
                                                                                  req.status_code,
                                                                                  pprint.pformat(req.json())))
        else:
            self.log.warn("HTTP DELETE to : {} response code : {}, \ndata : {} \nresponse : {}".format(
                self.api_host + "/" + api, req.status_code, pprint.pformat(data), pprint.pformat(req.json())))
        return {"response_code": req.status_code, "response": req.json()}


class AvisaController(object):
    """
        Description : A class that abstracts AVISA test schedule steps
    """

    def __init__(self, group_name, test_platforms, test_model, test_os_version, api_host="10.22.237.210:8080"):
        self.group_name = group_name
        self.tst_lst = []
        self.reservation = None
        self.reservation_id = None
        self.reservation_payload = {
            "deployment_id": None,
            "group_name": None,
            "devices": []
        }
        self._pp_config = {
            "ANDROID": "http://10.22.236.231/playerqa/configuration/android/demoConf.json",
            "IOS": "http://10.22.236.231/playerqa/configuration/ios/demoConf.json",
            "OSX": "http://10.22.236.231/playerqa/configuration/js/demoConf.json",
            "WIN": "http://10.22.236.231/playerqa/configuration/js/demoConf.json"
        }

        self.test_payload = {
            "deployment_id": None,
            "tests": []
        }
        self.test_model = test_model
        self.test_os_version = test_os_version
        self._hostip = api_host
        self.test_platforms = test_platforms.upper()
        self.log = Logger(self.__class__.__name__)
        self.http_client = HTTPClient(self._hostip)  # use default timeout as 5 sec

        # Generate an Unique UUID for Reservation
        self.reservation_id = self.get_reservation_id()

    # Function generates a unique reservation id for avisa reservation
    @exceptions_handler
    def get_reservation_id(self):
        return str(uuid.uuid4().hex)

    # Function generates the reservation payload based on the test platforms argument passed by the user
    @exceptions_handler
    def add_test_platforms(self):
        if self.test_platforms is None:
            self.reservation_payload["devices"].append({"make": "APPLE",
                                                        "model": self.test_model,
                                                        "os_version": self.test_os_version,
                                                        "pp_version": "*",
                                                        "os": "OSX",
                                                        "total_devices": 1})
        else:
            if 'IOS' in self.test_platforms:
                self.reservation_payload["devices"].append({"make": "APPLE",
                                                            "model": self.test_model,
                                                            "os_version": self.test_os_version,
                                                            "pp_version": "*",
                                                            "os": "IOS",
                                                            "total_devices": 1})

            if 'ANDROID' in self.test_platforms:
                self.reservation_payload["devices"].append({"make": "GOOGLE",
                                                            "model": self.test_model,
                                                            "os_version": self.test_os_version,
                                                            "pp_version": "*",
                                                            "os": "ANDROID",
                                                            "total_devices": 1})

            if 'JS' in self.test_platforms:
                self.reservation_payload["devices"].append({"make": "APPLE",
                                                            "model": self.test_model,
                                                            "os_version": self.test_os_version,
                                                            "pp_version": "*",
                                                            "os": "OSX",
                                                            "total_devices": 1})

    # Reserve Device in AVISA LAB for playback testing. Devices reserved based on user arguments.
    @exceptions_handler
    def reserve(self):
        self.reservation_payload["group_name"] = self.group_name
        self.reservation_payload["deployment_id"] = self.reservation_id
        self.add_test_platforms()
        self.log.info(pprint.pformat(self.reservation_payload))

        # Request AVISA for reservation
        http_response = self.http_client.post("api/reservations/", self.reservation_payload)
        if http_response['response_code'] != 200:
            self.log.error("Reservation not successful")
            self.reservation = None
        else:
            # Notify Reservation
            self.reservation = http_response['response']["reservations"]

    # Test Generator, Generates test based on Test Template.
    @exceptions_handler
    def generate_tests(self, asset_url, test_duration):
        self.test_payload["deployment_id"] = str(self.reservation_id)
        # Add test for each device type
        print (len(self.reservation))
        for device in self.reservation:
            device_id = device["device_id"]
            # Get Device Platform  OS name
            http_responses = self.http_client.get("api/devices/{}".format(device_id))
            tst = {
                "name": "AVISA-CLI-PLAYBACK-TEST",
                "device": str(device_id),
                "steps": [
                    {
                        "step": 1,
                        "name": "loadconfig",
                        "data": self._pp_config[http_responses['response']["device"]["os"]],
                        "duration": 10
                    },
                    {
                        "step": 2,
                        "name": "provision",
                        "data": "viperplayerqa,Dreamer777",
                        "duration": 10
                    },
                    {
                        "step": 3,
                        "name": "setasset",
                        "data": asset_url,
                        "duration": test_duration
                    },
                    {
                        "step": 5,
                        "name": "stop",
                        "data": "",
                        "duration": 10
                    }
                ]
            }
            self.test_payload["tests"].append(tst)
        return self.test_payload

    # Call Test Generator method and post the test to AVISA-C
    def submit_tests(self, asset, test_duration):
        test_list = []
        tst_payload = self.generate_tests(asset, test_duration)
        http_response = self.http_client.post("api/tests/", data=tst_payload)
        if http_response["response_code"] == 200:
            print ("appending results")
            for test in http_response["response"]["tests"]:
                test_list.append({"test_id": test["test_id"], "device_id": test["device_id"],
                                  "deployment_id": test["deployment_id"]})
        return test_list

    # Get Test Status based on Test_ID from AVISA-C
    def get_test_status(self, test_id):
        http_response = self.http_client.get("api/tests/status/{}".format(test_id))
        return http_response['response']["status"]

    # Clears all reservations and makes the devices available
    def clear_reservation(self):
        self.http_client.delete("api/reservations/{}".format(self.reservation_id))
        self.log.info("Reservations cleared : \n{}".format(self.reservation_payload))

    # Monitors the test(s) for status change and exits test(s) if duration exceeds playback time+10minutes
    def monitor_test(self, test_id, device_id, test_duration):
        test_duration = int(test_duration)
        start_time = time.time()
        while True:
            # check test_status
            test_status = self.get_test_status(test_id)
            if test_status == 1:
                self.log.info("Device : {}, Test : {} - NOT STARTED".format(device_id, test_id))
            elif test_status == 2:
                self.log.info(("Device : {}, Test : {} - IN PROGRESS".format(device_id, test_id)))
            elif test_status == 3:
                self.log.info(
                    "Device : {}, Test : {} - COMPLETED , Test Results @ http://{}/ui/results/{}".format(device_id,
                                                                                                         test_id,
                                                                                                         self._hostip,
                                                                                                         test_id))
                break  # break loop , exit while
            else:
                self.log.warn(
                    "Device : {}, Test : {} - COMPLETED with Status : {}".format(device_id, test_id, test_status))
                break  # break loop , exit while
            time.sleep(3)  # Poll AVIS-C every 3 seconds
            # Assumption : The Wrapper build, launch , load config, stop and Wrapper tear down together does not take
            # more than 10 minutes (600 seconds)
            if time.time() - start_time > (test_duration + 600):
                self.log.warn(
                    "Device : {} , Test_ID : {}, Exceed the standard Test Duration. Stopping test".format(device_id,
                                                                                                          test_id))
                self.log.error(
                    "Device : {} , Test_ID : {}, Exiting Playback Test Monitoring ".format(device_id, test_id))
                break

    # Execute the 4 steps of avisa test scheduling in order
    def test(self, asset_url, test_duration):
        # Reserve Resources for AVISA Playback Testing.
        self.reserve()
        # Generate and submit tests to AVISA System
        test_list = self.submit_tests(asset_url, test_duration)
        if test_list:
            for test in test_list:
                threading.Thread(name="TestID{}".format(test["test_id"]), target=self.monitor_test,
                                 args=(test["test_id"], test["device_id"], test_duration)).start()
        else:
            self.log.error("Tests not submitted")

        # Clear Reservations
        self.clear_reservation()
        if test_list:
            for test in test_list:
                self.log.info("Device : {}, Test : {} - COMPLETED , Test Results @ http://{}/ui/results/{}".format(
                    test["device_id"], test["test_id"], self._hostip, test["test_id"]))


# Initialize argument parser
def arg_parser_init():
    """
        Description : Function Initiates the CLI argument verbose and variables.
        Returns     : argparse.parse_args object
    """
    parser = argparse.ArgumentParser(
        description='Utility to use AVISA system from command line for basic playback testing')
    parser.add_argument('-g', dest='group_name',
                        help='Group name. If you do not know your group name, contact "Scott_Baldwin@comcast.com"')
    parser.add_argument('-a', dest='asset_url', help='A single HLS asset URL to test playback')
    parser.add_argument('-al', dest='asset_list_file', help='A file with a list of URLS to be tested')
    parser.add_argument('-d', dest='playback_duration', help='duration for asset playback in the test')
    parser.add_argument('-t', dest='test_platforms', help='platform type(s) to test the asset URL (ios,android,js)')
    parser.add_argument('-m', dest='test_model', default='*', help='device model, defaults to any')
    parser.add_argument('-o', dest='test_os_version', default='*', help='device os version, defaults to any')
    return parser.parse_args()


if __name__ == '__main__':
    # CLI Version
    _VERSION_ = "0.0.2"

    # Parse CLI arguments
    # -----------------------------------------------------------------------------------------
    parsed_args = arg_parser_init()

    # Get the Test Platforms
    USER_GRP_NAME = parsed_args.group_name
    TEST_DEVICES = parsed_args.test_platforms
    TEST_ASSET = parsed_args.asset_url
    TEST_DURATION = parsed_args.playback_duration
    TEST_MODEL = parsed_args.test_model
    TEST_OS_VERSION = parsed_args.test_os_version

    # Initialize AvisaController
    avisa = AvisaController(parsed_args.group_name,
                            parsed_args.test_platforms,
                            parsed_args.test_model,
                            parsed_args.test_os_version)

    # Start a Playback test using AVISA
    avisa.test(parsed_args.asset_url, parsed_args.playback_duration)
