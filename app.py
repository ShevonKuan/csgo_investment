import functools
from pathlib import Path

from api import Goods, Inventory
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid import DataReturnMode, GridUpdateMode
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import streamlit_echarts


def delete_goods(inventory, index):
    for i in index:
        inventory.delete(i['库存编号'])


def sell_goods(inventory, index):
    for i in index:
        try:
            inventory()[i['库存编号']].sell(eval(i['卖出价格']))
        except:
            st.error("卖出价格输入错误，请检查输入")

def lease_goods(inventory, index):
    for i in index:
        inventory()[i['库存编号']].lease()


def back_goods(inventory, index):
    for i in index:
        inventory()[i['库存编号']].back()


def edit_cost(inventory, index, cost):
    for index, i in enumerate(index):
        inventory()[i].cost = cost[index]


def open_inventory(path):
    with st.spinner("加载库存中..."):
        st.session_state.inventory = Inventory(path)
        st.success("库存已打开 ✅")
    with st.spinner("更新饰品信息..."):
        progress_bar = st.progress(0)
        rate = 1 / len(st.session_state.inventory())
        for p, i in enumerate(st.session_state.inventory):
            progress_bar.progress(rate * p)
            st.session_state.inventory()[i].refresh()
        progress_bar.empty()


def save_inventory(path):
    with st.spinner("保存库存中..."):
        st.session_state.inventory.save()
        st.success("库存保存成功 ✅")


cellsytle_jscode = JsCode(
    """
function (params) {
        if (params.value < 0) {
            return {
                'color': 'white',
                'backgroundColor': 'forestgreen'
            }
        } else {
            return {
                'color': 'white',
                'backgroundColor': 'crimson'
            }
        } 
    };
    """
)


def main() -> None:
    st.header("CSGO 饰品投资追踪 :moneybag: :dollar: :bar_chart:")
    st.caption("Made by Shevon & Lishuai")
    st.text("请在左侧打开库存文件")
    with st.sidebar:
        st.subheader("选择库存")
        path = st.text_input("库存文件路径", value="./data.pkl")
        launch = st.button('新建或打开库存', on_click=open_inventory, args=(path,))
        save = st.button('保存库存更改', on_click=save_inventory, args=(path,))
        if 'inventory' in st.session_state:
            st.caption('目前已启动库存 ' + st.session_state.inventory.path)
            st.subheader("添加饰品")
            form_track = st.form(key="track")
            with form_track:
                code = st.text_input("请输入饰品buff代码")
                cost = eval(st.text_input("请输入购买价格，0表示仅观望", "0"))
                submitted = st.form_submit_button(label="添加")
            if submitted:
                with st.spinner("加载饰品信息..."):
                    try:
                        tmp = Goods(code, cost)
                        tmp.refresh()
                        st.session_state.inventory.add(tmp)
                        st.success(tmp.name + "已添加 ✅")
                    except:
                        st.error("饰品信息加载失败，请检查代码是否正确")

    if 'inventory' in st.session_state:
        st.subheader("投资信息")
        if len(st.session_state.inventory()) > 0:
            col = st.columns(4)
            col2 = st.columns(4)
            col3 = st.columns(4)
            col[0].metric(
                "总投资额", value=f"{st.session_state.inventory.total_cost():.2f} 元"
            )
            col[1].metric("追踪总量", value=f"{len(st.session_state.inventory())} 件")
            col[2].metric(
                "库存价值(Buff计,含租出)",
                value=f"{st.session_state.inventory.calc_price():.2f} 元",
            )
            col[3].metric(
                "总套现", value=f"{st.session_state.inventory.sell_price():.2f} 元"
            )
            earn = (
                st.session_state.inventory.calc_price()
                + st.session_state.inventory.sell_price()
                - st.session_state.inventory.total_cost()
            )
            col2[0].metric("盈利(Buff计)", value=f"{earn:.2f} 元")
            col2[1].metric(
                "总收益率",
                value=f"{earn/st.session_state.inventory.total_cost()*100:.2f} %",
            )
            yyyp_earn = (
                st.session_state.inventory.calc_yyyp_price()
                + st.session_state.inventory.sell_price()
                - st.session_state.inventory.total_cost()
            )
            col2[2].metric("盈利(悠悠有品计)", value=f"{yyyp_earn:.2f} 元")
            col2[3].metric(
                "总收益率",
                value=f"{yyyp_earn/st.session_state.inventory.total_cost()*100:.2f} %",
            )
            col3[0].metric(
                "持有饰品收益(Buff计)",
                value=f"{st.session_state.inventory.calc_price() - st.session_state.inventory.total_cost_in_inventory():.2f} 元",
            )
            col3[1].metric(
                "持有饰品收益率(Buff计)",
                value=f"{100 * (st.session_state.inventory.calc_price() - st.session_state.inventory.total_cost_in_inventory())/st.session_state.inventory.total_cost_in_inventory():.2f} %",
            )
            col3[2].metric(
                "持有饰品收益(悠悠有品计)",
                value=f"{st.session_state.inventory.calc_yyyp_price() - st.session_state.inventory.total_cost_in_inventory():.2f} 元",
            )
            col3[3].metric(
                "持有饰品收益率(悠悠有品计)",
                value=f"{100 * (st.session_state.inventory.calc_yyyp_price() - st.session_state.inventory.total_cost_in_inventory())/st.session_state.inventory.total_cost_in_inventory():.2f} %",
            )

            # col[0].metric(
            #     "总投资额", value=f"{st.session_state.inventory.total_cost():.2f} 元"
            # )
            # col[1].metric(
            #     "库存理论收益(Buff计)",
            #     value=f"{st.session_state.inventory.calc_buff_earn():.2f} 元",
            # )
            # col[2].metric(
            #     "库存理论收益率(Buff计)",
            #     value=f"{st.session_state.inventory.calc_buff_earn_rate():.2f} %",
            # )
            # col[3].metric(
            #     "库存理论收益(悠悠有品计)",
            #     value=f"{st.session_state.inventory.calc_youpin_earn():.2f} 元",
            # )
            # col2 = st.columns(4)
            # col2[0].metric(
            #     "库存理论收益率(悠悠有品计)",
            #     value=f"{st.session_state.inventory.calc_youpin_earn_rate():.2f} %",
            # )
            # col2[1].metric("追踪总量", value=f"{len(st.session_state.inventory())} 件")
            # col2[2].metric(
            #     "库存价值(Buff计,含租出)",
            #     value=f"{st.session_state.inventory.calc_price():.2f} 元",
            # )
            # col2[3].metric(
            #     "总套现", value=f"{st.session_state.inventory.sell_price():.2f} 元"
            # )
            # col3 = st.columns(4)
            # earn = (
            #     st.session_state.inventory.calc_price()
            #     + st.session_state.inventory.sell_price()
            #     - st.session_state.inventory.total_cost()
            # )
            # col3[0].metric("盈利(库存价值+卖出收益-总投入)", value=f"{earn:.2f} 元")
            # col3[1].metric(
            #     "总收益率",
            #     value=f"{earn/st.session_state.inventory.total_cost()*100:.2f} %",
            # )
            st.subheader("目前资金组成")
            col4 = st.columns(2)
            with col4[0]:
                fig1 = Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS)).add(
                    "库存资金组成",
                    [('出租',sum(
                            [
                                st.session_state.inventory()[good].price
                                for good in st.session_state.inventory()
                                if st.session_state.inventory()[good].status == 1
                            ]
                        )), 
                     ('在库',sum(
                            [
                                st.session_state.inventory()[good].price
                                for good in st.session_state.inventory()
                                if (
                                    st.session_state.inventory()[good].status == 0
                                    and st.session_state.inventory()[good].cost != 0
                                )
                            ]
                        ))],
                    radius=["30%", "75%"],
                )
                streamlit_echarts.st_pyecharts(fig1, height="400px", key="fig1")
            with col4[1]:
                fig2 = Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS)).add(
                    "盈利资金组成",
                    [('库存增值',st.session_state.inventory.calc_price()
                        - st.session_state.inventory.total_cost_in_inventory(),), ('卖出收益',st.session_state.inventory.sell_earn(),)],
                    radius=["30%", "75%"],
                )
                streamlit_echarts.st_pyecharts(fig2, height="400px", key="fig2")
        else:
            st.caption("当前库存为空")
        # 追踪列表
        st.subheader("追踪列表")

        if len(st.session_state.inventory()) > 0:
            data = pd.DataFrame(
                columns=['库存编号', 'Buff id', '名称', '状态', '购入花费(元)(双击修改)', '卖出价格']
            )
            for xx in st.session_state.inventory:
                xx = st.session_state.inventory()[xx]
                data.loc[len(data)] = [
                    xx.index,
                    xx.id,
                    xx.name,
                    xx.get_status(),
                    xx.cost,
                    xx.sell_price,
                ]

            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_columns(['购入花费(元)(双击修改)', '卖出价格'], editable=True)
            gb.configure_selection(
                selection_mode='multiple',
                use_checkbox=True,
            )
            gb.configure_side_bar()
            gb.configure_grid_options(domLayout='normal')
            gridOptions = gb.build()
            grid = AgGrid(
                data,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                return_mode_value=DataReturnMode.FILTERED,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                enable_enterprise_modules=True,
            )
            selected = grid["selected_rows"]
            if selected != []:
                print(selected)
                st.button(
                    '删除选中饰品',
                    on_click=delete_goods,
                    args=(st.session_state.inventory, selected),
                )
                st.button(
                    '出售选中饰品',
                    on_click=sell_goods,
                    args=(st.session_state.inventory, selected),
                )
                st.button(
                    '租出选中饰品',
                    on_click=lease_goods,
                    args=(st.session_state.inventory, selected),
                )
                st.button(
                    '回仓选中饰品',
                    on_click=back_goods,
                    args=(st.session_state.inventory, selected),
                )
            edit_cost(
                st.session_state.inventory,
                list(grid['data']['库存编号']),
                list(grid['data']['购入花费(元)(双击修改)']),
            )
        else:
            st.caption("暂无饰品记录")

        goods = [st.session_state.inventory()[xx] for xx in st.session_state.inventory]
        # 已购列表
        st.subheader("已购列表")
        track = [xx for xx in goods if xx.cost != 0]
        if len(track) > 0:
            data_track = pd.DataFrame([xx() for xx in track])
            data_track['Status'] = data_track['Status'].map(
                {0: '在库中', 1: '已租出', 2: '已卖出'}
            )

            data_track.columns = [
                'Buff id',
                '有品 id',
                '名称',
                '购入花费(元)',
                'Buff 价格',
                '有品价格',
                'Steam 价格(元)',
                '状态',
                '有品在售',
                '有品在租',
                '短租价格(元)',
                '长租价格(元)',
                '押金(元)',
                '租售比',
                '理论目前收益(元)',
                '理论目前收益率(%)',
                '租金比例(%)',
                '押金比例(%)',
                '年化短租比例(%)',
                '年化长租比例(%)',
                '套现比例(%)',
                'buff和有品价格比例',
            ]
            data_track = data_track.round(4)
            del data_track['Buff id']
            del data_track['有品 id']
            gb0 = GridOptionsBuilder.from_dataframe(data_track)
            gb0.configure_columns(["Buff id", "有品 id", "名称"], pinned=True)
            gb0.configure_columns(
                ['理论目前收益(元)', '理论目前收益率(%)'],
                cellStyle=cellsytle_jscode,
            )
            gb0.configure_side_bar()
            gb0.configure_grid_options(domLayout='normal')

            gridOptions = gb0.build()
            grid_track = AgGrid(
                data_track,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=True,
            )
            st.subheader("理论收益分析")
            # Plot
            x = data_track.sort_values(
                by='理论目前收益率(%)',
            )['名称'].tolist()
            y1 = data_track.sort_values(
                by='理论目前收益率(%)',
            )['理论目前收益率(%)'].tolist()
            y2 = data_track.sort_values(
                by='理论目前收益率(%)',
            )['理论目前收益(元)'].tolist()
            fig0 = (
                Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
                .add_xaxis(x)
                .add_yaxis("理论目前收益率(%)", y1)
                .add_yaxis("理论目前收益(元)", y2)
                .reversal_axis()
                .set_global_opts(
                    # 设置操作图表缩放功能，orient="vertical" 为Y轴 滑动
                    datazoom_opts=[
                        opts.DataZoomOpts(),
                        opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
                        opts.DataZoomOpts(
                            orient="vertical",
                            range_start=0,
                            range_end=100,
                        ),
                    ],
                )
                # .render("bar_datazoom_both.html")
            )

            streamlit_echarts.st_pyecharts(fig0, height="900px", key="fig0")

        else:
            st.caption("暂无已购饰品")

        # 观望列表
        st.subheader("观望列表")
        observe = [xx for xx in goods if xx.cost == 0]
        if len(observe) > 0:
            data_observe = pd.DataFrame([xx() for xx in observe])
            del data_observe['Cost']
            data_observe['Status'] = data_observe['Status'].map({0: '观望中'})

            data_observe.columns = [
                'Buff id',
                '有品 id',
                '名称',
                'Buff 价格(元)',
                '有品价格(元)',
                'Steam 价格(元)',
                '状态',
                '有品在售',
                '有品在租',
                '短租价格(元)',
                '长租价格(元)',
                '押金',
                '租售比',
                '租金比例(%)',
                '押金比例(%)',
                '年化短租比例(%)',
                '年化长租比例(%)',
                '套现比例(%)',
                'buff和有品价格比例',
            ]
            data_observe = data_observe.round(4)
            del data_observe['Buff id']
            del data_observe['有品 id']
            gb1 = GridOptionsBuilder.from_dataframe(data_observe)
            gb1.configure_columns(["Buff id", "有品 id", "名称"], pinned=True)
            gb1.configure_side_bar()
            gb1.configure_grid_options(domLayout='normal')

            gridOptions = gb1.build()
            grid_observe = AgGrid(
                data_observe,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=True,
            )

        else:
            st.caption("暂无观望饰品")


if __name__ == "__main__":
    st.set_page_config(
        "CSGO 饰品投资追踪",
        "💰",
        layout="wide",
    )
    main()
