# avisa-demo

The primary script contained here (avisa-demo.py), provides basic AVISA playback functionality.

Currently, only android devices are supported.

# Usage 

You will have to coordinate with the AVISA team to procure an android device for your use. 

Once you have an android device checked out to you, you can use this utility as follows. 

```
StrongBad@Lappy486:~/avisa-demo> python3 avisa-demo.py --device_id=<your_device_id> --duration=360 --url=<your.m3u8>
```

The script supports are --verbose, --debug, and --help (amoung other) options.

# Python 3

This script was written and tested with the 3.6 version of the Python language.

Other versions may work, but none are guaranteed.

# As a Test!

The most meaningful data coming from the AVISA system at this time, vis-a-vis testing whether a stream is working or not,
is are the audio_loudness' and 'video_motion' keys from the 'audio' and 'video' results, respectively (see below). 

As the test is running, it will record any occurrances where these values are 0, which indicates a "frozen" state. The 
number of these incidents is reported in the scripts final report. If a certain threshold of these events is reached,
the script will terminate itself, (prematurely) regardless of the duration specified for the run. 

Use the --failure_threshold option to tune for your tolerances.

# Example Output

```

StrongBad@Lappy486:~/avisa-demo>  python3 avisa-demo.py --device_id=<redacted> --duration=60 --url=<redacted.m3u8>
reservation - deployment_id: b9f4d665-e4df-4c6e-8eb3-a2b6edea1061 | device_id: 75
initiating test - test_id: 1756
self.test_status: 1 (New / Not Started)
self.test_status: 1 (New / Not Started)
self.test_status: 1 (New / Not Started)
self.test_status: 1 (New / Not Started)
self.test_status: 2 (Started / In Progress)
{'audio': [], 'video': []}
self.test_status: 2 (Started / In Progress)
{'audio': [], 'video': []}
self.test_status: 2 (Started / In Progress)
{   'audio': [   {   'audio_loudness': 44,
                     'audio_rms': 188,
                     'date_time': '2017-12-15T18:49:31.296Z',
                     'playbacktime': 3,
                     'state': 'PLAYING'}],
    'video': []}
self.test_status: 2 (Started / In Progress)
{   'audio': [   {   'audio_loudness': 46,
                     'audio_rms': 229,
                     'date_time': '2017-12-15T18:49:47.004Z',
                     'playbacktime': 19,
                     'state': 'PLAYING'}],
    'video': [   {   'camera_fps': 13,
                     'date_time': '2017-12-15T18:49:43.089Z',
                     'playbacktime': 15,
                     'qr': '{}',
                     'state': 'PLAYING',
                     'video_laplace': 5,
                     'video_motion': 725}]}
self.test_status: 2 (Started / In Progress)
{   'audio': [   {   'audio_loudness': 46,
                     'audio_rms': 210,
                     'date_time': '2017-12-15T18:50:02.701Z',
                     'playbacktime': 35,
                     'state': 'PLAYING'}],
    'video': [   {   'camera_fps': 14,
                     'date_time': '2017-12-15T18:49:58.807Z',
                     'playbacktime': 31,
                     'qr': '{}',
                     'state': 'PLAYING',
                     'video_laplace': 5,
                     'video_motion': 158}]}
self.test_status: 2 (Started / In Progress)
{   'audio': [   {   'audio_loudness': 43,
                     'audio_rms': 158,
                     'date_time': '2017-12-15T18:50:17.325Z',
                     'playbacktime': 50,
                     'state': 'PLAYING'}],
    'video': [   {   'camera_fps': 10,
                     'date_time': '2017-12-15T18:50:14.545Z',
                     'playbacktime': 47,
                     'qr': '{}',
                     'state': 'PLAYING',
                     'video_laplace': 6,
                     'video_motion': 213}]}
self.test_status: 2 (Started / In Progress)
{   'audio': [   {   'audio_loudness': 45,
                     'audio_rms': 191,
                     'date_time': '2017-12-15T18:50:32.037Z',
                     'playbacktime': 65,
                     'state': 'PLAYING'}],
    'video': [   {   'camera_fps': 10,
                     'date_time': '2017-12-15T18:50:29.007Z',
                     'playbacktime': 62,
                     'qr': '{}',
                     'state': 'PLAYING',
                     'video_laplace': 7,
                     'video_motion': 548}]}
self.test_status: 3 (Completed)
self.test_results: {   'audio': {'count': 0, 'results': []},
    'deployment_id': 'b9f4d665-e4df-4c6e-8eb3-a2b6edea1061',
    'device_group': 'JOHNE',
    'device_hub': 'HUB_MAC_AIR_05',
    'device_id': 75,
    'device_make': 'SAMSUNG',
    'device_model': 'GalaxyNote5_01',
    'device_os': 'ANDROID',
    'device_os_version': '6.0.1',
    'test_id': 1756,
    'test_status': 3,
    'video': {'count': 0, 'results': []}}
results: {   'audio': {'count': 0, 'results': []},
    'deployment_id': 'b9f4d665-e4df-4c6e-8eb3-a2b6edea1061',
    'device_group': 'JOHNE',
    'device_hub': 'HUB_MAC_AIR_05',
    'device_id': 75,
    'device_make': 'SAMSUNG',
    'device_model': 'GalaxyNote5_01',
    'device_os': 'ANDROID',
    'device_os_version': '6.0.1',
    'test_id': 1756,
    'test_status': 3,
    'video': {'count': 0, 'results': []}}
releasing device


``` 

