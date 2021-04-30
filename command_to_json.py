import json

commands = \
    {
        'Channel 1 power': {
            'Command num':
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

        'Preselector power channels': {
            'Command num':
                {
                    'type': 'const_num',
                    'def_value': 0x0E,
                },
            'Power':
                {
                    'type': 'enum',
                    'values': {'Turn off both channels': 0, 'Turn on 1': 1, 'Turn on 2': 2, 'Turn on both channels': 3}
                },
        },

    }

with open('data1.json', 'w') as fp:
    json.dump(commands, fp, sort_keys=False, indent=4)
