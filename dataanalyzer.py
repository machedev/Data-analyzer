import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

#st.markdown(
#    """
#    <style>
#    [data-testid="stAppViewContainer"] {
#        background-color: #dbeda1;
#    }
#    </style>
#    """,
#    unsafe_allow_html=True
#)

months = range(1, 13)
month_labels = ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни', 'Юли', 'Август', 'Септември', 'Октомври', 'Ноември', 'Декември']

st.title("Графики и статистики за наблюдения на птици")

uploaded_file = st.file_uploader("Изберете CSV файл", type="csv")
if uploaded_file:

    plot_option = st.selectbox(
        "Избери графика",
        (   "Наблюдения по години",
            "Видове по години",
            "Наблюдения по месеци",
            "Видове по месеци",
            "Наблюдения и видове по месеци",
            "Наблюдения и видове по години",
            "Топ 10 на най-често наблюдавани видове",
            "Списък на всички отбелязани видове"
        )
    )

    # Read first line to determine separator and system type
    first_line = uploaded_file.readline().decode('utf-8').strip()
    separator = ';' if ';' in first_line else ','
    separated_values = first_line.split(separator)
    system_type = 'SmartBirds' if separated_values[0].replace('\ufeff', '').strip().lower() == 'id' else 'eBird'

    # Reset file pointer and read the whole file
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, sep=separator, encoding='utf-8')

    if system_type == 'SmartBirds':
        #df = df[df['speciesBg'] != 'Strix aluco | Горска улулица']
        df.index = pd.to_datetime(df['observationDate'], format='%d.%m.%Y')
        df['speciesBg'] = df['speciesBg'].str.replace(r'^.+\|\s*', '', regex=True).str.strip()
        monthly_counts = df['observationDate'].groupby(df.index.month).count()
        yearly_counts = df['observationDate'].groupby(df.index.year).count()
        unique_species = df.groupby(df.index.month)['speciesBg'].nunique()
        year_unique_species = df.groupby(df.index.year)['speciesBg'].nunique()
        top_species = df['speciesBg'].value_counts().head(10)
    else:
        #df = df[df['State/Province'].str.startswith('BG-')]
        df['Common Name'] = df['Common Name'].str.replace(r'\([^\)]+\)', '', regex=True).str.strip()
        df.index = pd.to_datetime(df['Date'], format='mixed')
        monthly_counts = df['Date'].groupby(df.index.month).count()
        yearly_counts = df['Date'].groupby(df.index.year).count()
        unique_species = df.groupby(df.index.month)['Common Name'].nunique()
        year_unique_species = df.groupby(df.index.year)['Common Name'].nunique()
        top_species = df['Common Name'].value_counts().head(10)

    # Plot
    fig, ax = plt.subplots(figsize=(18, 8))
    values_species = [unique_species.get(m, 0) for m in months]
    values_months = [monthly_counts.get(m, 0) for m in months]

    if plot_option == "Наблюдения по месеци":
        #ax.bar(months, [monthly_counts.get(m, 0) for m in months], color='blue')
        bars1 = ax.bar(months, values_months, width=0.4, color='blue')
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
        bar = ax.bar(yearly_counts.index, yearly_counts.values, width=0.4, color='red')
        ax.bar_label(bar, padding=3)
        ax.set_title(f"Наблюдения по години от {system_type}")
        ax.set_ylabel("Брой наблюдения")
        ax.set_xlabel("Година")
        ax.set_xticks(yearly_counts.index)
        min_val = max(min(yearly_counts.values) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Видове по години":
        bar = ax.bar(year_unique_species.index, year_unique_species.values, width=0.4, color='red')
        ax.bar_label(bar, padding=3)
        ax.set_title(f"Видове по години от {system_type}")
        ax.set_ylabel("Брой видове")
        ax.set_xlabel("Година")
        ax.set_xticks(year_unique_species.index)
        min_val = max(min(year_unique_species.values) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Видове по месеци":
        #bars2 = ax.bar(months, [unique_species.get(m, 0) for m in months], width=0.4, color='orange')
        bars2 = ax.bar(months, values_species, width=0.4, color='orange')
        ax.bar_label(bars2, padding=3)
        ax.set_title(f"Видове по месеци от {system_type}")
        ax.set_ylabel("Брой видове")
        ax.set_xlabel("Месец")
        ax.set_xticks(months)
        ax.set_xticklabels(month_labels)
        # Set y-axis to start from (lowest count - 10), but not below 0
        min_val = max(min(values_species) - 10, 0)
        ax.set_ylim(bottom=min_val)
        st.pyplot(fig)
    elif plot_option == "Наблюдения и видове по месеци":
        bars1 = ax.bar([m - 0.2 for m in months], values_months, width=0.4, label='Брой наблюдения', color='blue')
        bars2 = ax.bar([m + 0.2 for m in months], values_species, width=0.4, label='Брой видове', color='orange')
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
        bars1 = ax.bar([m - 0.2 for m in yearly_counts.index], yearly_counts.values, width=0.4, label='Брой наблюдения', color='blue')
        bars2 = ax.bar([m + 0.2 for m in year_unique_species.index], year_unique_species.values, width=0.4, label='Брой видове', color='orange')
        ax.bar_label(bars1, padding=3)
        ax.bar_label(bars2, padding=3)
        ax.set_title(f"Наблюдения и видове по години от {system_type}")
        ax.set_ylabel("Брой наблюдения и видове")
        ax.set_xlabel("Година")
        ax.set_xticks(yearly_counts.index)
        #ax.set_xticklabels(month_labels)
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
