"""
电商销售数据分析 - Streamlit云端版（中文友好版）
================================================
使用Plotly替代matplotlib，中文显示更好

运行方式：
1. 安装依赖：pip install streamlit pandas numpy plotly
2. 运行：streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 页面标题 =====
st.title("📊 电商销售数据分析平台")
st.markdown("---")

# ===== 侧边栏 =====
st.sidebar.title("🎛️ 控制面板")
st.sidebar.markdown("---")

# ===== 1. 数据上传与生成 =====
@st.cache_data
def generate_data():
    """生成模拟数据，使用缓存加速"""
    np.random.seed(42)
    
    dates_list = []
    start_date = datetime(2024, 1, 1)
    for i in range(366):
        dates_list.append(start_date + timedelta(days=i))
    
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
    customer_ids = list(range(1001, 2001))
    
    n_records = 5000
    data = []
    
    for i in range(n_records):
        date_idx = np.random.randint(0, len(dates_list))
        date = dates_list[date_idx]
        product = np.random.choice(list(products.keys()))
        customer = np.random.choice(customer_ids)
        city = np.random.choice(cities)
        price = np.random.choice(products[product]['价格'])
        quantity = np.random.choice([1, 1, 1, 2, 3])
        discount = np.random.choice([1.0, 0.95, 0.9, 0.85], p=[0.5, 0.25, 0.15, 0.1])
        amount = price * quantity * discount
        order_id = f"ORD{date.strftime('%Y%m%d')}{i:04d}"
        
        data.append({
            '订单ID': order_id,
            '订单日期': date,
            '客户ID': int(customer),
            '产品名称': product,
            '产品类别': products[product]['类别'],
            '城市': city,
            '单价': int(price),
            '数量': int(quantity),
            '折扣': float(discount),
            '订单金额': round(amount, 2)
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('订单日期').reset_index(drop=True)
    return df

def load_uploaded_data(uploaded_file):
    """加载上传的数据文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("不支持的文件格式！请上传CSV或Excel文件")
            return None
        
        # 检查必要的列
        required_columns = ['订单日期', '订单金额']
        if not all(col in df.columns for col in required_columns):
            st.warning(f"数据缺少必要列，期望列: {required_columns}")
        
        # 尝试转换日期列
        if '订单日期' in df.columns:
            df['订单日期'] = pd.to_datetime(df['订单日期'], errors='coerce')
        
        # 尝试转换数值列
        numeric_cols = ['订单金额', '单价', '数量', '折扣']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna().reset_index(drop=True)
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return None

# ===== 数据上传区域 =====
st.sidebar.subheader("📁 数据上传")
uploaded_file = st.sidebar.file_uploader(
    "上传CSV或Excel文件",
    type=['csv', 'xlsx', 'xls'],
    help="上传您的销售数据文件，支持CSV和Excel格式"
)

# 加载数据
with st.spinner('正在加载数据...'):
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file)
        if df is not None:
            st.sidebar.success(f"✅ 成功加载 {len(df)} 条数据")
        else:
            df = generate_data()
            st.sidebar.info("使用模拟数据")
    else:
        df = generate_data()
        st.sidebar.info("📊 使用模拟数据（上传文件可替换）")

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
    options=list(df['产品名称'].unique()),
    default=list(df['产品名称'].unique())
)

st.sidebar.subheader("🗺️ 城市筛选")
selected_cities = st.sidebar.multiselect(
    "选择城市（默认全选）",
    options=list(df['城市'].unique()),
    default=list(df['城市'].unique())
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
monthly = filtered_df.groupby('月份')['订单金额'].sum().reset_index()
monthly['月份'] = monthly['月份'].astype(str) + '月'

product_sales = filtered_df.groupby('产品名称')['订单金额'].sum().sort_values(ascending=False).reset_index()
category_sales = filtered_df.groupby('产品类别')['订单金额'].sum().sort_values(ascending=False).reset_index()
city_sales = filtered_df.groupby('城市')['订单金额'].sum().sort_values(ascending=False).head(5).reset_index()

# 图表布局
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 销售趋势", "🏷️ 产品分析", "🗺️ 城市分析", "⏰ 时间分析", "📋 数据表格"])

# ===== 标签页1：销售趋势 =====
with tab1:
    st.subheader("月度销售趋势")
    
    fig = px.line(
        monthly, 
        x='月份', 
        y='订单金额',
        markers=True,
        title='Monthly Sales Trend'
    )
    fig.update_traces(line=dict(color='#2E86AB', width=3), marker=dict(size=10))
    fig.update_layout(
        xaxis_title="月份 (Month)",
        yaxis_title="销售额 (Sales Amount)",
        template='plotly_white',
        height=400
    )
    fig.add_trace(px.area(monthly, x='月份', y='订单金额').data[0])
    
    st.plotly_chart(fig, width='stretch')

# ===== 标签页2：产品分析 =====
with tab2:
    col_prod1, col_prod2 = st.columns(2)
    
    with col_prod1:
        st.subheader("产品销售额TOP10")
        
        fig = px.bar(
            product_sales,
            y='产品名称',
            x='订单金额',
            orientation='h',
            title='Product Sales Ranking'
        )
        fig.update_layout(
            yaxis_title="产品 (Product)",
            xaxis_title="销售额 (Sales Amount)",
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, width='stretch')
    
    with col_prod2:
        st.subheader("产品类别占比")
        
        fig = px.pie(
            category_sales,
            values='订单金额',
            names='产品类别',
            title='Sales by Category'
        )
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, width='stretch')

# ===== 标签页3：城市分析 =====
with tab3:
    st.subheader("城市销售排名TOP5")
    
    fig = px.bar(
        city_sales,
        x='城市',
        y='订单金额',
        title='Top 5 Cities by Sales',
        color='订单金额',
        color_continuous_scale='Reds'
    )
    fig.update_layout(
        xaxis_title="城市 (City)",
        yaxis_title="销售额 (Sales Amount)",
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig, width='stretch')

# ===== 标签页4：时间分析 =====
with tab4:
    st.subheader("工作日 vs 周末 销售对比")
    
    weekday_sales = filtered_df.groupby('是否周末')['订单金额'].agg(['sum', 'mean']).reset_index()
    weekday_sales['类型'] = weekday_sales['是否周末'].map({False: '工作日 (Weekday)', True: '周末 (Weekend)'})
    
    col_week1, col_week2 = st.columns(2)
    
    with col_week1:
        st.write("**总销售额对比**")
        fig = px.bar(
            weekday_sales,
            x='类型',
            y='sum',
            title='Total Sales: Weekday vs Weekend',
            color='类型',
            color_discrete_map={'工作日 (Weekday)': '#3498DB', '周末 (Weekend)': '#E74C3C'}
        )
        fig.update_layout(template='plotly_white', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch')
    
    with col_week2:
        st.write("**平均客单价对比**")
        fig = px.bar(
            weekday_sales,
            x='类型',
            y='mean',
            title='Average Order Value: Weekday vs Weekend',
            color='类型',
            color_discrete_map={'工作日 (Weekday)': '#3498DB', '周末 (Weekend)': '#E74C3C'}
        )
        fig.update_layout(template='plotly_white', height=350, showlegend=False)
        st.plotly_chart(fig, width='stretch')

# ===== 标签页5：数据表格 =====
with tab5:
    st.subheader("原始数据")
    
    # 显示数据
    st.dataframe(filtered_df[['订单ID', '订单日期', '产品名称', '城市', '单价', '数量', '订单金额']], 
                 width='stretch')
    
    # ===== 数据下载区域 =====
    st.subheader("📥 数据下载")
    
    col_dl1, col_dl2,col_dl3 = st.columns(3)
    
    with col_dl1:
        # 下载CSV文件 - UTF-8-BOM编码
        csv_data = filtered_df[['订单ID', '订单日期', '产品名称', '城市', '单价', '数量', '订单金额']].copy()
        csv_data['订单日期'] = csv_data['订单日期'].dt.strftime('%Y-%m-%d')
        csv_bytes = csv_data.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📄 下载CSV文件",
            data=csv_bytes,
            file_name="电商销售数据_2024.csv",
            mime="text/csv",
            help="推荐使用，支持Excel直接打开"
        )
    
    with col_dl2:
        # 下载Excel文件（推荐，中文无乱码）
        excel_buffer = BytesIO()
        excel_data = filtered_df[['订单ID', '订单日期', '产品名称', '城市', '单价', '数量', '订单金额']].copy()
        excel_data['订单日期'] = excel_data['订单日期'].dt.strftime('%Y-%m-%d')
        excel_data.to_excel(excel_buffer, index=False, sheet_name='销售数据', engine='openpyxl')
        excel_bytes = excel_buffer.getvalue()
        
        st.download_button(
            label="📊 下载Excel文件",
            data=excel_bytes,
            file_name="电商销售数据_2024.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="推荐！中文显示完美，无需设置编码"
        )
    with col_dl3:
        # 下载Excel文件（推荐，中文无乱码）
        excel_buffer = BytesIO()
        
        df.to_excel(excel_buffer, index=False, sheet_name='销售数据', engine='openpyxl')
        excel_bytes = excel_buffer.getvalue()
        
        st.download_button(
            label="📊 下载Excel_Raw文件",
            data=excel_bytes,
            file_name="电商销售数据.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="推荐！中文显示完美，无需设置编码"
        )
    st.caption("💡 Excel格式推荐：完全支持中文，无需任何设置")

# ===== 页脚 =====
st.markdown("---")
st.caption(f"数据生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("📊 电商销售数据分析平台 - Powered by Streamlit & Plotly")
