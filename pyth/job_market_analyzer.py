"""
JOB MARKET TREND ANALYZER
A complete Data Science portfolio project analyzing DS job market trends

By: Abhisar Sharma
Technologies: Streamlit, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Job Market Trend Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5em;
        border-radius: 10px;
        margin: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# PHASE 0: SAMPLE DATA GENERATION (Simulating Web Scraping)
# ============================================================================
@st.cache_data
def generate_sample_job_data(n_jobs=500):
    """
    Simulate scraped job data. In real world, this would come from:
    - BeautifulSoup scraping LinkedIn/Indeed
    - APIs from job platforms
    
    This represents ~500 DS job postings
    """
    np.random.seed(42)
    
    job_titles = ['Data Scientist', 'Senior Data Scientist', 'Data Analyst', 
                  'ML Engineer', 'Analytics Engineer', 'Data Engineer']
    
    companies = ['Google', 'Amazon', 'Microsoft', 'Apple', 'Meta', 'Tesla', 
                 'Goldman Sachs', 'JP Morgan', 'Accenture', 'Deloitte',
                 'IBM', 'Intel', 'Oracle', 'Salesforce', 'Adobe', 'Stripe']
    
    locations = ['India', 'USA', 'UK', 'Canada', 'Germany', 'Singapore', 'Australia']
    
    # Raw job descriptions (simulated)
    job_descriptions = [
        "Python, SQL, Machine Learning, Statistical Analysis, Tableau, Data Visualization",
        "Java, Python, Big Data, Hadoop, Spark, AWS, Cloud Computing",
        "SQL, Python, R, Statistics, Tableau, Power BI, Business Intelligence",
        "Deep Learning, TensorFlow, PyTorch, Computer Vision, Python, CUDA",
        "Python, SQL, Airflow, Data Pipeline, ETL, Cloud Platforms",
        "R, Python, Statistical Modeling, Forecasting, Time Series",
        "Scala, Spark, Big Data, AWS, Data Engineering, Python",
        "Python, Machine Learning, XGBoost, Feature Engineering, Scikit-learn",
        "NLP, Python, NLTK, Transformers, Hugging Face, Deep Learning",
        "Python, SQL, MongoDB, NoSQL, Data Wrangling, Analytics"
    ]
    
    data = {
        'job_id': range(1, n_jobs + 1),
        'job_title': np.random.choice(job_titles, n_jobs),
        'company': np.random.choice(companies, n_jobs),
        'location': np.random.choice(locations, n_jobs),
        'salary_min': np.random.randint(400000, 800000, n_jobs),  # INR
        'salary_max': np.random.randint(900000, 1500000, n_jobs),  # INR
        'date_posted': pd.date_range(start='2025-01-01', periods=n_jobs, freq='6H'),
        'job_description': np.random.choice(job_descriptions, n_jobs),
        'is_remote': np.random.choice([0, 1], n_jobs, p=[0.3, 0.7]),
        'company_size': np.random.choice(['Startup', 'Mid-sized', 'Enterprise'], n_jobs)
    }
    
    return pd.DataFrame(data)

# ============================================================================
# PHASE 1: DATA LOADING
# ============================================================================
st.sidebar.header("📥 Data Source")
data_source = st.sidebar.radio("Choose data source:", 
                               ["Use Sample Data (Simulated)", "Upload CSV"])

if data_source == "Use Sample Data (Simulated)":
    df_raw = generate_sample_job_data(500)
    st.sidebar.success("✅ Sample data loaded (500 jobs)")
else:
    uploaded_file = st.sidebar.file_uploader("Upload job data CSV", type="csv")
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.sidebar.success(f"✅ Loaded {len(df_raw)} jobs")
    else:
        st.warning("Please upload a CSV file or use sample data")
        st.stop()

# ============================================================================
# PHASE 2: DATA CLEANING (Pandas + NumPy)
# ============================================================================
def clean_data(df):
    """
    Clean raw job data:
    1. Handle missing values
    2. Remove duplicates
    3. Fix data types
    4. Normalize text
    """
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['job_title', 'company', 'location'], keep='first')
    
    # Handle missing values
    df['salary_min'] = df['salary_min'].fillna(df['salary_min'].mean())
    df['salary_max'] = df['salary_max'].fillna(df['salary_max'].mean())
    df['is_remote'] = df['is_remote'].fillna(0).astype(int)
    
    # Ensure date is datetime
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    
    # Create new features
    df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2
    df['salary_range'] = df['salary_max'] - df['salary_min']
    df['days_since_posted'] = (pd.Timestamp.now() - df['date_posted']).dt.days
    
    return df

df_clean = clean_data(df_raw)

# ============================================================================
# PHASE 3: FEATURE ENGINEERING & ENCODING
# ============================================================================
def extract_skills(df):
    """
    Extract skills from job descriptions.
    This simulates what we'd do after web scraping: keyword matching
    """
    skills_dict = {
        'Python': ['python', 'py'],
        'SQL': ['sql', 'mysql', 'postgresql', 'oracle'],
        'R': ['r programming', 'r language', ' r '],
        'Machine Learning': ['machine learning', 'ml', 'sklearn', 'scikit-learn'],
        'Deep Learning': ['deep learning', 'tensorflow', 'pytorch', 'keras'],
        'Tableau': ['tableau', 'visualization'],
        'Power BI': ['power bi', 'powerbi'],
        'Spark': ['spark', 'pyspark', 'apache spark'],
        'AWS': ['aws', 'amazon web services'],
        'Azure': ['azure', 'microsoft azure'],
        'GCP': ['google cloud', 'gcp', 'bigquery'],
        'Hadoop': ['hadoop', 'hdfs'],
        'Statistics': ['statistics', 'statistical', 'stats'],
        'NLP': ['nlp', 'natural language'],
        'Computer Vision': ['computer vision', 'cv', 'image']
    }
    
    # Create binary columns for each skill
    for skill, keywords in skills_dict.items():
        df[f'skill_{skill}'] = 0
        for keyword in keywords:
            df[f'skill_{skill}'] |= df['job_description'].str.lower().str.contains(keyword, na=False).astype(int)
    
    return df, skills_dict

df_features = extract_skills(df_clean)[0]
skills_dict = extract_skills(df_clean)[1]

# ============================================================================
# ENCODING: CATEGORICAL VARIABLES
# ============================================================================
def encode_categorical(df):
    """
    Encode categorical variables:
    1. Label Encoding: job_title, company_size
    2. One-Hot Encoding: location, company
    """
    df_encoded = df.copy()
    
    # Label Encoding for job titles and company size
    le_title = LabelEncoder()
    le_size = LabelEncoder()
    
    df_encoded['job_title_encoded'] = le_title.fit_transform(df_encoded['job_title'])
    df_encoded['company_size_encoded'] = le_size.fit_transform(df_encoded['company_size'])
    
    # One-Hot Encoding for location (important for salary analysis by region)
    location_dummies = pd.get_dummies(df_encoded['location'], prefix='location', drop_first=True)
    df_encoded = pd.concat([df_encoded, location_dummies], axis=1)
    
    return df_encoded, le_title, le_size

df_encoded, le_title, le_size = encode_categorical(df_features)

# Store skill columns for later use
skill_columns = [col for col in df_encoded.columns if col.startswith('skill_')]

# ============================================================================
# MAIN DASHBOARD
# ============================================================================
st.markdown('<div class="main-header">📊 Job Market Trend Analyzer</div>', 
            unsafe_allow_html=True)
st.markdown("*Analyzing Data Science job market trends with Python, Pandas, NumPy, Scikit-learn, and Streamlit*")
st.divider()

# ============================================================================
# TAB 1: OVERVIEW & DATA EXPLORER
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🔍 EDA Analysis", 
    "💰 Salary Insights",
    "🤖 ML Models",
    "📥 Raw Data"
])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs Scraped", len(df_encoded))
    with col2:
        st.metric("Date Range", f"{df_encoded['date_posted'].min().date()} to {df_encoded['date_posted'].max().date()}")
    with col3:
        st.metric("Remote Jobs %", f"{(df_encoded['is_remote'].sum() / len(df_encoded) * 100):.1f}%")
    with col4:
        st.metric("Avg Salary", f"₹{df_encoded['salary_avg'].mean():,.0f}")
    
    st.subheader("🎯 Quick Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_job_title = st.selectbox("Job Title", df_encoded['job_title'].unique())
    with col2:
        selected_location = st.selectbox("Location", df_encoded['location'].unique())
    with col3:
        remote_only = st.checkbox("Remote Only")
    
    # Filter data
    filtered_df = df_encoded[
        (df_encoded['job_title'] == selected_job_title) &
        (df_encoded['location'] == selected_location)
    ]
    
    if remote_only:
        filtered_df = filtered_df[filtered_df['is_remote'] == 1]
    
    st.info(f"📌 Showing {len(filtered_df)} matching jobs")
    
    # Display filtered results
    display_cols = ['job_title', 'company', 'salary_avg', 'is_remote', 'date_posted']
    st.dataframe(filtered_df[display_cols].head(10), use_container_width=True)
    
    # Download button
    csv = filtered_df[display_cols].to_csv(index=False)
    st.download_button(
        label="⬇️ Download Filtered Jobs",
        data=csv,
        file_name=f"jobs_{selected_job_title}_{selected_location}.csv",
        mime="text/csv"
    )

# ============================================================================
# TAB 2: EXPLORATORY DATA ANALYSIS
# ============================================================================
with tab2:
    st.subheader("📈 Skill Demand Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 most demanded skills
        skill_counts = df_encoded[skill_columns].sum().sort_values(ascending=False)
        skill_names = [col.replace('skill_', '') for col in skill_counts.index]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0, 1, len(skill_names)))
        ax.barh(skill_names, skill_counts.values, color=colors)
        ax.set_xlabel('Number of Job Postings')
        ax.set_title('Top Skills in Demand', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Skill demand over time (monthly trend)
        df_encoded['year_month'] = df_encoded['date_posted'].dt.to_period('M')
        
        # Top 5 skills
        top_5_skills = skill_counts.head(5).index.tolist()
        
        trend_data = []
        for skill in top_5_skills:
            monthly_counts = df_encoded.groupby('year_month')[skill].sum()
            trend_data.append(monthly_counts.values)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, skill in enumerate(top_5_skills):
            skill_name = skill.replace('skill_', '')
            monthly_counts = df_encoded.groupby('year_month')[skill].sum()
            ax.plot(range(len(monthly_counts)), monthly_counts.values, 
                   marker='o', label=skill_name, linewidth=2)
        
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Number of Postings')
        ax.set_title('Skill Demand Trends Over Time', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    st.subheader("🏢 Job Title Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Job titles pie chart
        job_title_counts = df_encoded['job_title'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(job_title_counts.values, labels=job_title_counts.index, autopct='%1.1f%%',
              startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(job_title_counts))))
        ax.set_title('Distribution of Job Titles', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Company size distribution
        company_size_counts = df_encoded['company_size'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        ax.bar(company_size_counts.index, company_size_counts.values, color=colors)
        ax.set_ylabel('Number of Jobs')
        ax.set_title('Jobs by Company Size', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    st.subheader("📍 Geographic Distribution")
    
    location_counts = df_encoded['location'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(location_counts.index, location_counts.values, color=plt.cm.coolwarm(np.linspace(0, 1, len(location_counts))))
    ax.set_ylabel('Number of Jobs')
    ax.set_title('Job Postings by Location', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ============================================================================
# TAB 3: SALARY INSIGHTS
# ============================================================================
with tab3:
    st.subheader("💰 Salary Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Salary distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df_encoded['salary_avg'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax.axvline(df_encoded['salary_avg'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: ₹{df_encoded['salary_avg'].mean():,.0f}")
        ax.axvline(df_encoded['salary_avg'].median(), color='green', linestyle='--', linewidth=2, label=f"Median: ₹{df_encoded['salary_avg'].median():,.0f}")
        ax.set_xlabel('Average Salary (INR)')
        ax.set_ylabel('Frequency')
        ax.set_title('Salary Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Salary by job title
        salary_by_title = df_encoded.groupby('job_title')['salary_avg'].agg(['mean', 'std']).sort_values('mean', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(salary_by_title.index, salary_by_title['mean'].values, color='mediumpurple')
        ax.set_xlabel('Average Salary (INR)')
        ax.set_title('Average Salary by Job Title', fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Remote vs On-site salary comparison
        remote_salary = df_encoded[df_encoded['is_remote'] == 1]['salary_avg']
        onsite_salary = df_encoded[df_encoded['is_remote'] == 0]['salary_avg']
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bp = ax.boxplot([onsite_salary, remote_salary], labels=['On-site', 'Remote'], patch_artist=True)
        for patch, color in zip(bp['boxes'], ['#FF6B6B', '#4ECDC4']):
            patch.set_facecolor(color)
        ax.set_ylabel('Salary (INR)')
        ax.set_title('Salary Comparison: Remote vs On-site', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        
        st.metric("Remote Avg Salary", f"₹{remote_salary.mean():,.0f}")
        st.metric("On-site Avg Salary", f"₹{onsite_salary.mean():,.0f}")
        st.metric("Difference", f"₹{(remote_salary.mean() - onsite_salary.mean()):,.0f}")
    
    with col2:
        # Salary by location
        salary_by_location = df_encoded.groupby('location')['salary_avg'].mean().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(salary_by_location)))
        ax.bar(salary_by_location.index, salary_by_location.values, color=colors)
        ax.set_ylabel('Average Salary (INR)')
        ax.set_title('Salary by Location', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    st.subheader("🔗 Skill-Salary Correlation")
    
    # Calculate average salary for each skill
    skill_salary_data = []
    for skill_col in skill_columns:
        skill_name = skill_col.replace('skill_', '')
        avg_salary = df_encoded[df_encoded[skill_col] == 1]['salary_avg'].mean()
        count = df_encoded[skill_col].sum()
        skill_salary_data.append({'Skill': skill_name, 'Avg Salary': avg_salary, 'Count': count})
    
    skill_salary_df = pd.DataFrame(skill_salary_data).sort_values('Avg Salary', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        top_salary_skills = skill_salary_df.head(10)
        ax.barh(top_salary_skills['Skill'], top_salary_skills['Avg Salary'], color='gold')
        ax.set_xlabel('Average Salary (INR)')
        ax.set_title('Highest Paying Skills', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Salary vs skill count heatmap
        heatmap_data = []
        for skill_col in skill_columns[:5]:  # Top 5 skills
            skill_name = skill_col.replace('skill_', '')
            salaries = df_encoded[df_encoded[skill_col] == 1]['salary_avg'].values
            heatmap_data.append(salaries)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(heatmap_data, cmap='YlOrRd', xticklabels=False, yticklabels=[s.replace('skill_', '') for s in skill_columns[:5]], ax=ax)
        ax.set_title('Salary Distribution by Skill (Top 5)', fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

# ============================================================================
# TAB 4: MACHINE LEARNING MODELS
# ============================================================================
with tab4:
    st.subheader("🤖 Machine Learning Models")
    
    # Prepare features for ML
    feature_cols = skill_columns + [col for col in df_encoded.columns if col.startswith('location_')]
    X = df_encoded[feature_cols].fillna(0)
    y_salary = df_encoded['salary_avg']
    
    # Standardize features for clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model_choice = st.selectbox("Choose a Model", [
        "Salary Prediction (Random Forest)",
        "Salary Prediction (Linear Regression)",
        "Job Clustering (K-Means)"
    ])
    
    if model_choice == "Salary Prediction (Random Forest)":
        st.subheader("💰 Salary Prediction Model")
        
        # Train Random Forest
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        rf_model.fit(X, y_salary)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': [col.replace('skill_', '').replace('location_', '') for col in feature_cols],
            'Importance': rf_model.feature_importances_
        }).sort_values('Importance', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(feature_importance['Feature'], feature_importance['Importance'], color='teal')
            ax.set_xlabel('Importance Score')
            ax.set_title('Feature Importance (Random Forest)', fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Model performance
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X, y_salary, test_size=0.2, random_state=42)
            rf_model_train = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            rf_model_train.fit(X_train, y_train)
            
            train_score = rf_model_train.score(X_train, y_train)
            test_score = rf_model_train.score(X_test, y_test)
            
            st.metric("Training R² Score", f"{train_score:.3f}")
            st.metric("Testing R² Score", f"{test_score:.3f}")
            
            # Actual vs Predicted
            y_pred = rf_model_train.predict(X_test)
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(y_test, y_pred, alpha=0.5, color='darkblue')
            ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
            ax.set_xlabel('Actual Salary (INR)')
            ax.set_ylabel('Predicted Salary (INR)')
            ax.set_title('Actual vs Predicted Salary', fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
    
    elif model_choice == "Salary Prediction (Linear Regression)":
        st.subheader("📈 Linear Regression Model")
        
        lr_model = LinearRegression()
        lr_model.fit(X, y_salary)
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y_salary, test_size=0.2, random_state=42)
        lr_model_train = LinearRegression()
        lr_model_train.fit(X_train, y_train)
        
        train_score = lr_model_train.score(X_train, y_train)
        test_score = lr_model_train.score(X_test, y_test)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Training R² Score", f"{train_score:.3f}")
            st.metric("Testing R² Score", f"{test_score:.3f}")
        
        with col2:
            # Residuals
            y_pred = lr_model_train.predict(X_test)
            residuals = y_test - y_pred
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(y_pred, residuals, alpha=0.5, color='purple')
            ax.axhline(y=0, color='r', linestyle='--', lw=2)
            ax.set_xlabel('Predicted Salary (INR)')
            ax.set_ylabel('Residuals')
            ax.set_title('Residual Plot', fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
    
    else:  # K-Means Clustering
        st.subheader("👥 Job Market Segmentation (K-Means)")
        
        # Find optimal k using elbow method
        inertias = []
        K_range = range(2, 11)
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
            ax.set_xlabel('Number of Clusters (k)')
            ax.set_ylabel('Inertia')
            ax.set_title('Elbow Method for Optimal k', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            optimal_k = st.slider("Select Number of Clusters", 2, 10, 3)
        
        # Train final model
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        df_encoded['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Visualize clusters
        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(df_encoded['salary_avg'], df_encoded['days_since_posted'], 
                            c=df_encoded['cluster'], cmap='viridis', s=100, alpha=0.6)
        ax.set_xlabel('Average Salary (INR)')
        ax.set_ylabel('Days Since Posted')
        ax.set_title(f'Job Market Clusters (k={optimal_k})', fontsize=12, fontweight='bold')
        plt.colorbar(scatter, ax=ax, label='Cluster')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Cluster characteristics
        cluster_stats = df_encoded.groupby('cluster').agg({
            'salary_avg': 'mean',
            'is_remote': 'mean',
            'job_id': 'count'
        }).rename(columns={'job_id': 'job_count'})
        
        st.subheader("Cluster Characteristics")
        st.dataframe(cluster_stats, use_container_width=True)

# ============================================================================
# TAB 5: RAW DATA EXPLORER
# ============================================================================
with tab5:
    st.subheader("📥 Raw & Processed Data")
    
    data_view = st.radio("View:", ["Raw Data", "Cleaned Data", "Encoded Data with Skills"])
    
    if data_view == "Raw Data":
        st.dataframe(df_raw.head(20), use_container_width=True)
    elif data_view == "Cleaned Data":
        st.dataframe(df_clean.head(20), use_container_width=True)
    else:
        display_df = df_encoded[['job_title', 'company', 'location', 'salary_avg'] + skill_columns[:5]]
        st.dataframe(display_df.head(20), use_container_width=True)
    
    st.divider()
    st.subheader("📊 Data Quality Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df_encoded))
        st.metric("Duplicate Records Removed", len(df_raw) - len(df_clean))
    
    with col2:
        st.metric("Missing Values %", f"{(df_encoded.isnull().sum().sum() / (len(df_encoded) * len(df_encoded.columns)) * 100):.2f}%")
        st.metric("Date Range (Days)", (df_encoded['date_posted'].max() - df_encoded['date_posted'].min()).days)
    
    with col3:
        st.metric("Unique Companies", df_encoded['company'].nunique())
        st.metric("Unique Locations", df_encoded['location'].nunique())
    
    st.divider()
    st.subheader("⬇️ Download Processed Data")
    
    csv_clean = df_clean.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Data",
        data=csv_clean,
        file_name="jobs_cleaned.csv",
        mime="text/csv"
    )
    
    csv_encoded = df_encoded.to_csv(index=False)
    st.download_button(
        label="Download Encoded Data (with Skills)",
        data=csv_encoded,
        file_name="jobs_encoded.csv",
        mime="text/csv"
    )

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
### 📌 About This Project
This Data Science portfolio project demonstrates:
- **Web Scraping** (BeautifulSoup in real implementation)
- **Data Cleaning** (Pandas, NumPy)
- **Feature Engineering** (Encoding, categorization)
- **EDA** (Matplotlib, Seaborn)
- **Machine Learning** (Scikit-learn: Regression, Clustering)
- **Dashboard Development** (Streamlit)

**Built by:** Abhisar Sharma | **Skills Demonstrated:** Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Streamlit

""")