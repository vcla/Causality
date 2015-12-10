python summerdata.py -s water_12_phone_21_screen_59_9404 is also a good multiple fluents: thirst, cup, screen ... where there are ONLY detected actions!

python summerdata.py -s door_12_light_2_9406 is also a good multiple fluents: screen, door, light. actions: throwtrash, pressbutton
{147: {'screen': 4.511042523263396},
 175: {'door': 0.01375618393307834, 'screen': 0.12073814770214907},
 191: {'door': 1.381971717221202},
 197: {'door': 4.511042523263396},
 227: {'light': 4.111633152359644},
 231: {'light': 1.1412953889718431},
 268: {'door': 0.011047802855318829},
 272: {'door': 0.011047802855318829},
 274: {'door': 2.4837952676020367}}
{200: {'throwtrash_START': {'agent': 'uuid1', 'energy': 1.474476}},
 201: {'throwtrash_END': {'agent': 'uuid1', 'energy': 1.474476}},
 206: {'pressbutton_START': {'agent': 'uuid1', 'energy': 0.003846}},
 262: {'pressbutton_END': {'agent': 'uuid1', 'energy': 0.003846}}}

FLUENT AND EVENT KEYS WE CARE ABOUT: {'events': set(['standing_END', 'standing_START', 'pressbutton_START']), 'fluents': set(['light_off', 'light_on', 'door_off', 'door_on'])}
T


python summerdata.py -s light_8_screen_50

python base_unittests.py LightingTestCaseSecondOfTwoFluents
