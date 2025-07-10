import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

months = range(1, 13)
month_labels = ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни', 'Юли', 'Август', 'Септември', 'Октомври', 'Ноември', 'Декември']

st.title("Графики и статистики за наблюдения на птици")
st.markdown(
    """
    **Важно:** Това приложение не събира и не съхранява лични данни. Всички файлове се обработват само локално във вашия браузър и не се изпращат или записват никъде.
    """
)

uploaded_file = st.file_uploader("Изберете CSV файл", type="csv")
if uploaded_file:

    plot_option = st.selectbox(
        "Избери графика",
        (   "Наблюдения по години",
            "Видове по години",
            "Наблюдения по месеци",
            "Видове по месеци",
	    "Наблюдения по часове",
            "Наблюдения и видове по месеци",
            "Наблюдения и видове по години",
            "Топ 10 на най-често наблюдавани видове",
            "Списък на всички отбелязани видове"
        )
    )

    first_line = uploaded_file.readline().decode('utf-8').strip()
    separator = ';' if ';' in first_line else ','
    separated_values = first_line.split(separator)
    system_type = 'SmartBirds' if separated_values[0].replace('\ufeff', '').strip().lower() == 'id' else 'eBird'

    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, sep=separator, encoding='utf-8')

    if system_type == 'SmartBirds':
        df.index = pd.to_datetime(df['observationDate'], format='%d.%m.%Y')
        df['speciesBg'] = df['speciesBg'].str.replace(r'^.+\|\s*', '', regex=True).str.strip()
        monthly_counts = df['observationDate'].groupby(df.index.month).count()
        yearly_counts = df['observationDate'].groupby(df.index.year).count()
        unique_species = df.groupby(df.index.month)['speciesBg'].nunique()
        year_unique_species = df.groupby(df.index.year)['speciesBg'].nunique()
        top_species = df['speciesBg'].value_counts().head(10)
	df['hour'] = pd.to_datetime(df['observationTime'], format='%H:%M').dt.hour
        hour_spread = df.groupby('hour').size()
    else:
        df['Common Name'] = df['Common Name'].str.replace(r'\([^\)]+\)', '', regex=True).str.strip()
        df.index = pd.to_datetime(df['Date'], format='mixed')
        monthly_counts = df['Date'].groupby(df.index.month).count()
        yearly_counts = df['Date'].groupby(df.index.year).count()
        unique_species = df.groupby(df.index.month)['Common Name'].nunique()
        year_unique_species = df.groupby(df.index.year)['Common Name'].nunique()
        top_species = df['Common Name'].value_counts().head(10)
	df['hour'] = pd.to_datetime(df['Time'], format='%I:%M %p').dt.hour
        hour_spread = df.groupby('hour').size()

    fig, ax = plt.subplots(figsize=(18, 8))
    values_species = [unique_species.get(m, 0) for m in months]
    values_months = [monthly_counts.get(m, 0) for m in months]
    bar_width = 0.2 if len(yearly_counts) == 1 else 0.4

    if plot_option == "Наблюдения по месеци":
        bars1 = ax.bar(months, values_months, width=bar_width, color='blue')
        ax.bar_label(bars1, padding=3)
        ax.set_title(f"Наблюдения по месеци от {system_type}")
        ax.set_ylabel("Брой наблюдения")
        ax.set_xlabel("Месеци")
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels)
        min_val = max(min(values_months) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Наблюдения по години":
        bar = ax.bar(yearly_counts.index, yearly_counts.values, width=bar_width, color='red')
        fontsize = 8 if len(yearly_counts.index) > 10 else 12
        ax.bar_label(bar, padding=3, fontsize=fontsize)
        ax.set_title(f"Наблюдения по години от {system_type}")
        ax.set_ylabel("Брой наблюдения")
        ax.set_xlabel("Година")
        ax.set_xticks(yearly_counts.index)
        if len(yearly_counts.index) > 10:
            ax.set_xticklabels([str(y)[-2:] for y in yearly_counts.index])
        else:
            ax.set_xticklabels(yearly_counts.index)
        min_val = max(min(yearly_counts.values) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Видове по години":
        bar = ax.bar(year_unique_species.index, year_unique_species.values, width=bar_width, color='red')
        fontsize = 8 if len(year_unique_species.index) > 10 else 12
        ax.bar_label(bar, padding=3, fontsize=fontsize)
        ax.set_title(f"Видове по години от {system_type}")
        ax.set_ylabel("Брой видове")
        ax.set_xlabel("Година")
        ax.set_xticks(year_unique_species.index)
        if len(year_unique_species.index) > 10:
            ax.set_xticklabels([str(y)[-2:] for y in year_unique_species.index])
        else:
            ax.set_xticklabels(year_unique_species.index)
        min_val = max(min(year_unique_species.values) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Видове по месеци":
        bars2 = ax.bar(months, values_species, width=bar_width, color='orange')
        ax.bar_label(bars2, padding=3)
        ax.set_title(f"Видове по месеци от {system_type}")
        ax.set_ylabel("Брой видове")
        ax.set_xlabel("Месец")
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels)
        min_val = max(min(values_species) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Наблюдения и видове по месеци":
        bars1 = ax.bar([m - 0.2 for m in months], values_months, width=bar_width, label='Брой наблюдения', color='blue')
        bars2 = ax.bar([m + 0.2 for m in months], values_species, width=bar_width, label='Брой видове', color='orange')
        ax.bar_label(bars1, padding=3)
        ax.bar_label(bars2, padding=3)
        ax.set_title(f"Наблюдения и видове по месеци от {system_type}")
        ax.set_ylabel("Брой наблюдения и видове")
        ax.set_xlabel("Месец")
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels)
        ax.legend(['Брой наблюдения', 'Брой видове'])
        st.pyplot(fig)
    elif plot_option == "Наблюдения и видове по години":
        bars1 = ax.bar([m - 0.2 for m in yearly_counts.index], yearly_counts.values, width=bar_width, label='Брой наблюдения', color='blue')
        bars2 = ax.bar([m + 0.2 for m in year_unique_species.index], year_unique_species.values, width=bar_width, label='Брой видове', color='orange')
        fontsize = 6 if len(year_unique_species.index) > 10 else 12
        ax.bar_label(bars1, padding=3, fontsize=fontsize)
        ax.bar_label(bars2, padding=3, fontsize=fontsize)
        ax.set_title(f"Наблюдения и видове по години от {system_type}")
        ax.set_ylabel("Брой наблюдения и видове")
        ax.set_xlabel("Година")
        ax.set_xticks(yearly_counts.index)
        if len(year_unique_species.index) > 10:
            ax.set_xticklabels([str(y)[-2:] for y in year_unique_species.index])
        else:
            ax.set_xticklabels(year_unique_species.index)
        ax.legend(['Брой наблюдения', 'Брой видове'])
        st.pyplot(fig)
    elif plot_option == "Топ 10 на най-често наблюдавани видове":
        bars = ax.bar(top_species.index, top_species.values, color='green')
        ax.bar_label(bars, padding=3)
        ax.set_title(f"Топ 10 на най-много наблюдавани видове от {system_type}")
        ax.set_ylabel("Брой наблюдения")
        ax.set_xlabel("Видове")
        ax.set_xticklabels(top_species.index, rotation=45, ha='right')
        st.pyplot(fig)
    elif plot_option == "Списък на всички отбелязани видове":
        st.write(f"Списък на всички отбелязани видове от {system_type}:")
        if system_type == 'SmartBirds':
            species_list = sorted(df['speciesBg'].unique())
        else:
            species_list = sorted(df['Common Name'].unique())
        st.write(f"Брой видове : {len(species_list)}")
        st.markdown("\n".join(f"- {s}" for s in species_list))
    elif plot_option == "Наблюдения по часове":
        bars = ax.bar(hour_spread.index, hour_spread.values, color='purple')
        fontsize = 8 if len(hour_spread.index) > 10 else 12
        ax.bar_label(bars, padding=3, fontsize=fontsize)
        ax.set_title(f"Наблюдения по часове от {system_type}")
        ax.set_ylabel("Брой наблюдения")
        ax.set_xlabel("Час")
        ax.set_xticks(hour_spread.index)
        ax.set_xticklabels([f"{int(h)}:00" for h in hour_spread.index])
        st.pyplot(fig)
