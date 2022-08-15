#todo 展示为k线图

from futu import *
import pandas as pd
import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Kline
import datetime


pd.set_option('display.width', None) #设置pandas数据完整展示

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2018-09-11', end=datetime.date.today().strftime('%Y-%m-%d'))  # 历史上某天到今天的数据,日期需要转化为字符串


if ret == RET_OK:
    #print(data)
    # print(data['code'][0])    # 取第一条的股票代码
    # print(data['close'].values.tolist())   # 第一页收盘价转为 list
    # plt.plot(data['close']) #绘制表格
    # plt.plot(data['open'])
    # plt.show()
    klineData = data[['open', 'close', 'low', 'high']].values.tolist()  #将pd转换为数组 股价
    klineX = data['time_key'].values.tolist()
    klineXData = [dateStr[0:10] for dateStr in klineX]

    #print(klineData)
    #print(klineXData)
else:
    print('error:', data)

kline=(
    Kline(init_opts=opts.InitOpts(width='2500px',
                                  height='800px',
                                  page_title='Kline test',))
        .add_xaxis(xaxis_data = klineXData)
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
kline.render("test004.html")


quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽