# 绘制K线图 & MACD & MA

from futu import *
import datetime
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
import numpy as np
from pyecharts.commons.utils import JsCode

FUTUOPEND_ADDRESS = '127.0.0.1'  # FutuOpenD 监听地址
FUTUOPEND_PORT = 11111  # FutuOpenD 监听端口

TRADING_PERIOD = KLType.K_DAY  # 信号 K 线周期
TRADING_CODE = 'HK.00700'  # 股票标的
START_DATE = '2018-09-11'  # 股票回溯开始日期
END_DATE = datetime.date.today().strftime('%Y-%m-%d')  # 股票回溯结束日期
FAST_MOVING_AVERAGE = 5  # 均线快线的周期
SLOW_MOVING_AVERAGE = 10  # 均线慢线的周期

# MACD相关设定
MACD_SHORT = 12
MACD_LONG = 26
MACD_SIGNAL = 9


# 根据收盘价，计算MA, 返回快线和慢线数组
def calculate_MA(closeArray, fast_param, slow_param):
    fast_values = []  # 快线数组
    slow_values = []  # 慢线数组

    for i in range(len(closeArray)):
        if i < FAST_MOVING_AVERAGE:
            fast_values.append(np.nan)
        else:
            fast_value = format(sum(closeArray[i - FAST_MOVING_AVERAGE:i]) / FAST_MOVING_AVERAGE,
                                '.2f')  # 四舍五入取2位小数
            fast_values.append(float(fast_value))

        if i < SLOW_MOVING_AVERAGE:
            slow_values.append(np.nan)
        else:
            slow_value = format(sum(closeArray[i - SLOW_MOVING_AVERAGE:i]) / SLOW_MOVING_AVERAGE, '.2f')
            slow_values.append(float(slow_value))

    return fast_values, slow_values


# 根据收盘价，计算MACD，返回macd,diff,dea
def calculateEMA(period, closeArray, emaArray=[]):
    """计算指数移动平均"""
    length = len(closeArray)
    nanCounter = np.count_nonzero(np.isnan(closeArray))
    if not emaArray:
        emaArray.extend(np.tile([np.nan], (nanCounter + period - 1)))
        firstema = np.mean(closeArray[nanCounter:nanCounter + period - 1])
        emaArray.append(firstema)
        for i in range(nanCounter + period, length):
            ema = (2 * closeArray[i] + (period - 1) * emaArray[-1]) / (period + 1)
            emaArray.append(ema)
    return np.array(emaArray)


def calculateMACD(closeArray, shortPeriod=12, longPeriod=26, signalPeriod=9):
    ema_short = calculateEMA(shortPeriod, closeArray, [])
    ema_long = calculateEMA(longPeriod, closeArray, [])
    diff = np.round((ema_short - ema_long), 2)
    dea = np.round(calculateEMA(signalPeriod, diff, []), 2)
    macd = 2 * (diff - dea)
    return macd, diff, dea


# 画k线图
def draw_klines(data, self=None):
    klineData = data[['open', 'close', 'low', 'high']].values.tolist()  # 将pd转换为数组 股价
    klineX = data['time_key'].values.tolist()
    klineXData = [dateStr[0:10] for dateStr in klineX]  # 横坐标 日期

    kline = Kline()
    kline.add_xaxis(xaxis_data=klineXData)
    kline.add_yaxis(
        series_name="股价/港币",
        y_axis=klineData,
        itemstyle_opts=opts.ItemStyleOpts(opacity=.8),
    )
    kline.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            name='日期',
            is_scale=True,
        ),
        yaxis_opts=opts.AxisOpts(
            name='股价/港币',
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.7)
            ),
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                is_show=False,
                type_="inside",
                xaxis_index=[0, 1],
                range_start=80,
                range_end=100,
            ),
            # xaxis_index=[0, 0]设置第一幅图为内部缩放
            opts.DataZoomOpts(
                is_show=True,
                type_="slider",
                xaxis_index=[0, 1],
                pos_top="95%",
                range_start=80,
                range_end=100,
            ),
            # xaxis_index=[0, 1]连接第二幅图的axis
        ],
        title_opts=opts.TitleOpts(title="股价k线图"),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
    )

    maLine = Line()
    maLine.add_xaxis(klineXData)
    closeArray = data['close'].values.tolist()
    fast_MA, slow_MA = calculate_MA(closeArray, FAST_MOVING_AVERAGE, SLOW_MOVING_AVERAGE)  # 计算均线

    maLine.add_yaxis(
        series_name="MA" + str(FAST_MOVING_AVERAGE),
        y_axis=fast_MA,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
        label_opts=opts.LabelOpts(is_show=False),  # 不显示具体数值
        z=3,  # ma在最顶层
    )

    maLine.add_yaxis(
        series_name="MA" + str(SLOW_MOVING_AVERAGE),
        y_axis=slow_MA,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=2),
        label_opts=opts.LabelOpts(is_show=False),
        z=4,
    )

    KlineWithMA = kline.overlap(maLine)  # MA画在k线上
    return KlineWithMA


# 画MACD
def drawMACD(data):
    closeArray = data['close'].values.tolist()
    DIF, DEA, MACD = calculateMACD(closeArray, MACD_SHORT, MACD_LONG, MACD_SIGNAL)

    klineX = data['time_key'].values.tolist()
    klineXData = [dateStr[0:10] for dateStr in klineX]

    bar_2 = Bar()
    bar_2.add_xaxis(klineXData)
    bar_2.add_yaxis(
        series_name="MACD",
        y_axis=MACD.tolist(),
        xaxis_index=1,
        yaxis_index=1,
        label_opts=opts.LabelOpts(is_show=False),
        z=0,
        itemstyle_opts=opts.ItemStyleOpts(
            opacity=0.7,
            color=JsCode(
                # 就是这么神奇，要写在注释中,但是的确是生效的,通过浏览器进行解析
                """
                                    function(params) {
                                        var colorList;
                                        if (params.data >= 0) {
                                          colorList = '#D3403B';
                                        } else {
                                          colorList = '#66A578';
                                        }
                                        return colorList;
                                    }
                                    """
            )
        )
    )

    bar_2.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=1,
            axislabel_opts=opts.LabelOpts(is_show=True),
            is_scale=True,
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=1,
            split_number=4,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
        ),

        legend_opts=opts.LegendOpts(is_show=True, pos_top='70%'),  # 图例
    )

    line_2 = Line()
    line_2.add_xaxis(klineXData)
    line_2.add_yaxis(
        series_name="DIF",
        y_axis=DIF,
        xaxis_index=1,
        yaxis_index=2,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
    )
    line_2.add_yaxis(
        series_name="DEA",
        y_axis=DEA,
        xaxis_index=1,
        yaxis_index=2,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(opacity=1.0, width=2),
    )

    overlap_bar_line = bar_2.overlap(line_2)
    return overlap_bar_line


def drawAll(overlap_kline_ma, overlap_bar_line):
    grid_chart = Grid(init_opts=opts.InitOpts(width="2560px", height="800px"))
    # K线图和 MA 的折线图
    grid_chart.add(
        overlap_kline_ma,
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="3%", height="60%"),
    )
    # MACD DIFS DEAS
    grid_chart.add(
        overlap_bar_line,
        grid_opts=opts.GridOpts( pos_left="3%", pos_right="3%", pos_top="72%", height="20%"),
    )
    return grid_chart


def getGrid(kdata):
    k = draw_klines(kdata)
    m = drawMACD(kdata)
    return drawAll(k, m)


# 主函数
if __name__ == '__main__':
    quote_ctx = OpenQuoteContext(host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT)  # 获取行情对象
    # 获取历史k线数据
    ret, data, page_req_key = quote_ctx.request_history_kline(TRADING_CODE, start=START_DATE, end=END_DATE)
    if ret != RET_OK:
        print('获取K线失败：', data)

    grid_chart = getGrid(data)
    grid_chart.render("test007.01.html")

    quote_ctx.close()
