# 计算均线并形成数组

from futu import *
import datetime
from pyecharts import options as opts
from pyecharts.charts import Kline, Line

FUTUOPEND_ADDRESS = '127.0.0.1'  # FutuOpenD 监听地址
FUTUOPEND_PORT = 11111  # FutuOpenD 监听端口

TRADING_PERIOD = KLType.K_DAY  # 信号 K 线周期
TRADING_CODE = 'HK.00700'  # 股票标的
START_DATE = '2021-09-11'  # 股票回溯开始日期
END_DATE = datetime.date.today().strftime('%Y-%m-%d')  # 股票回溯结束日期
FAST_MOVING_AVERAGE = 5  # 均线快线的周期
SLOW_MOVING_AVERAGE = 10  # 均线慢线的周期


# 拉取 K 线，计算均线，判断多空
def calculate_MA(code, fast_param, slow_param):
    # 容错机制
    if fast_param <= 0 or slow_param <= 0:
        return 0
    if fast_param > slow_param:
        return calculate_MA(code, slow_param, fast_param)

    # 获取历史k线数据
    ret, data, page_req_key = quote_ctx.request_history_kline(TRADING_CODE, start=START_DATE, end=END_DATE)
    if ret != RET_OK:
        print('获取K线失败：', data)
        return 0

    # 根据每日收盘价，计算均线
    candlestick_list = data['close'].values.tolist()
    # print(candlestick_list)

    fast_values = []  # 快线数组
    slow_values = []  # 慢线数组

    for i in range(len(candlestick_list)):
        if i < FAST_MOVING_AVERAGE:
            fast_values.append('None')
        else:
            fast_value = format(sum(candlestick_list[i - FAST_MOVING_AVERAGE:i]) / FAST_MOVING_AVERAGE,
                                '.2f')  # 四舍五入取2位小数
            fast_values.append(fast_value)

        if i < SLOW_MOVING_AVERAGE:
            slow_values.append('None')
        else:
            slow_value = format(sum(candlestick_list[i - SLOW_MOVING_AVERAGE:i]) / SLOW_MOVING_AVERAGE, '.2f')
            slow_values.append(slow_value)

    # print(fast_values)
    # print(slow_values)

    return fast_values, slow_values

#画k线图
def draw_klines(code):
    ret, data, page_req_key = quote_ctx.request_history_kline(code, start=START_DATE,end=END_DATE)

    if ret == RET_OK:
        # print(data)
        # print(data['code'][0])    # 取第一条的股票代码
        klineData = data[['open', 'close', 'low', 'high']].values.tolist()  # 将pd转换为数组 股价
        klineX = data['time_key'].values.tolist()
        klineXData = [dateStr[0:10] for dateStr in klineX]

        kline = (
            Kline(init_opts=opts.InitOpts(width='2500px',
                                          height='800px',
                                          page_title='Kline test', ))
            .add_xaxis(xaxis_data=klineXData)
            .add_yaxis("股价/港币", klineData)
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                datazoom_opts=[opts.DataZoomOpts()],
                title_opts=opts.TitleOpts(title="股价k线图"),
            )

        )

        maline = Line()
        maline.add_xaxis(klineXData)
        fast_MA, slow_MA = calculate_MA(TRADING_PERIOD, FAST_MOVING_AVERAGE, SLOW_MOVING_AVERAGE)  # 计算均线

        maline.add_yaxis(
            series_name="MA"+str(FAST_MOVING_AVERAGE),
            y_axis = fast_MA,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.7,width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        maline.add_yaxis(
            series_name="MA" + str(SLOW_MOVING_AVERAGE),
            y_axis=slow_MA,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(opacity=0.7, width=2),
            label_opts=opts.LabelOpts(is_show=False)
        )

        maline.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=1,
                axislabel_opts=opts.LabelOpts(is_show=False)
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                split_number=3,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=True),
            ),
        )
        KlineWithMA = kline.overlap(maline) # MA画在k线上
        KlineWithMA.render("test005.02.html")

    else:
        print('error:', data)



# 主函数
if __name__ == '__main__':
    quote_ctx = OpenQuoteContext(host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT)  # 获取行情对象
    # calculate_MA(TRADING_PERIOD, FAST_MOVING_AVERAGE, SLOW_MOVING_AVERAGE)  # 计算均线
    draw_klines(TRADING_CODE)  # 画k线图
    quote_ctx.close()
