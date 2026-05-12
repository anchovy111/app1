"""
电商销售数据分析 - Streamlit云端版
=======================================
使用Streamlit创建交互式Web应用

运行方式：
1. 安装依赖：pip install streamlit pandas numpy
2. 运行：streamlit run streamlit_电商分析.py
3. 浏览器打开：http://localhost:8501

部署到云端：
- Streamlit Community Cloud（免费）
- 其他平台（Heroku, AWS, GCP等）
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="电商销售数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ===== 页面标题 =====
st.title("📊 电商销售数据分析平台")
st.markdown("---")

# ===== 侧边栏 =====
st.sidebar.title("🎛️ 控制面板")
st.sidebar.markdown("---")

# ===== 1. 数据生成 =====
@st.cache_data
def generate_data():
    """生成模拟数据，使用缓存加速"""
    np.random.seed(42)
    
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    
    products = {
        '手机': {'价格': [2999, 3999, 4999, 5999], '类别': '数码'},
        '电脑': {'价格': [4599, 5999, 7999, 9999], '类别': '数码'},
        '耳机': {'价格': [199, 299, 499, 799], '类别': '数码'},
        '平板': {'价格': [2499, 3499, 4499], '类别': '数码'},
        'T恤': {'价格': [59, 99, 159], '类别': '服装'},
        '牛仔裤': {'价格': [129, 199, 299], '类别': '服装'},
        '运动鞋': {'价格': [299, 499, 699], '类别': '服装'},
        '面膜': {'价格': [49, 99, 149], '类别': '美妆'},
        '口红': {'价格': [129, 199, 299], '类别': '美妆'},
        '洗发水': {'价格': [39, 69, 99], '类别': '美妆'},
    }
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '南京', '重庆']
    customer_ids = range(1001, 2001)
    
    n_records = 5000
    data = []
    
    for i in range(n_records):
        date = np.random.choice(dates)
        # 确保date是Python datetime对象
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y%m%d')
        else:
            # 如果是numpy datetime，转成Python datetime
            date_str = pd.Timestamp(date).strftime('%Y%m%d')
        product = np.random.choice(list(products.keys()))
        customer = np.random.choice(customer_ids)
        city = np.random.choice(cities)
        price = np.random.choice(products[product]['价格'])
        quantity = np.random.choice([1, 1, 1, 2, 3])
        discount = np.random.choice([1.0, 0.95, 0.9, 0.85], p=[0.5, 0.25, 0.15, 0.1])
        amount = price * quantity * discount
        order_id = f"ORD{date_str}{i:04d}"
        
        data.append({
            '订单ID': order_id,
            '订单日期': date,
            '客户ID': customer,
            '产品名称': product,
            '产品类别': products[product]['类别'],
            '城市': city,
            '单价': price,
            '数量': quantity,
            '折扣': discount,
            '订单金额': round(amount, 2)
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('订单日期').reset_index(drop=True)
    return df

# 加载数据
with st.spinner('正在加载数据...'):
    df = generate_data()

df['月份'] = df['订单日期'].dt.month
df['星期'] = df['订单日期'].dt.dayofweek
df['是否周末'] = df['星期'].isin([5, 6])

# ===== 2. 侧边栏筛选 =====
st.sidebar.subheader("📅 日期范围筛选")
min_date = df['订单日期'].min()
max_date = df['订单日期'].max()
start_date = st.sidebar.date_input(
    "开始日期",
    min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "结束日期",
    max_date,
    min_value=min_date,
    max_value=max_date
)

st.sidebar.subheader("🏷️ 产品筛选")
selected_products = st.sidebar.multiselect(
    "选择产品（默认全选）",
    options=df['产品名称'].unique(),
    default=df['产品名称'].unique()
)

st.sidebar.subheader("🗺️ 城市筛选")
selected_cities = st.sidebar.multiselect(
    "选择城市（默认全选）",
    options=df['城市'].unique(),
    default=df['城市'].unique()
)

# 应用筛选
mask = (
    (df['订单日期'] >= pd.to_datetime(start_date)) &
    (df['订单日期'] <= pd.to_datetime(end_date)) &
    (df['产品名称'].isin(selected_products)) &
    (df['城市'].isin(selected_cities))
)
filtered_df = df[mask].copy()

st.sidebar.success(f"筛选后共 {len(filtered_df)} 条记录")

# ===== 3. 主页面 - 关键指标卡片 =====
st.subheader("📈 核心指标概览")

col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df['订单金额'].sum()
total_orders = len(filtered_df)
total_customers = filtered_df['客户ID'].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

with col1:
    st.metric("💰 总销售额", f"¥{total_sales:,.2f}")
with col2:
    st.metric("📦 总订单数", f"{total_orders:,} 笔")
with col3:
    st.metric("👥 活跃客户", f"{total_customers:,} 人")
with col4:
    st.metric("🛒 平均客单价", f"¥{avg_order_value:.2f}")

st.markdown("---")

# ===== 4. 图表展示 =====
# 准备数据
monthly = filtered_df.groupby('月份')['订单金额'].sum()
product_sales = filtered_df.groupby('产品名称')['订单金额'].sum().sort_values(ascending=False)
category_sales = filtered_df.groupby('产品类别')['订单金额'].sum().sort_values(ascending=False)
city_sales = filtered_df.groupby('城市')['订单金额'].sum().sort_values(ascending=False)

# 图表布局
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 销售趋势", "🏷️ 产品分析", "🗺️ 城市分析", "⏰ 时间分析", "📋 数据表格"])

# ===== 标签页1：销售趋势 =====
with tab1:
    st.subheader("月度销售趋势")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly.index, monthly.values, marker='o', linewidth=3, markersize=8, color='#2E86AB')
    ax.fill_between(monthly.index, monthly.values, alpha=0.3, color='#2E86AB')
    ax.set_title('月度销售趋势', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('月份', fontsize=11)
    ax.set_ylabel('销售额 (元)', fontsize=11)
    ax.set_xticks(range(1, 13))
    ax.grid(True, alpha=0.3, linestyle='--')
    
    for i, v in enumerate(monthly.values):
        ax.text(monthly.index[i], v + (monthly.max() * 0.01), 
                f'¥{v/10000:.1f}万', ha='center', va='bottom', fontsize=9)
    
    st.pyplot(fig)

# ===== 标签页2：产品分析 =====
with tab2:
    col_prod1, col_prod2 = st.columns(2)
    
    with col_prod1:
        st.subheader("产品销售额TOP10")
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(product_sales)))
        bars = ax.barh(product_sales.index[::-1], product_sales.values[::-1], color=colors[::-1])
        ax.set_title('产品销售额排行', fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('销售额 (元)', fontsize=10)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        st.pyplot(fig)
    
    with col_prod2:
        st.subheader("产品类别占比")
        fig, ax = plt.subplots(figsize=(8, 5))
        colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        explode = [0.05] * len(category_sales)
        wedges, texts, autotexts = ax.pie(category_sales.values,
                                           labels=category_sales.index,
                                           autopct='%1.1f%%',
                                           colors=colors_pie,
                                           explode=explode,
                                           shadow=True,
                                           startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax.set_title('产品类别占比', fontsize=13, fontweight='bold', pad=10)
        st.pyplot(fig)

# ===== 标签页3：城市分析 =====
with tab3:
    st.subheader("城市销售排名TOP5")
    
    top5 = city_sales.head(5)
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ['#E74C3C', '#E67E22', '#F1C40F', '#2ECC71', '#3498DB']
    bars = ax.bar(top5.index, top5.values, color=colors, edgecolor='white', linewidth=2)
    ax.set_title('城市销售排名 TOP5', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('城市', fontsize=11)
    ax.set_ylabel('销售额 (元)', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + (top5.max() * 0.01),
                f'¥{height/10000:.1f}万', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    st.pyplot(fig)

# ===== 标签页4：时间分析 =====
with tab4:
    st.subheader("工作日 vs 周末 销售对比")
    
    weekday_sales = filtered_df.groupby('是否周末')['订单金额'].agg(['sum', 'mean'])
    
    fig, ax = plt.subplots(figsize=(10, 4))
    labels = ['工作日', '周末']
    x = np.arange(2)
    width = 0.35
    
    bars1 = ax.bar(x - width/2, [weekday_sales.loc[False, 'sum']/10000, weekday_sales.loc[True, 'sum']/10000], 
                   width, label='总销售额 (万元)', color='#3498DB', edgecolor='white', linewidth=2)
    bars2 = ax.bar(x + width/2, [weekday_sales.loc[False, 'mean'], weekday_sales.loc[True, 'mean']], 
                   width, label='平均客单价', color='#E74C3C', edgecolor='white', linewidth=2)
    
    ax.set_title('工作日 vs 周末对比', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('时间类型', fontsize=11)
    ax.set_ylabel('金额', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    st.pyplot(fig)

# ===== 标签页5：数据表格 =====
with tab5:
    st.subheader("原始数据")
    
    # 显示数据
    st.dataframe(filtered_df[['订单ID', '订单日期', '产品名称', '城市', '单价', '数量', '订单金额']], 
                 use_container_width=True)
    
    # 下载数据按钮
    csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "📥 下载数据 (CSV)",
        csv,
        "电商销售数据.csv",
        "text/csv"
    )

# ===== 页脚 =====
st.markdown("---")
st.caption(f"数据生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("📊 电商销售数据分析平台 - 基于Streamlit")
