import re
from collections import OrderedDict
import requests
from common import BankBase, format_value


class BankLeumi(BankBase):
    LOGIN_URL = "https://hb2.bankleumi.co.il/H/Login.html"
    LOGIN_POST_URL = "https://hb2.bankleumi.co.il/InternalSite/Validate.asp"
    HOME_URL = "https://hb2.bankleumi.co.il/uniquesig0/ebanking/SO/SPA.aspx#/hpsummary"
    CHECKING_RE = r'{\\"AccountType\\":\\"CHECKING\\",\\"TotalPerAccountType\\":(.+?)}'
    HOLDINGS_RE = r'{\\"AccountType\\":\\"SECURITIES\\",\\"TotalPerAccountType\\":(.+?)}'
    DEPOSIT_RE = r'{\\"AccountType\\":\\"CD\\",\\"TotalPerAccountType\\":(.+?)}'

    def __init__(self, asset_section, **asset_options):
        super(BankLeumi, self).__init__(asset_section, **asset_options)
        self._summery_page = self._session.get(self.HOME_URL).text

    def _establish_session(self, username, password):
        s = requests.Session()
        s.get(self.LOGIN_URL)
        post_data = {'system': 'test', 'uid': username, 'password': password, 'command': 'login'}
        s.post(self.LOGIN_POST_URL, data=post_data)
        return s

    def _get_checking_balance(self):
        val_matchobj = re.search(self.CHECKING_RE, self._summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'Checking')

    def _get_holdings_balance(self):
        val_matchobj = re.search(self.HOLDINGS_RE, self._summery_page)
        val = val_matchobj.group(1)
        return format_value(val, 'Holdings')

    def _get_deposit_balance(self):
        val_matchobj = re.search(self.DEPOSIT_RE, self._summery_page)
        if val_matchobj is None:
            return format_value("0", 'Deposit')
        val = val_matchobj.group(1)
        return format_value(val, 'Deposit')

    def get_values(self):
        return OrderedDict([("Checking", self._get_checking_balance()),
                            ("Holdings", self._get_holdings_balance()),
                            ("Deposit", self._get_deposit_balance())])

    def get_summery_page(self):
        return self._summery_page
