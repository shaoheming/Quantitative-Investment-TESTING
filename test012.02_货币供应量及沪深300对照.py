#货币供应量曲线绘制 叠加沪深300曲线 同一张表双轴实现 2022.0912
import baostock as bs
import pandas as pd
from datetime import datetime
import time
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid

START_DATE = '1990-12-19'  # 股票回溯开始日期,A股开市日
END_DATE = datetime.today().strftime('%Y-%m-%d')  # 股票回溯结束日期
INDEX_CODE = ['sh.000001', 'sh.000016', 'sh.000300', 'sh.000905']  # 重点指数
INDEX_NAME = ['A股综合', '上证50', '沪深300', '中证500']
OUTPUT_HTML = "test012.html"  # 输出网页地址

# 展示货币供应量数据
def draw_Money_Supply():
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 获取货币供应量
    rs = bs.query_money_supply_data_month(start_date=datetime.strptime(START_DATE, '%Y-%m-%d').strftime('%Y-%m'),
                                          end_date=datetime.strptime(END_DATE, '%Y-%m-%d').strftime('%Y-%m'))
    print('query_money_supply_data_month respond error_code:' + rs.error_code)
    print('query_money_supply_data_month respond  error_msg:' + rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    # print(result)

    date = []
    date_list = pd.to_datetime(result['statYear']+'-'+result['statMonth']).tolist()
    for date_value in date_list:
        date_value = date_value.to_pydatetime().date()
        date.append(date_value)

    M0_Value = result['m0Month'].values.tolist()
    M1_Value = result['m1Month'].values.tolist()
    M2_Value = result['m2Month'].values.tolist()
    #绘制曲线
    M_Line = Line()
    M_Line.add_xaxis(date)
    M_Line.add_yaxis(
        series_name='M0',
        y_axis=M0_Value,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 是否显示具体数值
    )
    M_Line.add_yaxis(
        series_name='M1',
        y_axis=M1_Value,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 是否显示具体数值
    )
    M_Line.add_yaxis(
        series_name='M2',
        y_axis=M2_Value,
        is_smooth=True,
        linestyle_opts=opts.LineStyleOpts(opacity=0.9, width=1),
        label_opts=opts.LabelOpts(is_show=False),  # 是否显示具体数值
    )

    M_Line.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            name='日期',
            is_scale=True,
        ),
        yaxis_opts=opts.AxisOpts(
            name='供应量',
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
                xaxis_index=[0,1],  # 四张图公用缩放
                pos_bottom="00%",
                range_start=0,
                range_end=100,
            ),
        ],
        title_opts=opts.TitleOpts(title="货币供应量"),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        legend_opts=opts.LegendOpts(is_show=True, pos_top='2%', pos_left='5%'),  # 图例
    )

    # 登出系统
    bs.logout()
    return M_Line

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
                                          end_date='2022-06-01',
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
            name='点数',
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.7)
            ),
        ),

        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross'),
        legend_opts=opts.LegendOpts(is_show=True, pos_top='60%', pos_left='5%'),  # 图例
    )

    # 登出系统
    bs.logout()
    print('完成绘制指数曲线draw_indexLines')

    return index_lines



#绘制图表
def drawAll():
    grid_chart = Grid(init_opts=opts.InitOpts(width="2500px", height="1250px"))

    grid_chart.add(
        draw_Money_Supply(),
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="3%", height="50%"),
    )

    grid_chart.add(
        draw_indexLines(),
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="3%",pos_top="60%", height="30%"),
    )

    return grid_chart


# 主函数
if __name__ == '__main__':
    grid_chart = drawAll()
    grid_chart.render(OUTPUT_HTML)