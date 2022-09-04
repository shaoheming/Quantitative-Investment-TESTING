# baostock提供1990-12-19至今的日k数据，而futuAPI仅有最近10年的数据，明显数据量上不如baostock，所以本期用 baostock
# A股综合指数+沪深300+中证500指数每日收盘价曲线

import baostock as bs
import pandas as pd

import datetime
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
import numpy as np
from pyecharts.commons.utils import JsCode
import talib

OUTPUT_HTML = "test011.html"  # 输出网页地址
TRADING_PERIOD = "d"  # 信号 K 线周期,d为日线
INDEX_CODE = ['sh.000001', 'sh.000016', 'sh.000300', 'sh.000905']  # 重点指数
INDEX_NAME = ['A股综合', '上证50', '沪深300', '中证500']
TRADING_CODE = 'sh.000001'  # A股综合指数
START_DATE = '1990-12-19'  # 股票回溯开始日期,A股开市日
END_DATE = datetime.date.today().strftime('%Y-%m-%d')  # 股票回溯结束日期


# 画A股核心指数曲线
def draw_indexLines(index_code=INDEX_CODE, index_name=INDEX_NAME, self=None):
    print('开始绘制指数曲线draw_indexLines')
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    index_lines = Line()

    for i, _code in enumerate(index_code):
        #  所有指数分别读取
        rs = bs.query_history_k_data_plus(_code,
                                          "date,code,close",
                                          start_date=START_DATE,
                                          end_date=END_DATE,
                                          frequency="d")
        # print('query_history_k_data_plus respond error_code:' + rs.error_code)
        # print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        Stock_price = result['close'].values.tolist()  # 每日收盘价
        Stock_date = result['date'].values.tolist()

        # 每个指数有数据的日期不同，所以需要特殊处理
        # 如果是综指，则画线，否则就新建一条线然后叠上去
        if i == 0:
            index_lines.add_xaxis(Stock_date)
            index_lines.add_yaxis(
                series_name=index_name[i],
                y_axis=Stock_price,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=1),
                label_opts=opts.LabelOpts(is_show=True),  # 显示具体数值
            )
        else:
            line_temp = Line()
            line_temp.add_xaxis(Stock_date)
            line_temp.add_yaxis(
                series_name=index_name[i],
                y_axis=Stock_price,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=1),
                label_opts=opts.LabelOpts(is_show=True),  # 显示具体数值
            )
            index_lines.overlap(line_temp)

    index_lines.set_global_opts(
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
                xaxis_index=[0],
                range_start=0,
                range_end=100,
            ),
            opts.DataZoomOpts(
                is_show=True,
                type_="slider",
                xaxis_index=[0],  # 四张图公用缩放
                pos_bottom="20%",
                range_start=80,
                range_end=100,
            ),
        ],
        title_opts=opts.TitleOpts(title="股价k线图"),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        legend_opts=opts.LegendOpts(is_show=True, pos_top='2%', pos_left='5%'),  # 图例
    )

    # 登出系统
    bs.logout()
    print('完成绘制指数曲线draw_indexLines')

    return index_lines


def drawAll():
    grid_chart = Grid(init_opts=opts.InitOpts(width="2500px", height="1250px"))

    grid_chart.add(
        draw_indexLines(),
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="3%", height="70%"),
    )

    return grid_chart


# 主函数
if __name__ == '__main__':
    grid_chart = drawAll()
    grid_chart.render(OUTPUT_HTML)

