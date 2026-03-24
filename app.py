import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Kalkulačka hliníkového oplotenia", layout="wide")

# --- DATABÁZA ---
db_stlpiky = {
    "50x60": {"sirka": 50, "min_zas": 15, "max_zas": 17},
    "70x70": {"sirka": 70, "min_zas": 20, "max_zas": 23},
    "Adaptér 40x34": {"sirka": 40, "min_zas": 20, "max_zas": 23},
    "Adaptér 40x60": {"sirka": 40, "min_zas": 20, "max_zas": 23}
}

db_osadenie = {
    "Betónovanie": 600,
    "Na platňu": 15,
    "Do otvoru": 0
}

# --- VIZUÁL ---
st.title("🚧 Kalkulačka hliníkového oplotenia")

with st.sidebar:
    st.header("📐 Vstupné rozmery")
    celkova_dlzka = st.number_input("Celková dĺžka plota (mm)", value=2000, step=100)
    vyska_plota = st.number_input("Čistá výška plota (mm)", value=1200, step=100)
    pozadovana_medzera = st.number_input("Požadovaná medzera (mm)", value=20, step=5)

st.header("⚙️ Výber komponentov")
col1, col2 = st.columns(2)

with col1:
    model_plota = st.selectbox("Model plota", ["Model 20", "Model 40"])
    typ_lamely = st.selectbox("Typ lamely", ["Alkor", "Luna"])
    vyska_lamely = st.selectbox("Výška lamely (mm)", [10, 20, 30, 40, 60, 80, 100, 120, 160, 200], index=6)

with col2:
    typ_stlpika = st.selectbox("Typ stĺpika / adaptér", ["50x60", "70x70", "Adaptér 40x34", "Adaptér 40x60"], index=2)
    sposob_osadenia = st.selectbox("Spôsob osadenia", ["Betónovanie", "Na platňu", "Do otvoru"], index=1)
    ukoncenie_stlpika = st.selectbox("Ukončenie stĺpika", ["Krytka", "Čapica", "Bez ukončenia"])

st.divider()

# --- VÝPOČTY ---
if st.button("Vypočítať materiál", type="primary"):
    
    sirka_stlpika = db_stlpiky[typ_stlpika]["sirka"]
    min_zasunutie = db_stlpiky[typ_stlpika]["min_zas"]
    max_zasunutie = db_stlpiky[typ_stlpika]["max_zas"]
    pridavok_na_osadenie = db_osadenie[sposob_osadenia]
    
    max_osovy_modul = 2000 
    
    # Horizontálna optimalizácia
    cista_dlzka_na_rozdelenie = celkova_dlzka - sirka_stlpika
    idealny_pocet_poli = math.ceil(cista_dlzka_na_rozdelenie / max_osovy_modul) if max_osovy_modul > 0 else 1
    konecny_pocet_stlpikov = idealny_pocet_poli + 1
    konecny_osovy_modul = cista_dlzka_na_rozdelenie / idealny_pocet_poli
    konecna_dlzka_lamely = konecny_osovy_modul - sirka_stlpika + (max_zasunutie * 2)
    
    # Vertikálny výpočet
    pocet_lamiel_do_pola = math.floor((vyska_plota + pozadovana_medzera) / (vyska_lamely + pozadovana_medzera))
    pocet_medzier_v_poli = (pocet_lamiel_do_pola * 2) - 2 
    skutocna_medzera = (vyska_plota - (pocet_lamiel_do_pola * vyska_lamely)) / pocet_medzier_v_poli if pocet_medzier_v_poli > 0 else 0
    dlzka_stlpika_vyroba = vyska_plota + pridavok_na_osadenie
    
    # Celkové množstvá
    celkovy_pocet_lamiel = pocet_lamiel_do_pola * idealny_pocet_poli
    celkovy_pocet_list = pocet_medzier_v_poli * idealny_pocet_poli
    
    # --- DYNAMICKÁ TVORBA TABUĽKY ---
    st.subheader("📋 Výsledný materiál (Kusovník)")
    
    # Vytvoríme prázdny zoznam, do ktorého budeme pridávať len to, čo naozaj treba
    polozky = []
    
    # 1. Základný hliník (Lamely, stĺpiky, lišty)
    polozky.append(["Hliník", f"Lamela {model_plota} ({typ_lamely})", f"Dĺžka: {konecna_dlzka_lamely:.0f} mm", celkovy_pocet_lamiel, "ks"])
    polozky.append(["Hliník", typ_stlpika, f"Dĺžka: {dlzka_stlpika_vyroba:.0f} mm", konecny_pocet_stlpikov, "ks"])
    if celkovy_pocet_list > 0:
        polozky.append(["Hliník", "Krycia lišta", f"Dĺžka: {skutocna_medzera:.1f} mm", celkovy_pocet_list, "ks"])
        
    # 2. Skrutky na lamely
    polozky.append(["Spojovací materiál", "Skrutky na lamely", "Tex 4,2x13 mm", celkovy_pocet_lamiel * 4, "ks"])
    
    # 3. Ukončenie stĺpika (iba ak nie je "Bez ukončenia")
    if ukoncenie_stlpika != "Bez ukončenia":
        polozky.append(["Príslušenstvo", ukoncenie_stlpika, f"Pre profil {typ_stlpika}", konecny_pocet_stlpikov, "ks"])
        polozky.append(["Spojovací materiál", "Skrutky na krytky/čapice", "Torx 4,2x22 mm", konecny_pocet_stlpikov * 2, "ks"])

    # 4. KOTVENIE NA PLATŇU (Logika z tvojho Excelu)
    if sposob_osadenia == "Na platňu":
        polozky.append(["Príslušenstvo", "Platňa pod stĺpik", "", konecny_pocet_stlpikov, "ks"])
        polozky.append(["Spojovací materiál", "Kotva do betónu", "10x120 mm", konecny_pocet_stlpikov * 4, "ks"])
        polozky.append(["Spojovací materiál", "Skrutka so záp. hlavou", "M8x60 (spoj platňa/stĺpik)", konecny_pocet_stlpikov * 4, "ks"])
        
    # Prevedenie do tabuľky
    df_vysledky = pd.DataFrame(polozky, columns=["Kategória", "Názov položky", "Rozmer / Špecifikácia", "Množstvo", "MJ"])
    
    st.dataframe(df_vysledky, use_container_width=True, hide_index=True)
    st.success("✅ Výpočet prebehol úspešne!")
