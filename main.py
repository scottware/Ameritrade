import tda

class Main:

    def __init__(self):
        self.tda = tda.TDA()


    def inner_loop(self, symbol = 'AMZN'):
        print("-------------")
        print("0. Exit")
        print("1. Get Quote")
        print("2. Recommend")
        print("3. Positions")
        print("4. Roll")
        print("5. Buy")
        print("-------------")
        task = input()
        command_list = ['0', '1', '2', '3', '4','5']
        if(task in command_list):
            if (task == "0"):
                sys.exit("exiting")
            if (task == "3"):
                self.tda.get_positions()
            if (task == "5"):
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
        self.inner_loop(symbol)


if __name__ == '__main__':
    main = Main()
    main.inner_loop()