from privatbank_client import *

parser = argparse.ArgumentParser(description='Request privatbank card info')
parser.add_argument('--card', required = True, type=int, help='Card num')
parser.add_argument('--secret', required = True, type=str, help='Merchant secret')
parser.add_argument('--client_id', required = True, type=int, help='Merchant id')
parser.add_argument('--balance', required = False, action='store_true', help='Get information about card balance')
parser.add_argument('--transactions', required = False, action='store_true', help='Get transactions History')
parser.add_argument('--from_date', required = False, help='Start date for transactions history')
parser.add_argument('--to_date', required = False, help='End date for transactions history')
parser.add_argument('--quota', required = False, type=str, help='Calculate quota per day for specified date')
parser.add_argument('--spent_today', required = False,  action='store_true', help='Amount of money spent today')

def transactions(client_id, secret, card, from_date, to_date):
    transactions = get_transactions(client_id, secret, card, from_date, to_date)
    for x in transactions:
        print("{} : {}/{} \t : {}({})".format(x["datetime"],x["amount"],x["rest"],x["description"].encode("utf-8"),x["terminal"]))


def daily_quota(client_id, secret, card, to_date):
    now = datetime.now()
    today = now.strftime("%d.%m.%Y")
    def balance():
        transactions = get_transactions(client_id, secret, card, today, today)
        if len(transactions) == 0 :
            return float(current_balance(client_id, secret, card))
        first_transaction = min(transactions, key = lambda tr:tr["datetime"])
        return float(first_transaction["rest"])
    amount = balance()
    salary = now.replace(month = to_date.month, day= to_date.day)
    amount_of_days = (salary - now).days
    uah_per_day = amount / amount_of_days
    return uah_per_day

def spent_today(client_id, secret, card):
    now = datetime.now()
    today = now.strftime("%d.%m.%Y")
    transactions = get_transactions(client_id, secret, card, today, today)
    amount = 0.0
    for t in transactions:
        amount += float(t["amount"])
    return amount


def main():
    args = parser.parse_args()
    if (args.quota):
        salary_date = datetime.strptime(args.quota, '%d.%m.%Y')
        print(daily_quota(args.client_id, args.secret, args.card, salary_date))
    if (args.balance):
        print(current_balance(args.client_id, args.secret, args.card))
    if (args.transactions):
        transactions(args.client_id, args.secret, args.card, args.from_date, args.to_date)
    if (args.spent_today):
        print(spent_today(args.client_id, args.secret, args.card))
if __name__ == "__main__":
    main()

