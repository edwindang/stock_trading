"""
Algorithmic Stock Trading
Edwin Dang

"""


def open_data(filename):
    # A function to open the data file
    infile = open(filename, 'r')
    str_list = infile.readlines()
    return str_list
    filename.close


def day_check(str_list, day): #returns pieces of information on any given day
    line = str_list[day]
    pieces = line.split(",")
    return pieces


def col_check(col, pieces):
    if col == "date":
        num = 0
        piece = str(pieces[num])
    elif col == "open":
        num = 1
        piece = float(pieces[num])
    elif col == "high":
        num = 2
        piece = float(pieces[num])
    elif col == "low":
        num = 3
        piece = float(pieces[num])
    elif col == "close":
        num = 4
        piece = float(pieces[num])
    elif col == "adj close":
        num = 5
        piece = float(pieces[num])
    else:
        num = 6
        piece = int(pieces[num])
    return piece


def test_data(filename, col, day):
    x = open_data(filename)
    y = day_check(x, day)
    z = col_check(col, y)
    return z


def transact(funds, stocks, qty, price, buy=False, sell=False):
    balance = float(funds)
    stock = int(stocks)
    quantity = int(qty)
    value = qty*price

    if buy == sell:
        print("Ambigious transaction! Can't determine whether to \
        buy or sell. No action performed.")
    elif sell is True and quantity > stock:
        print("Insufficient stock:", stocks, "stocks owned, \
        but selling", quantity, "!")
    elif buy is True and value > balance:
        print("Insufficient funds: purchase of", quantity, "at",
              price, "requires", value, "but you only have",
              balance, "available!")
    elif buy is True:
        new_balance = balance - value
        total_stocks = stocks + quantity
        return new_balance, total_stocks
    elif sell is True:
        new_balance = balance + value
        total_stocks = stocks - quantity
        return new_balance, total_stocks


def value(lines, i):  # Finds the opening value
    x = day_check(lines, i)
    open_value = float(x[1])  # call day_check here
    return open_value


def close_value(lines, i):  # Finds the closing value
    x = day_check(lines, i)
    close_value = float(x[4])
    return close_value


def twenty_day_SMA(recent_day, lines):
    i = recent_day
    summation = 0
    for i in range(i-20, i):
        open_value = value(lines, i)
        summation = summation + open_value
    average = summation/20
    summation = 0
    return average


def sell_tingz(stocks_owned, cash_balance, lines, i):  # Sells all shares once complete
    last_value = value(lines, i)
    return transact(cash_balance, stocks_owned, stocks_owned,
                    last_value, buy=False, sell=True)


def alg_moving_average(filename):  # This program trades based on an SMA indicator
    lines = open_data(filename)
    cash_balance = 1000
    stocks_owned = 0
    for i in range(21, len(lines)):
        open_value = value(lines, i)
        moving_avg = twenty_day_SMA(i, lines)
        if 0.95 * open_value <= moving_avg:
            if cash_balance < (open_value*10):
                continue
            elif cash_balance >= (open_value * 10):
                cash_balance, stocks_owned = transact(cash_balance,
                stocks_owned, 10, open_value, buy=True, sell=False)
                continue
        elif 1.05 * open_value >= moving_avg:
            if stocks_owned < 10:
                continue
            elif stocks_owned >= 10:
                cash_balance, stocks_owned = transact(cash_balance,
                stocks_owned, 10, open_value, buy=False, sell=True)
                continue
    cash_balance = float(cash_balance)
    stocks_owned = int(stocks_owned)
    cash_balance, stocks_owned = sell_tingz(stocks_owned, cash_balance,
                                            lines, (len(lines) - 1))
    return stocks_owned, cash_balance


# list of market differentials of 5 day intervals
five_day_differences = []


def recession(lines):  # This attempts to react to a potential recession of the market
    for i in range(15, len(lines)):
        five_day_difference = close_value(lines, i) - close_value(lines, i-5)
        five_day_differences.append(five_day_difference)
    for i in range(3):
        if five_day_differences[2] < five_day_differences[1] and five_day_differences[1] < five_day_differences[0]:
            return True
        else:
            return False


def rsi(recent_day, lines):  # 14 day period for RSI calculation
    avg_up = 0
    avg_down = 0
    up = 0
    down = 0
    i = recent_day
    for i in range(i-14, i):
        difference = close_value(lines, i) - close_value(lines, i-1)
        if difference >= 0:
            avg_up += difference
            up += 1
            
        else:
            avg_down += difference
            down += 1

    answer_1 = avg_up / up
    answer_2 = abs(avg_down / down)
    division = answer_1/answer_2
    rsi = 100 - (100/(1 + division))
    avg_up = 0
    avg_down = 0
    return rsi


def alg_mine(filename):  # This algorithm trades based on an RSI indicatior
    lines = open_data(filename)
    cash_balance = 1000
    stocks_owned = 0
    r = recession(lines)
    for i in range(16, len(lines)):
        RSI = rsi(i, lines)
        c_v = close_value(lines, i)  # Using close values for calculations and trades 
        if r is not True:
            if RSI <= 30:  # This condition is a buy signal
                if cash_balance < (c_v * 15):
                    continue
                elif cash_balance >= (c_v * 15):
                    cash_balance, stocks_owned = transact(cash_balance,
                    stocks_owned, 15, c_v, buy = True, sell = False)
                    continue
            elif RSI >= 70:  # This condition is a sell signal
                if stocks_owned > 15:
                    continue
                else:
                    cash_balance, stocks_owned = transact(cash_balance,
                    stocks_owned, 15, c_v, buy = False, sell = True)
            elif RSI < 70 and RSI > 30:  # No action in this condition
                continue
        else:  # Sells all stocks upon recession conditions
            last_value = five_day_differences[2]
            cash_balance, stocks_owned = transact(cash_balance, stocks_owned, stocks_owned, last_value)
            
    cash_balance = float(cash_balance)
    stocks_owned = int(stocks_owned)
    cash_balance, stocks_owned = sell_tingz(stocks_owned, cash_balance,
                                            lines, (len(lines) - 1))
    return stocks_owned, cash_balance


def main():
    # My testing will use MSFT.csv
    filename = input("Enter a filename for stock data (CSV format): ")

    # Calls moving average algorithm
    alg1_stocks, alg1_balance = alg_moving_average(filename)

    # Print results of the moving average algorithm, returned above:
    print("The results are: {0} of owned stock and ${1:0.2f} \
in cash!".format(alg1_stocks, alg1_balance))

    # Calling custom algorithim:
    alg2_stocks, alg2_balance = alg_mine(filename)

    # Print results of the custom algorithm:
    print("The results are: {0} of owned stock and ${1:0.2f} \
in cash!".format(alg2_stocks, alg2_balance))
    

if __name__ == '__main__':
    main()
