#!/usr/bin/env  python


""" This is basically scratchpad code for playing with the AVISA system. """

import argparse
import json
import pprint
import time
import uuid
import requests

AVISA = 'http://10.22.237.210:8080'

AVISA_STATUSES = {1: "New / Not Started",
                  2: "Started / In Progress",
                  3: "Completed",
                  -1: "Error",
                  0: "Stop test",
                  4: "No Tests"}

DEBUG = False
VERBOSE = False
QUIET = True

FAILSAFE_TIMEOUTS = {1: 15 * 60,  # 15m - to start the test
                     2: 60 * 60}  # 60m - to run the test

FAILURE_THRESHOLD = 0

PP = pprint.PrettyPrinter(indent=4, width=120)

#TODO: Need a logger. :)


class TestManager(object):

    def __init__(self, playback_url, duration=120, device_type=None, device_id=None, deployment_id=None):

        self.deployment_id = deployment_id
        self.device_id = device_id
        self.device_type = device_type
        self.duration = duration
        self.playback_url = playback_url
        self.test_case_payload_file = 'android-demo.json'
        self.test_id = None
        self.test_results = None
        self.test_status = None

        if not device_type and not device_id:
            raise Exception("TestManager requires either a device_type or device_id be specified.")

    def __enter__(self):

        self.reserve()

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.release()

    def _call_avisa(self, url, payload, method, debug=DEBUG):

        r = None
        status_code = None
        response = None

        if debug:
            print("=== AVISA CALL START ===")
            print("URL: {}".format(url))
            print("PAYLOAD: \n{}".format(PP.pformat(payload)))

        if method is 'post':
            r = requests.post(url, json=payload)
        elif method is 'put':
            r = requests.put(url, json=payload)
        elif method is 'get':
            r = requests.get(url, json=payload)
        elif method is 'delete':
            r = requests.delete(url, json=payload)

        status_code = r.status_code

        if debug:
            print("RESPONSE: {}".format(PP.pformat(r.content.decode())))
            print("STATUS: {}".format(r.status_code))

        if status_code != 200:
            raise Exception("AVISA CALL FAILED!\nMESSAGE:{}\nSTATUS: {}".format(status_code, r.content.decode()))
        else:
            response = json.loads(r.content.decode())

        if debug:
            print("=== AVISA CALL END ===")

        return status_code, response

    def run(self):

        with open(self.test_case_payload_file) as f:
            test_payload = json.load(f)

        test_payload["deployment_id"] = self.deployment_id
        test_payload["tests"][0]["steps"][2]["duration"] = self.duration
        test_payload["tests"][0]["steps"][2]["data"] = self.playback_url

        test_url = '{}/api/tests/'.format(AVISA)

        _, content = self._call_avisa(test_url, test_payload, 'post', debug=VERBOSE)

        self.test_id = content['tests'][0]['test_id']

        if not QUIET:
            print("initiating test - test_id: {}".format(self.test_id))

    def reserve(self):

        if self.deployment_id is None:
            self.deployment_id = str(uuid.uuid4())

        if self.device_id:
            reserve_url = "{}/api/reservations/device/".format(AVISA)
            reserve_payload = {"deployment_id": self.deployment_id, "device_id": self.device_id}

        if self.device_type:
            raise Exception("Running tests by device type is not yet implemented.")

        self._call_avisa(reserve_url, reserve_payload, 'post', debug=VERBOSE)


        if not QUIET:
            print("reservation - deployment_id: {} | device_id: {}".format(self.deployment_id, self.device_id))

    def release(self):

        release_url = "{}/api/reservations/{}".format(AVISA, self.deployment_id)
        release_payload = {}

        if not QUIET:
            print("releasing device")

        self._call_avisa(release_url, release_payload, 'delete', debug=DEBUG)

    def status(self):

        status_url = "{}/api/tests/status//{}".format(AVISA, self.test_id)
        status_payload = {}

        _, response = self._call_avisa(status_url, status_payload, 'get', debug=DEBUG)

        self.test_status = response['status']

        if not QUIET:
            print("self.test_status: {} ({})".format(self.test_status, AVISA_STATUSES[self.test_status]))

        return self.test_status

    def summary_results(self):

        results_url = "{}/api/results/{}".format(AVISA, self.test_id)
        results_payload = {}

        _, response = self._call_avisa(results_url, results_payload, 'get', debug=DEBUG)

        self.test_results = response

        if not QUIET:
            print("self.test_results: {}".format(PP.pformat(self.test_results)))

        return self.test_results

    def detailed_results(self, rtype, count=None):

        results_url = "{}/api/results/{}/{}".format(AVISA, rtype, self.test_id)
        results_payload = {}

        if count is not None:
            results_url = "{}/api/results/{}/{}?count={}".format(AVISA, rtype, self.test_id, count)
            results_payload = {'count': count}

        _, response = self._call_avisa(results_url, results_payload, 'get', debug=DEBUG)

        return response

    def get_latest_results(self):

        results = self.detailed_results('video', count=1)
        results.update(self.detailed_results('audio', count=1))

        return results


def set_log_level(debug=DEBUG, verbose=VERBOSE, quiet=QUIET):

    global DEBUG
    global VERBOSE
    global QUIET

    if debug:
        verbose = True
        quiet = False

    elif verbose:
        debug = False
        quiet = False

    elif quiet:
        debug = False
        verbose = False

    DEBUG = debug
    VERBOSE = verbose
    QUIET = quiet


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run a basic playback test with AVISA.')

    parser.add_argument('--url', type=str, default='http://10.22.244.94/BBC_WORLD_HD_TVE.m3u8', action='store',
                        help='The .m3u8 stream url from which to test playback.')
    parser.add_argument('--device_id', type=int, default=None, action='store',
                        help='The specific device_id of the device with which you want to test playback.')
    parser.add_argument('--duration', type=int, default=120, action='store',
                        help='The number of seconds to run the playback test.')
    parser.add_argument('--failure_threshold', type=int, default=FAILURE_THRESHOLD, action='store',
                        help='The number of failures to tolerate before declaring failure and ending the playback.')
    parser.add_argument('--device_type', type=str, default=None, action='store',
                        help='The type of device with which you want to test playback. (Not Implemented)')
    parser.add_argument('--deployment_id', type=str, default=None, action='store',
                        help='The name of this test, as it will be registered in AVISA.')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--quiet', action='store_true')


    args = parser.parse_args()

    set_log_level(args.debug, args.verbose, args.quiet)

    tm = TestManager(playback_url=args.url,
                     deployment_id=args.deployment_id,
                     duration=args.duration,
                     device_type=args.device_type,
                     device_id=args.device_id)

    failures = {'audio': {}, 'video': {}}

    with tm:

        tm.run()

        total_failures = 0

        while tm.status() in [1, 2]:

            if tm.test_status is 2:

                latest_results = tm.get_latest_results()
                print(PP.pformat(latest_results))

                if 'audio' in latest_results.keys() and latest_results['audio']:
                    if latest_results['audio'][0]['audio_loudness'] == 0:
                        print("audio freeze failure detected")
                        failures['audio'].update({time.time(): "Audio Loudness: 0 - Frozen"})

                if 'video' in latest_results.keys() and latest_results['video']:
                    if latest_results['video'][0]['video_motion'] == 0:
                        print("video freeze failure detected")
                        failures['video'].update({time.time(): "Video Motion: 0 - Frozen"})

            total_failures = len(failures['audio'].keys()) + len(failures['video'].keys())

            if total_failures > args.failure_threshold:
                print('Exiting - Too many failures encountered.')
                print("failures:\n{}".format(PP.pformat(failures)))
                print("total failures: {}".format(total_failures))
                exit(1)

            time.sleep(5)

        print("results: {}".format(PP.pformat(tm.summary_results())))
        print("failures:\n{}".format(PP.pformat(failures)))
        print("total failures: {}".format(total_failures))
        exit(0)
