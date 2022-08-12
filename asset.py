class Assets:
    def __init__(self, start_jpy, sell_fee=0.0, buy_fee=0.0):
        """
        資産管理クラス
        :param start_jpy: 日本円初期値
        :param sell_fee: 売却手数料
        :param buy_fee: 購入手数料
        """
        self.jpy = start_jpy  # 保有日本円
        self.assets_info = []  # 購入した暗号資産の情報
        self.asset_sum = 0.0  # 暗号資産の合計

        self.SELL_FEE = sell_fee  # 売却手数料
        self.BUY_FEE = buy_fee  # 購入手数料

    def get_buyable_amount(self, price):
        """
        購入可能な暗号資産の数量を取得
        :param price: 購入単価
        :return: 購入可能数量
        """
        return self.jpy / price

    def add_asset_info(self, price, amount):
        """
        資産情報を追加
        1. 購入した資産を資産情報に追加
        2. 購入に使用した日本円を減算
        :param price: 購入単価
        :param amount: 購入数量
        """
        # 暗号資産の情報を追加
        self.assets_info.append({"price": price, "amount": amount})
        self.asset_sum += amount

        # 日本円の情報を更新
        self.jpy -= price * amount

    def reduce_asset_info(self, price, amount):
        """
        資産情報をから暗号資産量を減算

        :param price: 売却単価
        :param amount: 売却数量
        :return: sold_asset_info: 売却資産情報
        - buy_price: 購入単価
        - sell_price: 売却単価
        - amount: 売却数量
        :return: reduce_amount: 暗号資産売却量
        """
        sold_asset_info = []

        remain_amount = amount  # 処理対象残量
        for info in self.assets_info:
            # 処理対象残量および所有暗号資産が存在する場合
            if remain_amount > 0 and self.asset_sum > 0:
                # 資産情報の数量をすべて売却する場合
                if info["amount"] < remain_amount:
                    amount_info = info["amount"]

                # 資産情報の数量で一部売却できない場合
                else:
                    # 処理対象残量分だけ売却
                    amount_info = remain_amount

                # 売却資産情報を格納
                sold_asset_info.append({"buy_price": info["price"], "sell_price": price, "amount": amount_info})
                # 資産情報の更新
                self.asset_sum -= amount_info
                # 日本円所持量を加算
                self.jpy += (1 - self.SELL_FEE) * price * amount_info

                # 処理対象残量の更新
                remain_amount -= amount_info

            # 処理対象残量もしくは所有暗号資産が存在しない場合
            else:
                # 資産情報チェック終了
                break

        # 減少量を計算
        reduce_amount = amount - remain_amount

        return sold_asset_info, reduce_amount
