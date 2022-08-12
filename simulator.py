from asset import Assets


class Environment:
    def __init__(self, limit_time, start_jpy, sell_fee=0.0, buy_fee=0.0):
        """
        暗号資産取引シミュレータ
        :param limit_time: 注文情報保持最大時間
        :param start_jpy: 日本円初期値
        """
        self.assets = Assets(start_jpy=start_jpy, sell_fee=sell_fee, buy_fee=buy_fee)
        self.LIMIT_TIME = limit_time

        # 注文情報
        self.sell_orders = []
        self.buy_orders = []

        # 現在のOHLC
        self.open = None
        self.high = None
        self.low = None
        self.close = None

    @property
    def assets_list(self):
        """
        資産情報
        :return: asset_dict
        - crypto: 暗号資産数量
        - jpy: 日本円数量
        """
        # 資産管理クラスから暗号資産数量と日本円数量を取得
        crypto_amount = self.assets.asset_sum
        jpy_amount = self.assets.jpy

        asset_dict = {"crypto": crypto_amount, "jpy": jpy_amount}
        return asset_dict

    def step(self, open_price, high_price, low_price, close_price):
        """
        OHLC情報と資産情報を更新
        :param open_price:
        :param high_price:
        :param low_price:
        :param close_price:
        :return:
        """
        # 価格を更新
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price

        # 資産状況を更新
        del_order_info, sell_result_list, buy_result_list = self.update()
        update_info = {
            "sell_update_info": sell_result_list,
            "buy_update_info": buy_result_list,
            "del_order_info": del_order_info
        }

        return update_info

    def update(self):
        """
        注文情報を確認して保有資産情報を更新
        1. 買い注文の約定チェック
        2. 売り注文の約定チェック
        3. 一定時間経過後の注文を削除
        :return:
        """
        # 売り注文約定チェックと売却結果を取得
        sell_results_list = self.check_sell_contract()
        # 買い注文約定チェックと購入結果を取得
        buy_results_list = self.check_buy_contract()
        # 一定時間経過後の注文を削除
        del_order_info = self.del_old_order()

        return del_order_info, sell_results_list, buy_results_list

    def check_buy_contract(self):
        """
        買い注文の約定チェック
        買い注文単価が安値を下回った場合に約定
        :return: contract_info: 約定情報
        """
        contract_info = []
        tmp_buy_orders = []

        for order in self.buy_orders:
            # 購入注文単価が安値以下の場合に約定処理
            if order["price"] <= self.low:
                # 購入可能量取得
                buy_able_amounts = self.assets.get_buyable_amount(order["price"])
                if buy_able_amounts > 0:
                    if order["amount"] <= buy_able_amounts:
                        buy_amount = order["amount"]
                    else:
                        buy_amount = buy_able_amounts

                    # 資産情報を更新
                    self.assets.add_asset_info(order["price"], buy_amount)
                    # 注文情報を更新
                    order["amount"] -= buy_amount
                    # 約定情報を追加
                    contract_info.append({"price": order["price"], "amount": buy_amount})

                # 約定未完了の場合はタイマーを進める
                if order["amount"] > 0:
                    order["timer"] += 1
                    tmp_buy_orders.append(order)

        # 注文リストを更新
        self.buy_orders = tmp_buy_orders

        return contract_info

    def check_sell_contract(self):
        """
        売り注文の約定チェック
        売り注文単価が高値を上回った場合に約定
        :return: contract_info: 約定情報
        """
        contract_info = []
        tmp_sell_orders = []
        for order in self.sell_orders:
            # 売却単価が高値以上であれば約定処理
            if order["price"] >= self.high:
                sold_asset_info, contract_amount = self.assets.reduce_asset_info(order["price"], order["amount"])
                # 売却処理があった場合
                if len(sold_asset_info) > 0:
                    # 約定情報に売却結果を追加
                    contract_info += sold_asset_info
                    # 注文情報の更新
                    order["amount"] -= contract_amount

                    # 約定未完了の場合はタイマーを進める
                    if order["amount"] > 0:
                        order["timer"] += 1
                        tmp_sell_orders.append(order)

        # 注文リストを更新
        self.sell_orders = tmp_sell_orders

        return contract_info

    def del_old_order(self):
        """
        一定時間経過した注文を削除する
        :return: del_order_info
        - deleted_buy_order: 削除した買い注文
        - deleted_sell_order: 削除した売り注文
        """
        del_order_info = {"deleted_buy_order": [], "deleted_sell_order": []}

        # 買い注文のタイマーを確認
        tmp_buy_order = []
        for order in self.buy_orders:
            # 一定時間経過した注文
            if order["timer"] >= self.LIMIT_TIME:
                del_order_info["deleted_buy_order"].append(order)
            # 一定時間経過していない注文
            else:
                tmp_buy_order.append(order)
        # 一定時間経過していない注文を注文リストに反映
        self.buy_orders = tmp_buy_order

        # 売り注文のタイマーを確認
        tmp_sell_order = []
        for order in self.sell_orders:
            # 一定時間経過した注文
            if order["timer"] >= self.LIMIT_TIME:
                del_order_info["deleted_sell_order"].append(order)
            # 一定時間経過していない注文
            else:
                tmp_sell_order.append(order)
        # 一定時間経過していない注文を注文リストに反映
        self.sell_orders = tmp_sell_order

        return del_order_info
