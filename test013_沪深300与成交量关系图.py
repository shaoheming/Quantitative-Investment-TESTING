# baostock提供1990-12-19至今的日k数据，而futuAPI仅有最近10年的数据，明显数据量上不如baostock，所以本期用 baostock
# 沪深300 以及 沪深300的成交额 成交量曲线画一张图上
#三y轴示意：https://gallery.pyecharts.org/#/Bar/multiple_y_axes
#将成交量展示出来 done 20220918
#y轴设定不同的颜色，与曲线颜色一致 done 20220918
#曲线平滑 done 20220918
#图表整体下移一点 + 标题居中  下移不做了，不会。好像也不影响什么。done 20220918

import baostock as bs
import pandas as pd

import datetime
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid

OUTPUT_HTML = "test013.html"  # 输出网页地址
INDEX_CODE = 'sh.000300'  # 沪深300
START_DATE = '1990-12-19'  # 股票回溯开始日期,A股开市日
END_DATE = datetime.date.today().strftime('%Y-%m-%d')  # 股票回溯结束日期
colors = ["#d14a61", "#5793f3", "#675bba"]

# 画A股核心指数曲线
def draw_indexLines(index_code=INDEX_CODE, self=None):
    print('开始绘制指数曲线draw_indexLines')
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    rs = bs.query_history_k_data_plus(index_code,
                                      "date,code,close,volume,amount",  # volume成交量 amount成交金额
                                      start_date=START_DATE,
                                      end_date=END_DATE,
                                      frequency="d")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    Stock_price = result['close'].values.tolist()  # 每日收盘价
    Stock_date = result['date'].values.tolist()
    Stock_amount = result['amount'].values.tolist() #以元为单位
    Stock_amount = [float(x)/100000000 for x in Stock_amount] #转为以亿为单位 零少一点 比较好算
    Stock_volume = result['volume'].values.tolist()
    Stock_volume = [float(x)/100000000 for x in Stock_volume] #亿股

    index_lines = Line(init_opts=opts.InitOpts(width="2500px", height="600px"))
    index_lines.add_xaxis(Stock_date)
    index_lines.add_yaxis(
        series_name='沪深300',
        y_axis=Stock_price,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(color=colors[0], opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 不显示具体数值，显示的话太乱了
    )
    index_lines.extend_axis(
        yaxis=opts.AxisOpts(
            name="成交额",
            type_="value",
            position="right",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[1])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value} 亿"),
        )
    )
    index_lines.extend_axis(
        yaxis=opts.AxisOpts(
            type_="value",
            name="成交量",
            position="right",
            offset=100,
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[2])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value}亿股"),
        )
    )

    index_lines.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            name=' ',
            is_scale=True,
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="点数",
            position="left",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(color=colors[0])
            ),
            axislabel_opts=opts.LabelOpts(formatter="{value}点"),
            splitline_opts=opts.SplitLineOpts(
                is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=.6)
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
                xaxis_index=[0],
                pos_bottom="0%",
                range_start=0,
                range_end=100,
            ),
        ],
        title_opts=opts.TitleOpts(title="沪深300与成交额+成交量曲线", pos_left='center'),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        legend_opts=opts.LegendOpts(is_show=True, pos_top='0%', pos_left='10%'),  # 图例
    )

    amount_line = Line()
    amount_line.add_xaxis(Stock_date)
    amount_line.add_yaxis(
        series_name='成交额',
        y_axis=Stock_amount,
        yaxis_index=1,  # 以哪个y轴为y轴
        z_level=1,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(color=colors[1], opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 不显示具体数值，显示的话太乱了
    )

    volume_line = Line()
    volume_line.add_xaxis(Stock_date)
    volume_line.add_yaxis(
        series_name='成交量',
        y_axis=Stock_volume,
        yaxis_index=2,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(color=colors[2], opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 不显示具体数值，显示的话太乱了
    )

    index_lines.overlap(amount_line)
    index_lines.overlap(volume_line)

    # 登出系统
    bs.logout()
    print('完成绘制曲线draw_indexLines')

    return index_lines


# 主函数
if __name__ == '__main__':
    draw_indexLines().render(OUTPUT_HTML)
