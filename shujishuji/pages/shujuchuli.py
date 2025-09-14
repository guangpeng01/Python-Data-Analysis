import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="机器学习模型训练平台",   
    layout="wide",    
    initial_sidebar_state="expanded"  
)

# 缓存数据加载
@st.cache_data
def load_data(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None


def data_preprocessing(df):
    """数据预处理函数"""
    st.subheader('数据预处理')
    
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = df.copy()

    
    with st.form('preprocessing_form'):   
        col1, col2 = st.columns(2)    
        
        with col1:
            columns_to_drop = st.multiselect(
                '选择要删除的列',
                st.session_state.processed_data.columns,
                
                help="选择不需要的特征列"
            )
            
        with col2:
            categorical_cols = st.session_state.processed_data.select_dtypes(
                include=['object', 'category','int']).columns.tolist()  
            columns_to_encode = st.multiselect(
                '选择要进行独热编码的列',
                categorical_cols,   
                
                help="选择分类变量进行独热编码"
            )
        
        submitted = st.form_submit_button('应用预处理') 
    
    if submitted:
        try:
            
            if columns_to_drop:    
                st.session_state.processed_data = st.session_state.processed_data.drop(
                    columns=columns_to_drop)
            
          
            if columns_to_encode:    
                st.session_state.processed_data = pd.get_dummies(
                    st.session_state.processed_data, 
                    columns=columns_to_encode, 
                    dtype=int
                )
            
            st.success("预处理完成！")
            show_correlation_matrix(st.session_state.processed_data)

            
        except Exception as e:
            st.error(f"预处理出错: {str(e)}")
    
    return st.session_state.processed_data    


def show_correlation_matrix(df):
    """显示相关性矩阵"""
    st.subheader('特征相关性矩阵')
    try:
        corr_matrix = df.corr()  
        fig, ax = plt.subplots(figsize=(10,6))   
        sns.heatmap(
            corr_matrix,    
            annot=True,    
            fmt=".2f",     
            cmap='coolwarm',  
            center=0,    
            ax=ax      
        )
        # plt.title("特征相关性热力图", pad=20)  
        st.pyplot(fig)    
    except Exception as e:
        st.warning(f"无法计算相关性矩阵: {str(e)}")


def feature_selection(df):
    """特征选择界面"""
    st.subheader('特征选择')    
    
    
    if 'selected_features' not in st.session_state:
        st.session_state.selected_features = []
    if 'selected_target' not in st.session_state:
        st.session_state.selected_target = None
    
    
    with st.form('feature_selection_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            features = st.multiselect(
                '选择特征变量',
                df.columns,
                default=st.session_state.selected_features,    
                key='feature_select'
            )
            
        with col2:
            target = st.selectbox(
                '选择目标变量',
                df.columns,
                index=df.columns.get_loc(st.session_state.selected_target) 
                if st.session_state.selected_target in df.columns else 0,
                key='target_select'
            )
        
        submitted = st.form_submit_button('确认选择')

        if submitted:
            if not features:
                st.error("❌ 请至少选择一个特征变量！")
                return None, None
            
            if target in features:
                st.error("❌ 目标变量不能同时作为特征变量！")
                return None, None
            
            try:
                st.session_state.selected_features = features
                st.session_state.selected_target = target
                
                st.success("✅ 特征选择有效！")
                return df[features].values, df[target].values
            except Exception as e:
                st.error(f"数据选择错误: {str(e)}")
                return None, None

    return None, None



def save_model(model):
    """将训练好的模型保存并提供下载按钮"""
    try:
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_{timestamp}.pkl"
        
        # 将模型序列化为字节流
        model_bytes = pickle.dumps(model)
        
        # 创建下载按钮，并添加回调函数
        if st.download_button(
            label="💾 下载训练好的模型",
            data=model_bytes,
            file_name=filename,
            mime="application/octet-stream",
            help="点击下载训练好的随机森林模型",
            on_click=clear_all  # 添加这行，点击按钮后调用clear_all
        ):
            st.success("模型下载完成，已清空会话数据")
            return True
    except Exception as e:
        st.error(f"模型保存失败: {str(e)}")
    return False



def train_random_forest(X, y):
    """训练随机森林模型（修复版）"""
    st.subheader('随机森林模型训练')
    
    
    if 'training_results' not in st.session_state:
        st.session_state.training_results = None
    
    if 'training_results' not in st.session_state:
        st.session_state.training_results = None
    try:

        st.session_state.training_results = None    
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 训练模型
        model = RandomForestClassifier(
            # n_estimators=100,
            # max_depth=3,
            # random_state=42,
            # n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = model.predict(X_test)
        results = {
            'model': model,
            'accuracy': accuracy_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'features': X.shape[1]
        }
        
        # 保存结果
        st.session_state.training_results = results
        st.session_state.model = model

        pkl_filename = "moxing02.pkl"
        with open(pkl_filename,'wb') as file:
            pickle.dump(st.session_state.model,file)
        st.write('保存成功')

        
    except Exception as e:
        st.error(f"训练异常: {str(e)}")
    
    # 自动显示训练结果
    if st.session_state.training_results:
        results = st.session_state.training_results
        st.success(f"训练完成！特征数: {results['features']}")
        
        # 使用选项卡展示结果
        tab1, tab2 = st.tabs(["📊 指标", "📋 混淆矩阵"])
        
        with tab1:
            col1, col2 = st.columns(2)
            col1.metric("准确率", f"{results['accuracy']:.4f}")
            col2.metric("F1分数", f"{results['f1']:.4f}")
            
        with tab2:
            st.dataframe(pd.DataFrame(
                results['confusion_matrix'],
                columns=["预测负类", "预测正类"],
                index=["真实负类", "真实正类"]
            ))
        save_model(results['model'])  # 替换原来的保存代码
    return None

def clear_all():
    """清空会话状态和缓存"""
    # 清空会话状态
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # 清空缓存（如果有使用）
    st.cache_data.clear()
    st.cache_resource.clear()
    

def main():
    st.title("🎯 机器学习模型训练平台")   
    # st.sidebar.title("导航")    
    
    uploaded_file = st.file_uploader(
        "上传CSV文件",
        type=["csv"],
        help="请上传包含训练数据的CSV文件"
    )
    # clear_all()
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            with st.expander("🔍 查看原始数据", expanded=True):
                st.dataframe(df)
            

            df_processed = data_preprocessing(df)

            if df_processed is not None:
                # 特征选择
                X, y = feature_selection(df_processed)
                
                if X is not None and y is not None:
                    # 模型训练
                    train_random_forest(X, y)
                    clear_all()
    # return None                


if __name__ == "__main__":
    main()
    









