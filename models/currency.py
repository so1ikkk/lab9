class Currency:
    def __init__(self, num_code, char_code, name, value, nominal):
        self.num_code = num_code
        self.char_code = char_code.upper()
        self.name = name
        self.value = value
        self.nominal = nominal
