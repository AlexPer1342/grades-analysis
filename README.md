# 📘 Mokinių pasiekimų analizės aplikacija

Minimalistinis ir interaktyvus Streamlit įrankis, skirtas analizuoti mokinių pažymių ir lankomumo duomenis. Sukurtas siekiant pateikti aiškią, vizualiai patrauklią informaciją mokytojams, klasių vadovams ir administracijai.

---

## 🔍 Pagrindinės funkcijos

- 📂 Įkelkite Excel (.xlsx) failą su mokinių pažymiais ir lankomumu
- 📊 Peržiūrėkite:
  - Vidurkius pagal dalykus
  - Moksleivių vietas klasėje pagal pažymių vidurkį
  - Pasiekimų lygių pasiskirstymą (aukštesnysis, pagrindinis, patenkinamas ir t. t.)
- 🧮 Automatiniai skaičiavimai:
  - Vidurkis, moda, standartinis nuokrypis
  - Mokinių ir įrašų skaičius
- 🧾 PDF ataskaitų generavimas:
  - Bendra klasės analizė
  - Individuali mokinio ataskaita
- 🧠 Automatiškai sugeneruotos rekomendacijos mokiniams pagal pažymių vidurkį
- 📉 Įtraukiama lankomumo statistika
- 🎨 Modernūs grafikai su mėlynais akcentais
- 🔤 Teisingai rodomos lietuviškos raidės PDF ataskaitose

---

## 📦 Priklausomybės

Prieš paleisdami aplikaciją, įdiekite priklausomybes:

```bash
pip install -r requirements.txt
Turinys requirements.txt faile:
streamlit
pandas
matplotlib
reportlab
openpyxl
🚀 Paleidimas
Paleisti lokaliai:
streamlit run grades_app.py
Arba jei failas vadinasi kitaip:
streamlit run streamlit_app.py
🌐 Publikavimas Streamlit Cloud platformoje
Įkelkite projektą į GitHub
Nueikite į https://share.streamlit.io
Prisijunkite naudodami GitHub
Pasirinkite repozitoriją ir nurodykite paleidimo failą (grades_app.py)
Spauskite Deploy ir naudokitės aplikacija internete
📸 Ekrano nuotraukos (nebūtina)
Galite įkelti vizualizacijų pavyzdžius (grafikai, PDF ataskaitos, filtravimo panelės ir pan.)
📝 Licencija
Šis projektas platinamas pagal MIT licenciją. Naudokite, modifikuokite ir pritaikykite savo poreikiams.
