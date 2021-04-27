commands = \
    {
        'Preamplifier power':
            {
                'Command num': {'0x04': 4},
                'Power': {'Off': 0, 'On': 1, 'Block': 2},
            },

        'Set preselector band':
            {
                'Command num': {'0x05': 5},
                'Low':
                    {
                        'BF0 30-60MHz': 0x00,
                        'BF1 60-90MHz': 0x01,
                        'BF2 90-130MHz': 0x02,
                        'BF3 130-210MHz': 0x03,
                        'BF4 210-320MHz': 0x04,
                        'BF5 320-480MHz': 0x05,
                        'BF6 480-860MHz': 0x06,
                        'BF7 860-1600MHz': 0x07,
                        'BF8 1600-2900MHz': 0x08,
                        'BF9 2900-4060MHz': 0x09,
                        'BF10 4060-5000MHz': 0x0A,
                        'BF11 5000-6000MHz': 0x0B,
                        'BF12 WI-FI 2.4MHz': 0x0C,
                     }
            },
        'Preamplifier channel power':
            {
                'Command num': {'0x0E': 0x0E},
                'Power':
                    {
                        'Turn off both channels': 0,
                        'Turn on 1 channel': 1,
                        'Turn on 2 channel': 2,
                        'Turn on both channels': 3
                    }
            },
        'Питание 12В для оптического передатчика или питание 5В для дополнительного РЧ-усилителя':
            {
                'Номер команды': {'0x10': 0x10},
                'Питание':
                    {
                        'Выкл': 0,
                        'ВКЛ': 1,
                    }
            },
        'TEST':
            {
                'Номер команды': {'0x10': 0x10},
                'Питание':
                    {
                        'Выкл': 0,
                        'ВКЛ': 1,
                    },
                'test byte': 20,
            },
    }