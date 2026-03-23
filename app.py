import streamlit as st
import pandas as pd
import math

# Nastavenie vzhľadu stránky
st.set_page_config(page_title="Kalkulačka hliníkového oplotenia", layout="wide")

# --- DATABÁZA VLOŽENÁ PRIAMO DO KÓDU ---
# 1. Parametre stĺpikov (Šírka v osi, Min. zasunutie, Max. zasunutie)
db_stlpiky = {
    "50x60": {"sirka": 50, "min_zas": 15, "max_zas": 17},
    "70x70": {"sirka": 70, "min_zas": 20, "max_zas": 23},
    "Adaptér 40x34": {"sirka": 40, "min_zas": 20, "max_zas": 23},
    "Adaptér 40x60": {"sirka": 40, "min_zas": 20, "max_zas": 23}
}

# 2. Prídavky na osadenie (v mm)
db_osadenie = {
    "Betónovanie": 600,
    "Na platňu": 15,
    "Do otvoru": 0
}

# ----------------------------------------
# VIZUÁL A ROZHRANIE APLIKÁCIE
# ----------------------------------------
st.title("🚧 Kalkulačka hliníkového oplotenia")
st.write("Zadajte rozmery a vyberte komponenty pre automatický výpočet materiálu.")

# Bočný panel (Základné rozmery)
with st.sidebar:
    st.header("📐 Vstupné rozmery")
    celkova_dlzka = st.number_input("Celková dĺžka plota (mm)", value=2000, step=100)
    vyska_plota = st.number_input("Čistá výška plota (mm)", value=1200, step=100)
    pozadovana_medzera = st.number_input("Požadovaná medzera (mm)", value=20, step=5)

# Hlavná časť (Výber komponentov)
st.header("⚙️ Výber komponentov")

col1, col2 = st.columns(2)

with col1:
    model_plota = st.selectbox("Model plota", ["Model 20", "Model 40"])
    typ_lamely = st.selectbox("Typ lamely", ["Alkor", "Luna"])
    vyska_lamely = st.selectbox("Výška lamely (mm)", [10, 20, 30, 40, 60, 80, 100, 120, 160, 200], index=6)

with col2:
    typ_stlpika = st.selectbox("Typ stĺpika / adaptér", ["50x60", "70x70", "Adaptér 40x34", "Adaptér 40x60"], index=2)
    sposob_osadenia = st.selectbox("Spôsob osadenia", ["Betónovanie", "Na platňu", "Do otvoru"], index=2)
    ukoncenie_stlpika = st.selectbox("Ukončenie stĺpika", ["Krytka", "Čapica", "Bez ukončenia"])

st.divider()

# ----------------------------------------
# VÝPOČTOVÁ LOGIKA
# ----------------------------------------
if st.button("Vypočítať materiál", type="primary"):
    
    # Načítanie hodnôt z databázy na základe výberu používateľa
    sirka_stlpika = db_stlpiky[typ_stlpika]["sirka"]
    min_zasunutie = db_stlpiky[typ_stlpika]["min_zas"]
    max_zasunutie = db_stlpiky[typ_stlpika]["max_zas"]
    pridavok_na_osadenie = db_osadenie[sposob_osadenia]
    
    max_osovy_modul = 2000 # Pevná hodnota z Excelu
    
    # --- HORIZONTÁLNA OPTIMALIZÁCIA ---
    cista_dlzka_na_rozdelenie = celkova_dlzka - sirka_stlpika
    
    # Ochrana proti deleniu nulou
    if max_osovy_modul > 0:
        idealny_pocet_poli = math.ceil(cista_dlzka_na_rozdelenie / max_osovy_modul)
    else:
        idealny_pocet_poli = 1
        
    konecny_pocet_stlpikov = idealny_pocet_poli + 1
    konecny_osovy_modul = cista_dlzka_na_rozdelenie / idealny_pocet_poli
    
    # Výpočet lamely (simulácia tvojej excel logiky pre 1966mm)
    konecna_dlzka_lamely = konecny_osovy_modul - sirka_stlpika + (max_zasunutie * 2)
    
    # --- VERTIKÁLNY VÝPOČET ---
    # ROUNDDOWN vzorec
    pocet_lamiel_do_pola = math.floor((vyska_plota + pozadovana_medzera) / (vyska_lamely + pozadovana_medzera))
    
    # Medzery a lišty
    pocet_medzier_v_poli = (pocet_lamiel_do_pola * 2) - 2 
    if pocet_medzier_v_poli > 0:
        skutocna_medzera = (vyska_plota - (pocet_lamiel_do_pola * vyska_lamely)) / pocet_medzier_v_poli
    else:
        skutocna_medzera = 0
        
    dlzka_stlpika_vyroba = vyska_plota + pridavok_na_osadenie
    
    # --- CELKOVÉ MNOŽSTVÁ ---
    celkovy_pocet_lamiel = pocet_lamiel_do_pola * idealny_pocet_poli
    celkovy_pocet_list = pocet_medzier_v_poli * idealny_pocet_poli
    
    # Skrutky (ukážka hrubého výpočtu)
    skrutky_na_lamely = celkovy_pocet_lamiel * 4
    skrutky_na_krytky = konecny_pocet_stlpikov * 2
    
    # ----------------------------------------
    # ZOBRAZENIE VÝSLEDKOV
    # ----------------------------------------
    st.subheader("📋 Výsledný materiál (Kusovník)")
    
    # Dáta pre finálnu tabuľku
    vysledky_data = {
        "Kategória": ["Hliník", "Hliník", "Hliník", "Krytka stĺpika", "Spojovací materiál", "Spojovací materiál"],
        "Názov položky": [f"Lamela {model_plota} ({typ_lamely})", typ_stlpika, "Krycia lišta", ukoncenie_stlpika, "Skrutky na lamely", "Skrutky na krytky"],
        "Rozmer / Špecifikácia": [f"Dĺžka: {konecna_dlzka_lamely:.0f} mm", f"Dĺžka: {dlzka_stlpika_vyroba:.0f} mm", f"Dĺžka: {skutocna_medzera:.1f} mm", f"Pre profil {typ_stlpika}", "Tex 4,2x13 mm", "Torx 4,2x22 mm"],
        "Množstvo": [celkovy_pocet_lamiel, konecny_pocet_stlpikov, celkovy_pocet_list, konecny_pocet_stlpikov, skrutky_na_lamely, skrutky_na_krytky],
        "MJ": ["ks", "ks", "ks", "ks", "ks", "ks"]
    }
    
    df_vysledky = pd.DataFrame(vysledky_data)
    
    # Zobrazenie úhľadnej tabuľky
    st.dataframe(df_vysledky, use_container_width=True, hide_index=True)
    
    st.success("✅ Výpočet prebehol úspešne!")
