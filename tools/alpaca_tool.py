from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce, QueryOrderStatus

class AlpacaTool:
    def __init__(self, api_key, secret_key):
        self.trading_client = TradingClient(api_key, secret_key)

    def buying_power(self):
        account = self.trading_client.get_account()

        if account.trading_blocked:
            raise Exception('Account is currently restricted from trading.')
        
        return account.buying_power
    
    def gain_loss(self):
        account = self.trading_client.get_account()

        if account.trading_blocked:
            raise Exception('Account is currently restricted from trading.')
        
        return float(account.equity) - float(account.last_equity)
    
    def get_all_assets(self):
        search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)

        return self.trading_client.get_all_assets(search_params)
    
    def get_open_position(self, ticker):
        return self.trading_client.get_open_position(ticker)
    
    def get_all_positions(self):
        # Get a list of all of our positions.
        return self.trading_client.get_all_positions()
    
    def create_buy_market_order(self, ticker, quantity):
        # preparing market order
        market_order_data = MarketOrderRequest(
                                symbol=ticker,
                                qty=quantity,
                                side=OrderSide.BUY,
                                time_in_force=TimeInForce.FOK
                            )

        # Market order
        return self.trading_client.submit_order(order_data=market_order_data)
    
    def create_sell_market_order(self, ticker, quantity):
        # preparing market order
        market_order_data = MarketOrderRequest(
                                symbol=ticker,
                                qty=quantity,
                                side=OrderSide.SELL,
                                time_in_force=TimeInForce.DAY
                            )

        # Market order
        return self.trading_client.submit_order(order_data=market_order_data)
    
    def get_all_closed_orders(self, limit=100):
        # Get the last 100 closed orders
        get_orders_data = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            limit=limit,
            nested=True  # show nested multi-leg orders
        )

        return self.trading_client.get_orders(filter=get_orders_data)
    
    def get_all_open_orders(self, limit=100):
        # Get the last 100 closed orders
        get_orders_data = GetOrdersRequest(
            status=QueryOrderStatus.OPEN,
            limit=limit,
            nested=False  # show nested multi-leg orders
        )

        return self.trading_client.get_orders(filter=get_orders_data)
    
#     from alpaca.trading.stream import TradingStream

# stream = TradingStream('api-key', 'secret-key', paper=True)


# @conn.on(client_order_id)
# async def on_msg(data):
#     # Print the update to the console.
#     print("Update for {}. Event: {}.".format(data.event))

# stream.subscribe_trade_updates(on_msg)
# # Start listening for updates.
# stream.run()