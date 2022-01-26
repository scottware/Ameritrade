import tda

class Congifuration:
    def __init__(self, value=False):
        self.debug = value

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug=value

class Main:

    def __init__(self):
        self.tda = tda.TDA(Congifuration())


    def inner_loop(self, symbol = 'AMZN'):
        print("-------------")
        print("0. Exit")
        print("1. Get Quote")
        print("2. Recommend")
        print("3. Positions")
        print("4. Roll")
        print("5. Roll - consolidate")
        print("6. Buy")
        print("-------------")
        task = input()
        command_list = ['0', '1', '2', '3', '4','5','6']
        if(task in command_list):
            if (task == "0"):
                sys.exit("exiting")
            if (task == "3"):
                positions = self.tda.get_positions()
                for position in positions:
                    instrument = position['instrument']
                    description = instrument['symbol']
                    print(f'{description} {position["shortQuantity"]}')

            if (task == "6"):
                self.tda.buy()

            s = None
            if(task in ['1','2']):
                print(f'which security? [{symbol}]')
                s = input()

            if(s != None and s != ''):
                symbol = s
            if(task == "1"):
                quote = self.tda.get_quote(symbol)
                print(f'{symbol} {quote["lastPrice"]}  {quote["netChange"]}')
            if(task == "2"):
                self.tda.is_cheap(symbol)
            if (task == "4"):
                # print(f'{symbol} option name')
                # s = input()
                self.tda.roll_options()
            if (task == "5"):
                # print(f'{symbol} option name')
                # s = input()
                self.tda.roll_options_consolidate()
        self.inner_loop(symbol)


if __name__ == '__main__':
    main = Main()
    main.inner_loop()