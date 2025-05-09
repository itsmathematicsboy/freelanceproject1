import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

day = pd.read_csv(r'day_cleaned.csv')
hour = pd.read_csv(r'hour_cleaned.csv')

day['dteday'] = pd.to_datetime(day['dteday'])  
hour['dteday'] = pd.to_datetime(hour['dteday'])


st.set_page_config(layout="wide")

st.markdown('<h2 style = "text-align: center;"> Dashboard Perilaku Penyewa Sepeda </h2>', unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; text-align: center;">
                <h4>Jumlah Penyewa Per Hari</h4>
                <p style="font-size: 24px; font-weight: bold;">{}</p>
            </div>
        """.format(len(day)), unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; text-align: center;">
                <h4>Jumlah Penyewa Per Jam</h4>
                <p style="font-size: 24px; font-weight: bold;">{}</p>
            </div>
        """.format(len(hour)), unsafe_allow_html=True)

    with col3:
        mean_jam = np.mean(hour['Jam'])
        jam_range = f'{int(np.ceil(mean_jam))}-{int(np.floor(mean_jam))}'
        st.markdown("""
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 5px; text-align: center;">
                <h4>Rata-rata Jam Yang Dihabiskan Penyewa</h4>
                <p style="font-size: 24px; font-weight: bold;">{}</p>
            </div>
        """.format(jam_range), unsafe_allow_html=True)

@st.cache_data
def get_rent_by_hour(hour):
    hourly_rentals = hour.groupby(by=['Jam'])[['Total Penyewa', 'non aktif', 'aktif']].sum().sort_values(by=['Total Penyewa'], ascending=False)
    hourly_rentals = hourly_rentals.reset_index()
    melted_data = hourly_rentals.melt(id_vars=['Jam'], value_vars=['Total Penyewa', 'non aktif', 'aktif'], var_name='User Type', value_name='Total Rentals')
    return melted_data

@st.cache_data
def get_rent_by_mth(day):
    day1 = day.copy()
    day1['bulan'] = day1['dteday'].dt.to_period('M').astype(str)
    monthly = day1.groupby('bulan').agg({
    'aktif': 'sum',
    'non aktif': 'sum'
    }).reset_index()
    monthly['bulan'] = pd.to_datetime(monthly['bulan'])
    return monthly

@st.cache_data
def get_rent_by_day(day):
    day['dteday'] = pd.to_datetime(day['dteday'])
    daily_rentals = day.groupby(by=day['dteday'].dt.day_name())['Total Penyewa'].sum().sort_values(ascending=False)
    return daily_rentals

@st.cache_data
def get_rent_by_hour_trend(hour):
    pagi_df = hour[(hour['Jam'] >= 6) & (hour['Jam'] <= 9)].copy()
    malam_df = hour[(hour['Jam'] >= 18) & (hour['Jam'] <= 21)].copy()
    pagi_df.loc[:, 'Waktu'] = 'Pagi'
    malam_df.loc[:, 'Waktu'] = 'Malam'
    pagi_malam_df = pd.concat([pagi_df, malam_df])
    return pagi_malam_df

@st.cache_data
def get_rent_by_season(day):
    pivot_musim = pd.pivot_table(
    day,
    values='Total Penyewa',
    index='musim',
    aggfunc='sum'
    )
    return pivot_musim

@st.cache_data
def get_rent_cnt_by_season(day):
    ssn_act = day.groupby('musim')[['non aktif','aktif']].sum().reset_index()
    ssn_melted = ssn_act.melt(id_vars='musim', 
                          value_vars=['non aktif', 'aktif'], 
                          var_name='status', 
                          value_name='Total')
    return ssn_melted

@st.cache_data
def get_data1(day):
    final_data1 = pd.pivot_table(
        data=day,
        index='musim',
        values=['aktif', 'non aktif', 'temp', 'atemp', 'hum'],
        aggfunc={
            'aktif': 'count',
            'non aktif': 'count',
            'temp': 'sum',
            'atemp': 'sum',
            'hum': 'sum'
        }
    )
    return final_data1

@st.cache_data
def get_data2(hour):
    hr_final = hour.groupby('dteday')[['temp','atemp','hum']].sum().reset_index()
    return hr_final
monthly = get_rent_by_mth(day)
melted_data = get_rent_by_hour(hour)
daily_rentals = get_rent_by_day(day)
pagi_malam_df = get_rent_by_hour_trend(hour)
pivot_musim = get_rent_by_season(day)
ssn_melted = get_rent_cnt_by_season(day)
final_data1 = get_data1(day)
final_data2 = get_data2(hour)
final_data2 = final_data2.sort_values(by = 'temp', ascending = False).head()

# Plotting
with st.container():
    col1, col2 = st.columns(2)
    col1.subheader('Trend Penyewa Aktif per Bulan')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=monthly, x='bulan', y='aktif', label='Aktif', color='blue', ax=ax)
    sns.scatterplot(data=monthly, x='bulan', y='aktif', label='Aktif', marker = 'o',color='blue', ax=ax)
    sns.lineplot(data=monthly, x='bulan', y='non aktif', label='Non Aktif', color='orange', ax=ax)
    sns.scatterplot(data=monthly, x='bulan', y='non aktif', label='Non Aktif', marker = 'v',color='orange', ax=ax)

    ax.set_title('Jumlah Penyewa Aktif dan Non Aktif per Bulan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Penyewa')
    ax.grid(True, linestyle = '--')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    col1.pyplot(fig)
    
    col2.markdown('<h4 style = "font-size = 10px;">Trend Penyewaan Sepeda Per Hari</h4>',unsafe_allow_html=
                  True)
    fig, ax = plt.subplots(figsize = (14, 9))
    sns.lineplot(x = daily_rentals.index, y = daily_rentals.values, color = 'green', ax = ax)
    sns.scatterplot(x=daily_rentals.index, y=daily_rentals.values, marker = 'o', ax = ax)
    ax.set_title('Distribusi Penyewaan Sepeda Berdasarkan Hari dalam Seminggu')
    ax.set_xlabel('Hari')
    ax.set_ylabel('Total Penyewaan')
    ax.grid(True, linestyle = '--')
    
    col2.pyplot(fig)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        col1.subheader('Trend Penyewaan Sepeda Berdasarkan Durasi per Jam dan Tipe Pengguna')
        fig, ax = plt.subplots(figsize = (10, 8))
        sns.barplot(x = 'Jam', y = 'Total Rentals',  hue='User Type', data = melted_data, ax = ax)
        ax.set_title('Total Penyewaan Sepeda Berdasarkan Durasi per Jam dan Tipe Pengguna')
        ax.grid(True, axis = 'y',linestyle = '--')
        ax.legend(title = 'Tipe Pengguna')
        col1.pyplot(fig)
    with col2:
        col2.subheader('Trend Penyewaan Sepeda Berdasarkan Durasi per Jam dan Tipe Pengguna')
        fig, ax = plt.subplots(figsize = (10, 8))
        sns.barplot(x = 'Jam', y = 'Total Penyewa', hue = 'Waktu', data = pagi_malam_df, estimator = 'sum', errorbar = None, ax = ax)
        for i in ax.containers:
            ax.bar_label(i, fontsize=10)
        ax.set_title('Pola Penyewaan Sepeda di Pagi dan Malam Hari')
        ax.legend()
        col2.pyplot(fig)

with st.container():
    cols1, cols2 = st.columns(2)
    with cols1:
        cols1.subheader('Trend Penyewaan Sepeda Berdasarkan Musim')
        fig,ax = plt.subplots(figsize = (20, 12))
        ax.pie(pivot_musim['Total Penyewa'], autopct = '%1.1f%%')
        ax.set_title('Total Penyewa Sepeda Berdasarkan Musim')
        ax.legend(labels = pivot_musim.index)
        cols1.pyplot(fig)
    with cols2:
        cols2.subheader('Trend Penyewaan Sepeda Berdasarkan Musim dan Keaktifan')
        fig, ax = plt.subplots(figsize = (10, 8))
        sns.barplot(data = ssn_melted, x = 'musim', y = 'Total', hue = 'status', errorbar = None, ax = ax)
        ax.set_title('Total Penyewa Sepeda Berdasarkan Musim dan Keaktifan')
        ax.legend()
        cols2.pyplot(fig)

with st.container():
    col1, col2 = st.columns(2)
    col1.subheader('Data Hari Tambahan Untuk Aktif dan Non-Aktif Berdasarkan Suhu dan Kekuatan Angin')
    col1.dataframe(final_data1)
    col2.subheader('Data Jam Tambahan Untuk Aktif dan Non-Aktif Berdasarkan Suhu dan Kekuatan Angin')
    col2.dataframe(final_data2)
        
