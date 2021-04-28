import json
import Preselector_commands

commands = \
    {
        'Channel 1 power':
            {
                'Comand num':
                    {
                        'type': 'const_num',
                        'def_value': 0x9E,
                    },
                'Power':
                    {
                        'type': 'enum',
                        'values': {'Off': 0, 'On': 1}
                    },
                'Freq':
                    {
                        'type': 'num',
                        'def_value': 100,
                        'min': 30,
                        'max': 6000,
                        'step': 10,
                    },

            },

    }

with open('data1.json', 'w') as fp:
    json.dump(commands, fp, sort_keys=False, indent=4)
