# csgo_investment

本仓库是基于爬虫和python streamlit实现的csgo饰品价格跟踪，可以追踪饰品的buff和悠悠有品价格，同时对盈利亏损状况进行统计。您可以将您希望加入的功能以issues的形式发出。

# 注意

由于悠悠有品的价格和租赁相关信息api现在需要鉴权才能访问，可以通过登录获取10天访问权限，但是这与本项目的初衷不符，所以暂时不再支持租赁信息，前端展示的租赁相关消息均为错误的，仅为最低限度修改代码而保留。该bug修复方式为使用无状态无鉴权api，但是该api无法获取租金相关信息。见issue [5](https://github.com/ShevonKuan/csgo_investment/issues/5)

# 名词和算法说明
- 租金比例 = (租金价格 / 饰品价格) * 100
- 年化短租比例 = (192 * 租金价格 / 饰品价格) * 100
- 年化长租比例 = (264 * 租金价格 / 饰品价格) * 100
- 套现比例 = 饰品价格 / Steam价格
- 总投资额 = 购买饰品总花费
- 追踪总量 = 加入库存文件的饰品数量
- 库存价值 = 库存饰品和已租出饰品总价值
- 总套现 = 卖出饰品总收入
- 盈利 = 总套现 + 库存价值 - 总投资额
- 总收益率 = 盈利 / 总投资额 * 100
- 持有饰品收益 = 库存价值 - 库存内和已租出饰品总花费
- 持有饰品收益率 = ( 库存价值 - 库存内和已租出饰品总花费 ) / 库存内和已租出饰品总花费 * 100

# Prerequirements
```bash
pip install -r requirements.txt
```

# Quick Start
```bash
streamlit run app.py
```

# Docker Mode
You can use docker to run this app.
1. Pull image first
```bash
docker pull shevonkuan/csgo_investment
```
2. Run the image
```bash
docker run -p 80:8501 -dit -v <path_to_store_data>:/usr/local/csgo/data --restart=always shevonkuan/csgo_investment:v1.0.1
```
3. Now you can access the app at `http://<your_ip>`

# Demo
![demo](/demo.gif)

# TODO
- multi-threading crawler of buff and youyou
- use front and back end separation to imporocve the performance
- add account system to record the user's data
- ...
