"""buff api"""
import requests
import json
import pickle
import os


class Goods:
    def __init__(self, goods_id, cost=0):
        self.index = 0
        self.id = goods_id  # buff id
        self.youpin_id = 0

        self.name = ''  # name
        self.cost = cost  # 购入花费
        self.price = 0  # buff当前价格
        self.steam_price = 0  # steam当前价格

        self.status = 0  # 0:在库中 1:租出 2:卖出

        self.on_sale_count = 0  # youpin在售
        self.on_lease_count = 0  # youpin租出
        self.lease_unit_price = 0  # youpin短租金
        self.long_lease_unit_price = 0  # youpin长租金
        self.youpin_price = 0  # youpin当前价格
        self.deposit = 0  # 押金
        self.sell_price = 0  # 卖出价格
        self.__get_buff()
        self.__get_youpin()

    def __get_buff(self):
        url = (
            'https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id='
            + self.id
        )
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            self.price = eval(data['data']['items'][0]['price'])
            self.name = data['data']['goods_infos'][self.id]['name']
            self.steam_price = eval(
                data['data']['goods_infos'][self.id]['steam_price_cny']
            )
            return True
        else:
            return False

    def __get_youpin(self):
        url = "https://api.youpin898.com/api/homepage/es/template/GetCsGoPagedList"
        payload = json.dumps(
            {
                "listType": "30",
                "gameId": "730",
                "keyWords": self.name,
                "pageIndex": 1,
                "pageSize": 20,
                "sortType": "0",
                "listSortType": "2",
            }
        )
        headers = {
            'authority': 'api.youpin898.com',
            'content-type': 'application/json;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42',
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        self.youpin_id = response['Data'][0]['Id']
        self.on_sale_count = response['Data'][0]["OnSaleCount"]  # youpin在售
        self.on_lease_count = response['Data'][0]["OnLeaseCount"]  # youpin租出
        self.lease_unit_price = eval(response['Data'][0]["LeaseUnitPrice"])  # youpin短租金
        self.long_lease_unit_price = eval(
            response['Data'][0]["LongLeaseUnitPrice"]
        )  # youpin长租金
        self.youpin_price = eval(response['Data'][0]["Price"])  # youpin当前价格
        self.deposit = eval(response['Data'][0]["LeaseDeposit"])  # 押金

    def refresh(self):
        self.__get_buff()
        self.__get_youpin()

    def sell(self, price):
        self.status = 2
        self.sell_price = price

    def lease(self):
        self.status = 1

    def back(self):
        self.status = 0

    def get_status(self):
        if self.status == 0 and self.cost != 0:
            return "在库中"
        elif self.status == 1:
            return "租出"
        elif self.status == 0 and self.cost == 0:
            return "观望中"
        else:
            return "卖出"

    def __call__(self):
        if self.cost == 0:
            return {
                "BuffId": self.id,
                "YoupinId": self.youpin_id,
                "Name": self.name,
                "Cost": self.cost,
                "BuffPrice": self.price,
                "YoupinPrice": self.youpin_price,
                "SteamPrice": self.steam_price,
                "Status": self.status,
                "OnSaleCount": self.on_sale_count,
                "OnLeaseCount": self.on_lease_count,
                "LeaseUnitPrice": self.lease_unit_price,
                "LongLeaseUnitPrice": self.long_lease_unit_price,
                "Deposit": self.deposit,
                "RentSaleRatio": self.on_lease_count / self.on_sale_count,  # 目前租售比
                "LeaseRatio": self.lease_unit_price / self.price * 100,  # 租金比例
                "DepositRatio": self.deposit / self.price * 100,  # 押金比例
                "AnnualizedShortTermLeaseRatio": 192
                * self.lease_unit_price
                / self.price
                * 100,  # 年化短租比例
                "AnnualizedLongTermLeaseRatio": 264
                * self.long_lease_unit_price
                / self.price
                * 100,  # 年化长租比例
                "CashRatio": self.price / self.steam_price * 100,  # 套现比例
                "BuffYouyouRatio": self.price / self.youpin_price,  # buff和有品价格比例
            }
        else:
            return {
                "BuffId": self.id,
                "YoupinId": self.youpin_id,
                "Name": self.name,
                "Cost": self.cost,
                "BuffPrice": self.price,
                "YoupinPrice": self.youpin_price,
                "SteamPrice": self.steam_price,
                "Status": self.status,
                "OnSaleCount": self.on_sale_count,
                "OnLeaseCount": self.on_lease_count,
                "LeaseUnitPrice": self.lease_unit_price,
                "LongLeaseUnitPrice": self.long_lease_unit_price,
                "Deposit": self.deposit,
                "RentSaleRatio": self.on_lease_count / self.on_sale_count,  # 目前租售比
                "TheoreticalCurrentEarnings": self.price - self.cost,  # 理论目前收益
                "TheoreticalCurrentEarningsRate": (self.price - self.cost)
                / self.cost
                * 100,  # 理论目前收益率
                "LeaseRatio": self.lease_unit_price / self.price * 100,  # 租金比例
                "DepositRatio": self.deposit / self.price * 100,  # 押金比例
                "AnnualizedShortTermLeaseRatio": 192
                * self.lease_unit_price
                / self.price
                * 100,  # 年化短租比例
                "AnnualizedLongTermLeaseRatio": 264
                * self.long_lease_unit_price
                / self.price
                * 100,  # 年化长租比例
                "CashRatio": self.price / self.steam_price * 100,  # 套现比例
                "BuffYouyouRatio": self.price / self.youpin_price,  # buff和有品价格比例
            }


class Inventory:
    """库存管理"""

    def __init__(self, path) -> None:
        """选择一个库存并启动该库存"""
        self.path = path
        if os.path.exists(path):
            self.__data = pickle.load(open(path, "rb"))
        else:
            self.__data = {}

    def __call__(self):
        return self.__data

    def __iter__(self):
        return self.__data.__iter__()

    def add(self, good: Goods):
        if good.__class__ == Goods:
            good.index = len(self())
            self.__data[good.index] = good
        else:
            raise TypeError("输入类型错误")

    def delete(self, good):
        del self()[good]

    def save(self):
        pickle.dump(self.__data, open(self.path, "wb"))

    def reset(self):
        self.__data = []

    def total_cost(self):
        return sum([self()[good].cost for good in self()])

    def total_cost_in_inventory(self):
        return sum(
            [
                self()[good].cost
                for good in self()
                if (self()[good].status == 0 and self()[good].cost != 0)
                or self()[good].status == 1
            ]
        )

    def calc_buff_earn(self):
        return sum(
            [
                self()[good].price - self()[good].cost
                for good in self()
                if self()[good].cost != 0
            ]
        )

    def calc_youpin_earn(self):
        return sum(
            [
                self()[good].youpin_price - self()[good].cost
                for good in self()
                if self()[good].cost != 0
            ]
        )

    def calc_buff_earn_rate(self):
        return self.calc_buff_earn() / self.total_cost() * 100

    def calc_youpin_earn_rate(self):
        return self.calc_youpin_earn() / self.total_cost() * 100

    def calc_price(self):
        return sum(
            [
                self()[good].price
                for good in self()
                if (self()[good].status == 0 and self()[good].cost != 0)
                or self()[good].status == 1
            ]
        )

    def sell_price(self):
        return sum(
            [self()[good].sell_price for good in self() if self()[good].status == 2]
        )


if __name__ == "__main__":
    g = Goods('759220', 22.5)
    print(g)
