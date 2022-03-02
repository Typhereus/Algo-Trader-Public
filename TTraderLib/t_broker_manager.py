from binance.enums import *

def order_send_to_broker(client, side, quantity, symbol, order_type=ORDER_TYPE_MARKET):

    # This shit has a lot of problems
    # Fix Precision issues, Take USD Upfront..., have its own client manager maybe...

    # return purchase price
    # return order successful
    # return sell price
    # return order info
    try:
        place_order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)

        order_data = place_order['fills']
        purchase_price = float(order_data[0]['price'])
        #note("Bought at: " + str(purchase_price) + " " + str(timestamp_date[-1]))

        result = str(place_order)
        #note("Order Result: {}".format(result))

    except Exception as e:
        #note("an exception occurred in order sent to broker - {}".format(e))
        return False

    return True