import TTraderLib.t_event_system as t_event_system


class AllTraderEvents:
    on_order_buy_end = t_event_system.SimpleEventSystem()
    on_order_sell_end = t_event_system.SimpleEventSystem()
    on_period_begin = t_event_system.SimpleEventSystem()
    on_period_end = t_event_system.SimpleEventSystem()
    on_data_end = t_event_system.SimpleEventSystem()
