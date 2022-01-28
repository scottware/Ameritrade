import requests
import json
import urllib
import pandas as pd
import numpy as np
import sys
from colorama import init, Fore, Back, Style

credentials = {}
pd.set_option('display.max_rows', None, )
pd.set_option('display.max_columns', None, )
pd.set_option('display.width', 1000)

class TDA:
    def __init__(self, config):
        self.config = config
        init(autoreset=True)

    def load_credentials(self, error_message=None):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        save = False
        global credentials

        if (not ('access_token' in credentials)
                or not ('refresh_token' in credentials)
                or not ('td_consumer_key' in credentials)):
            f = open('credentials.json')
            credentials = json.load(f)

        if (not ('td_consumer_key' in credentials) or
                (credentials['td_consumer_key'] == None or credentials['td_consumer_key'] == '')):
            credentials['td_consumer_key'] = ''
            save = True
        if (not ('access_token' in credentials)):
            credentials['access_token'] = ''
            save = True

        # if(not( 'access_token' in credentials )
        #         or credentials['access_token'] == None
        #         or credentials['access_token'] == '' ):
        if (error_message == 'No AuthToken is present.'):
            auth_url = 'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={callback_url}&client_id={consumer_key}@AMER.OAUTHAP'
            callback_url = 'http://localhost:8080'
            endpoint = auth_url.format(callback_url=callback_url, consumer_key=credentials['td_consumer_key'])
            print(endpoint)
            q = input()
            print(q)

            qs = urllib.parse.parse_qs(q)
            url = next(iter(qs))
            decoded_access = qs[url][0]

            grant_type = 'authorization_code'
            access_type = 'offline'
            code = decoded_access
            redirect_uri = 'http://localhost:8080'

            endpoint = 'https://api.tdameritrade.com/v1/oauth2/token'

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = {'grant_type': grant_type, 'access_type': access_type,
                      'code': code, 'redirect_uri': redirect_uri, 'client_id': credentials['td_consumer_key'],
                      'refresh_token': ''}

            page = requests.post(endpoint, headers=headers, data=params)

            content = json.loads(page.content)
            credentials['access_token'] = content['access_token']
            credentials['refresh_token'] = content['refresh_token']
            save = True

        if (error_message == 'Not Authorized.'):
            ##refresh

            grant_type = 'refresh_token'
            access_type = 'offline'
            refresh_token = credentials['refresh_token']

            endpoint = 'https://api.tdameritrade.com/v1/oauth2/token'

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            params = {'grant_type': grant_type, 'access_type': access_type,
                      'refresh_token': refresh_token, 'client_id': credentials['td_consumer_key']}
            page = requests.post(endpoint, headers=headers, data=params)

            content = json.loads(page.content)
            credentials['access_token'] = content['access_token']
            credentials['refresh_token'] = content['refresh_token']
            save = True

        ####    'Not Authorized.'
        if (save):
            credential_prep = json.dumps(credentials)
            f = open("credentials.json", "w")
            f.write(credential_prep)
            f.close()


    def get_quote(self, symbol):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        symbol = symbol.upper()
        self.load_credentials()
        global credentials
        endpoint = 'https://api.tdameritrade.com/v1/marketdata/{stock_ticker}/quotes?'
        headers = {"Authorization": "Bearer " + credentials['access_token']}

        full_url = endpoint.format(stock_ticker=symbol)
        page = requests.get(url=full_url,
                            params={'apikey': credentials['td_consumer_key']},
                            headers=headers)

        content = json.loads(page.content)
        if 'error' in content:
            print(content)
            print(full_url)
            print(headers)
            self.load_credentials(content['error'])
            return self.get_quote(symbol)
        else:
            # lastPrice = content[symbol]['lastPrice']
            # bidPrice = content[symbol]['bidPrice']
            # askPrice = content[symbol]['askPrice']
            # closePrice = content[symbol]['closePrice']
            # netChange = content[symbol]['netChange']
            #
            # print(f'Bid Price {bidPrice}')
            # print(f'Ask Price {askPrice}')
            # print(f'Last Price {lastPrice}')
            # print(f'Close Price {closePrice}')
            # print(f'Change {netChange}')
            return content[symbol]

    def print_quote(self, quote):
        color = Fore.RED
        if quote["netChange"] > 0:
            color = Fore.GREEN

        print(f'{quote["symbol"]}  {Style.BRIGHT} {quote["lastPrice"]} {color} {quote["netChange"]}{Fore.RESET}')

    def get_chain(self, symbol):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        base_url = 'https://api.tdameritrade.com/v1/marketdata/chains?&symbol={stock_ticker}&contractType={contractType}'

        endpoint = base_url.format(stock_ticker=symbol, contractType='PUT')

        page = requests.get(url=endpoint,
                            params={'apikey': credentials['td_consumer_key']})

        content = json.loads(page.content)

        df = pd.DataFrame(data=None, index=None,
                          columns=['Description', 'Symbol', 'Strike', 'Bid', 'Mark', 'Ask', 'Bid Value', 'Daily Value'])

        for date in content['putExpDateMap'].keys():
            for strike in content['putExpDateMap'][date].keys():
                detail = content['putExpDateMap'][date][strike][0]
                option_symbol = detail['symbol']
                description = detail['description']
                bid = detail['bid']
                ask = detail['ask']
                mark = detail['mark']
                strike = detail['strikePrice']
                daysToExpiration = detail['daysToExpiration']
                dailyValue = mark / daysToExpiration if daysToExpiration != 0 else 0
                bidValue = bid / daysToExpiration if daysToExpiration != 0 else 0
                # dailyValue = abs(dailyValue-1.0)

                #if (daysToExpiration == 0):
                #    pass
                #else:

                new_data = [daysToExpiration,option_symbol,description,strike,bid,mark,ask,
                            dailyValue,bidValue]
                new_data_cols = ['Days', 'Symbol', 'Description', 'Strike', 'Bid', 'Mark', 'Ask',
                                 'Daily Value', 'Bid Value']
                new_row = pd.DataFrame([new_data], columns=new_data_cols)
                df = pd.concat([df,new_row], ignore_index=True)
        return df


    def is_cheap(self, symbol):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        symbol = symbol.upper()
        quote = self.get_quote(symbol)
        self.print_quote(quote)

        lastPrice = quote['lastPrice']
        bidPrice = quote['bidPrice']
        askPrice = quote['askPrice']
        closePrice = quote['closePrice']
        netChange = quote['netChange']

        pd.set_option('display.max_rows', None, )
        pd.set_option('display.max_columns', None, )
        pd.set_option('display.width', 1000)

        df = self.get_chain(symbol)
        print(f'Closing Price {closePrice}')

        # df.query('Strike <= closePrice')
        is_cheap = df[(df['Strike'] <= lastPrice) &
                      (df['Daily Value'] >= (lastPrice * 0.00057143)) &  ## 0.8
                      (df['Daily Value'] < (lastPrice * 0.00085714))]  ## 1.2

        is_cheap = is_cheap.sort_values(by=['Strike'])

        # print(is_cheap)
        print(is_cheap.head(25))


    def get_account(self):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        self.load_credentials()
        global credentials
        endpoint = 'https://api.tdameritrade.com/v1/accounts/{account_id}?'
        account_id = '872016966'
        headers = {"Authorization": "Bearer " + credentials['access_token']}

        full_url = endpoint.format(account_id=account_id)
        page = requests.get(url=full_url,
                            params={'fields': "positions,orders"},
                            headers=headers)

        content = json.loads(page.content)
        return content


    def get_positions(self):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        content = self.get_account()
        positions = content['securitiesAccount']['positions']

        return positions


    def roll_options(self):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        positions = self.get_positions()
        options = filter(lambda positions: len(positions['instrument']['symbol']) > 5, positions)
        filtered=[]
        for x in options:
            filtered.append(x['instrument']['symbol'])
        filtered.sort()

        print("-------------")
        print(f'0. Exit')
        for x in filtered:
            index = filtered.index(x) + 1
            (symbol, o) = x.split("_")
            (date, strike) = o.split("P")

            print(f'{index}. {date} ${strike}')
        print("-------------")

        num = input()
        n=0
        try:
            n=int(num)
        except ValueError:
            print(f'invalid number {num}')
            self.roll_options()

        if n == 0:
            return
        elif n > len(filtered):
            print(f'invalid number {n}')
            self.roll_options()
        else:
            choice = filtered[n-1]
            (symbol, x) = choice.split("_")
            range = 0.015

            quote = self.get_quote(symbol)
            self.print_quote(quote)

            df = self.get_chain(symbol.upper())
            mine = df[(df['Symbol'] == choice)]

            # my_bid = df
            print(mine)
            print("----------------------------------------------------------------------------------------------------------------------")
            mark = mine['Mark'].values[0]
            low = mark * (1 - range)
            high = mark * (1 + range)
            days = mine['Days'].values[0]
            choices = df[
                (df['Mark'] * 1.0 < high) & (df['Mark'] * 1.0 > low) & (df['Days'] > days)]  # and date is later than Mine
            choices = choices.sort_values(by=['Days'])

            print(choices)
            self.roll_options()

    def roll_options_consolidate(self):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        positions = self.get_positions()
        options = filter(lambda positions: len(positions['instrument']['symbol']) > 5, positions)

        total_value = 0.0
        total_quantity = 0
        symbol = ''

        for x in options:
            symbol = x['instrument']['symbol']
            quantity = x['shortQuantity']
            quote = self.get_quote(symbol)
            total_quantity += int(quantity)
            total_value += float(quantity) * float(quote['mark'])

        (symbol, z) = symbol.split("_")

        print(f'total value: {total_value}')
        mark = round(total_value/total_quantity,2)
        print('AVG: ' + Style.BRIGHT  + Fore.BLUE + str(mark))

        range = 0.01
        low = mark * (1 - range)
        high = mark * (1 + range)
        # days = mine['Days'].values[0]

        quote = self.get_quote(symbol)
        self.print_quote(quote)
        df = self.get_chain(symbol.upper())
        days=0
        print("----------------------------------------------------------------------------------------------------------------------")
        choices = df[
            (df['Mark'] * 1.0 < high) & (df['Mark'] * 1.0 > low) & (df['Days'] > days)]  # and date is later than Mine
        choices = choices.sort_values(by=['Days'])

        print(choices)

    def buy(self):
        if self.config.debug == True:
            print("### " + sys._getframe().f_code.co_name)

        self.load_credentials()
        global credentials
        endpoint = 'https://api.tdameritrade.com/v1/accounts/{account_id}/orders'
        account_id = '872016966'
        headers = {"Authorization": "Bearer " + credentials['access_token'],"Content-Type":"application/json"}

        params = {'complexOrderStrategyType': 'NONE',
                    "orderType": "LIMIT",
                    "session": "NORMAL",
                    "price": "6.45",
                    "duration": "DAY",
                    "orderStrategyType": "SINGLE",
                    "orderLegCollection": [
                        { "instruction": "SELL_TO_OPEN",
                          "quantity": 1,
                          "instrument": {
                            "symbol": "AMZN_011422P3250",
                            "assetType": "OPTION"
                            }
                        }
                      ]
                    }

        full_url = endpoint.format(account_id=account_id)
        p = json.dumps(params)
        page = requests.post(full_url, headers=headers, data=p)

        if(page.content):
            content = json.loads(page.content)
            print(content)
            return content




if __name__ == '__main__':
    pass
