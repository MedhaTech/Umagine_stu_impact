import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import json

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="📊 Student Registration Dashboard", layout="wide")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("cleaned_school_data.csv")
df['State'] = df['State'].str.strip().str.title()
df['City'] = df['City'].str.strip().str.title()
df['School Name'] = df['School Name'].str.strip().str.title()
df['No of teachers registered'] = pd.to_numeric(df['No of teachers registered'], errors='coerce').fillna(0)

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Filter")
selected_state = st.sidebar.selectbox("Select State", ["All"] + sorted(df["State"].unique()))
filtered_df = df if selected_state == "All" else df[df["State"] == selected_state]

# ------------------ HEADER ------------------
st.markdown("<h1 style='text-align: center; color: white;'>📊 Student Registration Dashboard</h1>", unsafe_allow_html=True)

# ------------------ KPIs ------------------
total_schools = filtered_df['School Name'].nunique()
total_teachers = int(filtered_df['No of teachers registered'].sum())
avg_teachers = round(total_teachers / total_schools, 2)

col1, col2, col3 = st.columns(3)
col1.metric("🏫 Total Schools", total_schools)
col2.metric("👩‍🏫 Total Teachers", total_teachers)
col3.metric("📈 Avg Teachers/School", avg_teachers)

st.markdown("---")

# ------------------ PIE CHART ------------------
st.subheader("📍 Teacher Distribution by State")
state_summary = df.groupby("State")["No of teachers registered"].sum().reset_index()
fig1 = px.pie(state_summary, names='State', values='No of teachers registered', hole=0.4)
fig1.update_layout(legend_font_color="black", legend_title_font_color="black")
st.plotly_chart(fig1, use_container_width=True)

# ------------------ BAR CHARTS ------------------
st.subheader("🏫 Top & Bottom Schools")
school_counts = df.groupby("School Name")["No of teachers registered"].sum().sort_values(ascending=False)
top_schools = school_counts.head(5).reset_index()
bottom_schools = school_counts.tail(5).reset_index()

col4, col5 = st.columns(2)
fig_top = px.bar(top_schools, x='School Name', y='No of teachers registered', color='No of teachers registered',
                 color_continuous_scale='greens', title="Top 5 Schools")
fig_bottom = px.bar(bottom_schools, x='School Name', y='No of teachers registered', color='No of teachers registered',
                    color_continuous_scale='reds', title="Bottom 5 Schools")
col4.plotly_chart(fig_top, use_container_width=True)
col5.plotly_chart(fig_bottom, use_container_width=True)

# ------------------ GEO MAP INDIA ------------------
st.subheader("🗺️ India Geo Heatmap – Teacher Participation by State")
with open("india_states.geojson", "r", encoding="utf-8") as f:
    india_geo = json.load(f)
for feature in india_geo['features']:
    feature['properties']['ST_NM'] = feature['properties']['ST_NM'].strip().title()

map_df = df.groupby("State")["No of teachers registered"].sum().reset_index()
map_df.columns = ["State", "TeacherCount"]

fig_map = px.choropleth(
    map_df,
    geojson=india_geo,
    featureidkey='properties.ST_NM',
    locations='State',
    color='TeacherCount',
    color_continuous_scale='RdYlGn_r',
    title='📌 Geo Map: Teacher Registration Intensity'
)
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0},
    geo_bgcolor="rgba(0,0,0,0)",
    legend_title_text="Teachers Registered",
    legend_font_color="white"
)
st.plotly_chart(fig_map, use_container_width=True)

# ------------------ TEXT HEATMAP ------------------
st.subheader("📍 Statewise Teacher Heatmap (Text Style)")
fig2, ax = plt.subplots(figsize=(8, 14))
sns.heatmap(
    map_df.set_index('State').sort_values('TeacherCount', ascending=False),
    cmap='YlGnBu',
    annot=True,
    fmt=".0f",
    linewidths=0.5
)
st.pyplot(fig2)

# ------------------ ZERO TEACHERS ------------------
st.subheader("🚫 Schools with Zero Teachers")
zero_teacher_count = df[df['No of teachers registered'] == 0]['School Name'].nunique()
if zero_teacher_count > 0:
    st.warning(f"⚠️ Total Schools with 0 Teachers: **{zero_teacher_count}**")
else:
    st.success("✅ No schools with zero teacher registration.")

# ------------------ LOW PARTICIPATION CITIES ------------------
city_counts = df.groupby('City')['School Name'].nunique().sort_values()
low_participation = city_counts[city_counts <= 2]
st.subheader("📌 Cities with ≤ 2 Registered Schools")
if not low_participation.empty:
    st.dataframe(low_participation.rename("School Count"))
else:
    st.success("All cities have more than 2 schools.")

# ------------------ OUTLIER & RANGE ------------------
st.subheader("📉 Outlier & Range Stats")
school_dist = df.groupby("School Name")["No of teachers registered"].sum()
over_100 = school_dist[school_dist > 100]
range_3_10 = school_dist[(school_dist >= 3) & (school_dist <= 10)].count()
percent_range = round((range_3_10 / total_schools) * 100, 2)

col6, col7 = st.columns(2)
col6.info(f"🧯 Schools > 100 Teachers: **{len(over_100)}**")
col7.info(f"📊 Schools with 3–10 Teachers: **{range_3_10}** ({percent_range}%)")

# ------------------ STATE PARTICIPATION RANKING ------------------
st.subheader("🏆 State Participation Ranking")

top_state = map_df.sort_values("TeacherCount", ascending=False).iloc[0]
bottom_state = map_df.sort_values("TeacherCount", ascending=True).iloc[0]
total_teachers_all = map_df["TeacherCount"].sum()
top_pct = round((top_state["TeacherCount"] / total_teachers_all) * 100, 2)
bot_pct = round((bottom_state["TeacherCount"] / total_teachers_all) * 100, 2)

colA, colB = st.columns(2)
colA.success(f"""
🏆 **Top State**  
**{top_state['State']}**  
👨‍🏫 {top_state['TeacherCount']} teachers  
📊 {top_pct}%
""")

colB.error(f"""
🔻 **Lowest State**  
**{bottom_state['State']}**  
👨‍🏫 {bottom_state['TeacherCount']} teachers  
📉 {bot_pct}%
""")

# ------------------ DATA QUALITY ------------------
st.subheader("🧹 Data Quality Summary")
duplicates = df.duplicated().sum()
missing_city = df['City'].isnull().sum()
missing_address = df['Address'].isnull().sum() if 'Address' in df.columns else 0
missing_pincode = df['Pincode'].isnull().sum() if 'Pincode' in df.columns else 0

colX, colY, colZ = st.columns(3)
colX.info(f"🔁 **Duplicate Rows:** {duplicates}")
colY.warning(f"🏙️ **Missing City:** {missing_city}")
colZ.warning(f"📮 **Missing Pincode:** {missing_pincode}")
if 'Address' in df.columns:
    st.info(f"🏠 **Missing Address:** {missing_address}")


# 📍 Final India Map Summary
st.markdown("## 🗺️ India State Participation Summary")

# Show the uploaded image
st.image("map.png", use_container_width=True)

# Explanatory legend
st.markdown("""
### 🧠 Insights by State Performance

#### 🟢 Top Performing States (Highest Teacher Registrations)
These states showed **strong outreach and high participation**:
- **Rajasthan**
- **Tamil Nadu**
- **Andhra Pradesh**
- **Kerala**
- **Madhya Pradesh**

#### 🟠 Medium Performing States (Growth Opportunity)
These states are **performing decently**, and can **rise with more support**:
- **Karnataka**
- **Odisha**
- **Assam**
- **Bihar**
- **Chhattisgarh**

#### 🔴 Bottom Performing States (Needs Attention)
These states have **very low registration counts**, possibly due to awareness, tech access, or outreach issues:
- **Lakshadweep**
- **Daman and Diu**
- **Chandigarh**
- **Mizoram**
- **Andaman and Nicobar Islands**
""")
