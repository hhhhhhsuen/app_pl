import base64
import streamlit as st
import pandas as pd
import os
import io
import requests
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

# 设置页面配置
st.set_page_config(page_title="app评论查询工具v1.0-ShuaiSuen", page_icon=":mag:", layout="wide")

# 标题
st.title('app评论查询工具v1.0-ShuaiSuen')

# 获取关键词输入
keyword = st.text_input('请输入要检索的关键词：')

# 配置腾讯云COS连接参数
secret_id = 'AKIDBMTRErJi284tXijeO4WO8g172mKfAWgg'
secret_key = 'rZ6PTvITSEmwrfGeplTxDG4dz95oSwJS'
region = 'ap-beijing'
bucket = 'appdate01-1259110268'
cos_config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
cos_client = CosS3Client(cos_config)

def load_data(cos_path):
    # 从腾讯云COS下载文件到内存
    file_data = cos_client.get_object(Bucket=bucket, Key=cos_path)["Body"].get_raw_stream().read()
    return pd.read_excel(io.BytesIO(file_data), engine='openpyxl')

# 使用从腾讯云COS获取的文件路径调用 load_data 函数
cos_path = 'str_pl/test.xlsx'
df = load_data(cos_path)

# 省略其他部分，例如提供下载链接的函数、下载原始数据、搜索按钮等

# 提供下载链接的函数
def get_download_link(df, filename, file_format):
    if file_format == 'csv':
        towrite = io.StringIO()
        df.to_csv(towrite, index=False, encoding="utf-8-sig", header=True)
        towrite.seek(0)
        b64 = base64.b64encode(towrite.getvalue().encode()).decode()
    elif file_format == 'xlsx':
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, encoding="utf-8-sig", header=True, engine='openpyxl')
        towrite.seek(0)
        b64 = base64.b64encode(towrite.read()).decode()

    href = f'<a href="data:file/{file_format};base64,{b64}" download="{filename}">点击下载{filename}</a>'
    return href


# 下载原始数据
st.markdown(get_download_link(df, "原始数据.xlsx", "xlsx"), unsafe_allow_html=True)

# 搜索按钮
if st.button('搜索'):
    # 过滤结果
    result = df[df.apply(lambda x: x.astype(str).str.contains(keyword, case=False).any(), axis=1)]

    # 显示结果统计
    total_count = len(df)
    keyword_count = len(result)
    keyword_percentage = round(keyword_count / total_count, 4)
    st.write(
        f"数据中共有 {total_count} 条记录，其中包含关键词 '{keyword}' 的记录有 {keyword_count} 条，占比为 {keyword_percentage}")

    if result.empty:
        st.warning('没有找到相关结果')
    else:
        st.markdown('**搜索结果：**')
        st.write(result.head(20))  # 只显示前20条结果

        # 下载搜索结果
        st.markdown(get_download_link(result, "搜索结果.csv", "csv"), unsafe_allow_html=True)

