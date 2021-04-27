import json
import Preselector_commands


commands =\
    {
        'Channel 1 power':
            {
                'Comand num': {'5': 5},
                'Power': {'Off': 0, 'On': 1},
            },

        'Set filter':
            {
                'Comand num': {'4': 4},
                'Low': {'BF1 30-90MHz': 0x01, 'BF2 90-120MHz': 0x02, 'BF3 120-210MHz': 0x03},
                'Hight': {'BF1 30-90MHz': 0x01, 'BF2 90-120MHz': 0x02, 'BF3 120-210MHz': 0x03},
            }
    }

with open('data.json', 'w') as fp:
    json.dump(Preselector_commands.commands, fp, sort_keys=False, indent=4)