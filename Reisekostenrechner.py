import streamlit as st
import math
import pandas as pd
import altair as alt

# ---------------------------------------------------------
# Seiten-Layout konfigurieren
# ---------------------------------------------------------
st.set_page_config(
    page_title="Reisekosten-Rechner Italien",
    layout="wide"
)

# Kleiner CSS-Hack, damit Spalten bei mittlerer Breite nebeneinander bleiben
st.markdown("""
<style>
@media (min-width: 600px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
    }
}
div.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Titel
# ---------------------------------------------------------
st.title("Reisekosten-Rechner Italien")

# ---------------------------------------------------------
# Links: Eingaben & Tabelle / Rechts: Diagramm
# ---------------------------------------------------------
col_left, col_right = st.columns([1,1])

with col_left:
    st.subheader("Eingaben")

    # Eingaben
    anzahl_personen = st.slider("Anzahl Personen", 3, 12, 6)
    anzahl_tage = st.slider("Anzahl Reisetage", 7, 14, 7)
    ski_tage = st.slider("Skitage", 0, anzahl_tage, 0)
    aktivitaeten = st.number_input(
        "Aktivitäten (gesamt in €)",
        min_value=0,
        step=50,
        value=0
    )

    # -----------------------------------------------------
    # Neue Mietwagen-Logik
    # -----------------------------------------------------

    # Festpreis inkl. Tank
    FESTPREIS = 582.0

    def mietwagen_kosten_pro_auto(tage: int) -> float:
        """
        7 Tage = 169,20 €
        Jeder weitere Tag = 28,20 €
        Bei 14 Tagen => 2 × 169,20 €
        """
        if tage <= 7:
            return 169.20
        elif tage < 14:
            return 169.20 + (tage - 7) * 28.20
        else:  # genau 14 Tage
            return 169.20 * 2

    # Anzahl benötigter Autos (max 4 Personen pro Auto)
    autos = math.ceil(anzahl_personen / 4)

    # Gesamte Mietwagenkosten = Festpreis + Zeitkosten
    mietwagen_zeitkosten = mietwagen_kosten_pro_auto(anzahl_tage)
    mietwagen_gesamt = autos * (FESTPREIS + mietwagen_zeitkosten)

    # Mietwagen hat weiterhin keinen Min/Max-Unterschied
    mietwagen_min = mietwagen_gesamt
    mietwagen_max = mietwagen_gesamt

    # Unterkunft (10–15 €/Nacht/Person, ab 9. Person kostenfrei)
    zahlende_personen = min(anzahl_personen, 8)
    unterkunft_min = 10 * zahlende_personen * anzahl_tage
    unterkunft_max = 15 * zahlende_personen * anzahl_tage

    # Verpflegung (10–15 €/Tag/Person)
    verpflegung_min = 10 * anzahl_personen * anzahl_tage
    verpflegung_max = 15 * anzahl_personen * anzahl_tage

    # Skikosten (60 €/Tag/Person)
    skikosten_min = 60 * ski_tage * anzahl_personen
    skikosten_max = skikosten_min

    # Aktivitäten
    akt_min = aktivitaeten
    akt_max = aktivitaeten

    # Summen min / max
    gesamt_min = (
        mietwagen_min + unterkunft_min
        + verpflegung_min + skikosten_min + akt_min
    )
    gesamt_max = (
        mietwagen_max + unterkunft_max
        + verpflegung_max + skikosten_max + akt_max
    )

    # Pro Person
    if anzahl_personen > 0:
        gesamt_min_pp = gesamt_min / anzahl_personen
        gesamt_max_pp = gesamt_max / anzahl_personen
    else:
        gesamt_min_pp = 0
        gesamt_max_pp = 0

    # -----------------------------------------------------
    # Tabelle
    # Kategorie | Gesamt max. | Gesamt min. | p.P. max | p.P. min
    # -----------------------------------------------------
    st.subheader("Kostenübersicht (Tabelle)")

    def fmt(euro):
        return f"{euro:,.0f} €"

    table_data = [
        {
            "Kategorie": "Mietwagen",
            "Gesamt max.": fmt(mietwagen_max),
            "Gesamt min.": fmt(mietwagen_min),
            "p.P. max": fmt(mietwagen_max / anzahl_personen if anzahl_personen else 0),
            "p.P. min": fmt(mietwagen_min / anzahl_personen if anzahl_personen else 0),
        },
        {
            "Kategorie": "Unterkunft",
            "Gesamt max.": fmt(unterkunft_max),
            "Gesamt min.": fmt(unterkunft_min),
            "p.P. max": fmt(unterkunft_max / anzahl_personen if anzahl_personen else 0),
            "p.P. min": fmt(unterkunft_min / anzahl_personen if anzahl_personen else 0),
        },
        {
            "Kategorie": "Verpflegung",
            "Gesamt max.": fmt(verpflegung_max),
            "Gesamt min.": fmt(verpflegung_min),
            "p.P. max": fmt(verpflegung_max / anzahl_personen if anzahl_personen else 0),
            "p.P. min": fmt(verpflegung_min / anzahl_personen if anzahl_personen else 0),
        },
        {
            "Kategorie": "Skikosten",
            "Gesamt max.": fmt(skikosten_max),
            "Gesamt min.": fmt(skikosten_min),
            "p.P. max": fmt(skikosten_max / anzahl_personen if anzahl_personen else 0),
            "p.P. min": fmt(skikosten_min / anzahl_personen if anzahl_personen else 0),
        },
        {
            "Kategorie": "Aktivitäten",
            "Gesamt max.": fmt(akt_max),
            "Gesamt min.": fmt(akt_min),
            "p.P. max": fmt(akt_max / anzahl_personen if anzahl_personen else 0),
            "p.P. min": fmt(akt_min / anzahl_personen if anzahl_personen else 0),
        },
        {
            "Kategorie": "Gesamt",
            "Gesamt max.": fmt(gesamt_max),
            "Gesamt min.": fmt(gesamt_min),
            "p.P. max": fmt(gesamt_max_pp),
            "p.P. min": fmt(gesamt_min_pp),
        },
    ]

    st.table(table_data)

with col_right:
    st.subheader("Diagramm: Kosten pro Person (Stacked Min + (Max-Min))")

    # Für das Diagramm: Gestapelte Balken (Min + Delta)
    def to_delta_rows(cat: str, min_val: float, max_val: float) -> list:
        """Erzeugt 2 Zeilen für eine Kategorie:
           1) Min
           2) Delta (max - min)"""
        delta = max_val - min_val
        if delta < 0:
            delta = 0
        return [
            {"Kategorie": cat, "Typ": "Min", "Wert": min_val if min_val >= 0 else 0},
            {"Kategorie": cat, "Typ": "Delta", "Wert": delta},
        ]

    df_stack = []
    def val_pp(x):  # Hilfsfunktion: Kosten pro Person oder 0
        return x / anzahl_personen if anzahl_personen else 0

    # Mietwagen
    df_stack += to_delta_rows("Mietwagen", val_pp(mietwagen_min), val_pp(mietwagen_max))
    # Unterkunft
    df_stack += to_delta_rows("Unterkunft", val_pp(unterkunft_min), val_pp(unterkunft_max))
    # Verpflegung
    df_stack += to_delta_rows("Verpflegung", val_pp(verpflegung_min), val_pp(verpflegung_max))
    # Skikosten
    df_stack += to_delta_rows("Skikosten", val_pp(skikosten_min), val_pp(skikosten_max))
    # Aktivitäten
    df_stack += to_delta_rows("Aktivitäten", val_pp(akt_min), val_pp(akt_max))
    # Gesamt
    df_stack += to_delta_rows("Gesamt", gesamt_min_pp, gesamt_max_pp)

    df_stacked = pd.DataFrame(df_stack)

    # Altair Stacked Bar Chart
    chart = (
        alt.Chart(df_stacked)
        .mark_bar()
        .encode(
            x=alt.X("Kategorie:N", title="", sort=None),
            y=alt.Y("Wert:Q", title="Kosten pro Person (€)", stack="zero"),
            color=alt.Color("Typ:N", legend=alt.Legend(title="Anteil")),
            tooltip=["Kategorie:N", "Typ:N", "Wert:Q"]
        )
        .properties(width=500, height=400)
    )

    st.altair_chart(chart, use_container_width=True)
