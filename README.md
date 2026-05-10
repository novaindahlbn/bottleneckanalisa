# ProcessMining — Enterprise Batch Job Process Mining Dashboard

Generic Process Mining untuk analisis backend batch job di sistem Enterprise.

---

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt

# Install graphviz (untuk Heuristic Net visualization)
# Windows:  choco install graphviz  ATAU  download dari https://graphviz.org/download/
# Mac:      brew install graphviz
# Linux:    apt-get install graphviz
```

### 2. Jalankan aplikasi
```bash
python -m streamlit run processmining_app.py
```

### 3. Buka browser
Aplikasi otomatis terbuka di `http://localhost:8501`


## Tahapan Proses Mining
### Process Discovery
- Heuristic Net (model proses visual)
- Tabel varian proses + frekuensi
- Distribusi durasi case

### Conformance Checking
- Average Trace Fitness (0-1)
- Precision (0-1)  
- % Trace yang sepenuhnya fit
- Top deviasi: Log Moves & Model Moves

### Bottleneck Analysis
- **Total Time Ranking** — aktivitas dengan beban waktu kumulatif tertinggi
- **Frequency Ranking** — aktivitas yang paling sering dieksekusi
- **Mean Duration Ranking** — aktivitas yang paling lambat per eksekusi
- **Transition Delay** — pasangan aktivitas A→B dengan delay terpanjang
