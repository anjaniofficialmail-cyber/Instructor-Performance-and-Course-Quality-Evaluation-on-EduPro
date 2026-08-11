import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Instructor & Course Analytics", layout="wide")

st.title("📊 EduPro Instructor Performance & Course Quality Dashboard")
st.markdown("Data-driven analysis of instructor effectiveness and course quality on the EduPro platform.")

@st.cache_data
def load_data():
    df = pd.read_csv('data/merged_dataset.csv')
    return df

df = load_data()

# Build the teacher-course pairs table used across most charts
pairs = df.drop_duplicates(subset=['TeacherID', 'CourseID'])[
    ['TeacherID', 'TeacherName', 'Expertise', 'YearsOfExperience', 'TeacherRating',
     'CourseID', 'CourseName', 'CourseCategory', 'CourseLevel', 'CourseRating']
]

st.write(f"Dataset loaded: {df['TeacherID'].nunique()} instructors, {df['CourseID'].nunique()} courses, {len(df)} transactions")

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

expertise_options = sorted(pairs['Expertise'].unique())
selected_expertise = st.sidebar.multiselect("Instructor Expertise", expertise_options, default=expertise_options)

category_options = sorted(pairs['CourseCategory'].unique())
selected_category = st.sidebar.multiselect("Course Category", category_options, default=category_options)

level_options = sorted(pairs['CourseLevel'].unique())
selected_level = st.sidebar.multiselect("Course Level", level_options, default=level_options)

rating_range = st.sidebar.slider("Teacher Rating Range", 1.0, 5.0, (1.0, 5.0), 0.1)

# Apply filters
filtered = pairs[
    (pairs['Expertise'].isin(selected_expertise)) &
    (pairs['CourseCategory'].isin(selected_category)) &
    (pairs['CourseLevel'].isin(selected_level)) &
    (pairs['TeacherRating'].between(rating_range[0], rating_range[1]))
]

st.sidebar.markdown(f"**Showing {filtered['TeacherID'].nunique()} instructors, {filtered['CourseID'].nunique()} courses**")

# ---- INSTRUCTOR LEADERBOARD ----
st.header("🏆 Instructor Performance Leaderboard")

leaderboard = filtered.drop_duplicates(subset='TeacherID')[
    ['TeacherName', 'Expertise', 'YearsOfExperience', 'TeacherRating']
].sort_values('TeacherRating', ascending=False).reset_index(drop=True)
leaderboard.index = leaderboard.index + 1  # start ranking at 1

st.dataframe(leaderboard, use_container_width=True)

# ---- EXPERIENCE VS RATING SCATTER ----
st.header("📈 Experience vs Teacher Rating")

scatter_data = filtered.drop_duplicates(subset='TeacherID')
fig_scatter = px.scatter(
    scatter_data,
    x='YearsOfExperience',
    y='TeacherRating',
    color='Expertise',
    hover_data=['TeacherName'],
    title='Does More Experience Mean Higher Ratings?'
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---- COURSE QUALITY HEATMAP ----
st.header("🔥 Course Quality Heatmap")

heatmap_data = filtered.drop_duplicates(subset='CourseID').pivot_table(
    index='CourseCategory',
    columns='CourseLevel',
    values='CourseRating',
    aggfunc='mean'
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto='.2f',
    color_continuous_scale='RdYlGn',
    aspect='auto',
    title='Average Course Rating by Category & Level'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ---- EXPERTISE-WISE COMPARISON ----
st.header("🎯 Expertise-wise Performance Comparison")

expertise_compare = filtered.groupby('Expertise').agg(
    AvgTeacherRating=('TeacherRating', 'mean'),
    AvgCourseRating=('CourseRating', 'mean'),
    NumCourses=('CourseID', 'nunique')
).reset_index().sort_values('AvgCourseRating', ascending=False)

fig_expertise = px.bar(
    expertise_compare,
    x='Expertise',
    y=['AvgTeacherRating', 'AvgCourseRating'],
    barmode='group',
    title='Average Teacher Rating vs Course Rating by Expertise Area',
    labels={'value': 'Average Rating', 'variable': 'Metric'}
)
st.plotly_chart(fig_expertise, use_container_width=True)

st.dataframe(expertise_compare, use_container_width=True)