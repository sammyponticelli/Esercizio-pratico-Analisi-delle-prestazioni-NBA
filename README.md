# NBA Impact Analysis

Analisi dell'impatto dei giocatori NBA sulle prestazioni in partita attraverso un indicatore sintetico, denominato **Impact Score**.

L'Impact Score viene calcolato con una formula predefinita nella quale ogni statistica individuale presenta un peso specifico.

---

## Dataset

`nba_players_25_26_regular_season_wide_data.csv` — statistiche individuali della **Regular Season NBA 2025-26** (582 giocatori, 28 variabili).

Variabili principali utilizzate nell'analisi:

| Variabile | Descrizione |
|---|---|
| `player_name` | Nome del giocatore |
| `age_completed_years` | Età (anni compiuti) |
| `team` | Squadra |
| `position` | Ruolo (G / F / C e combinazioni) |
| `minutes_played` | Minuti giocati (totali di stagione) |
| `one_point_made`, `two_point_made`, `three_point_made` | Canestri realizzati per tipologia |
| `offensive_rebounds`, `defensive_rebounds` | Rimbalzi offensivi e difensivi |
| `assists`, `steals`, `blocks`, `turnovers` | Assist, palle rubate, stoppate, palle perse |
| `wins`, `losses` | Vittorie e sconfitte (usate per derivare le partite giocate) |

I dati sono di stagione (totali): le medie per partita vengono derivate nel corso dell'analisi.

---

## Formula dell'Impact Score

Tutte le statistiche sono espresse come **medie per partita**:

```
Impact_Score = PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV
```

dove:

- `PTS = one_point_made + 2 · two_point_made + 3 · three_point_made`
- `REB = offensive_rebounds + defensive_rebounds`
- `games_played = wins + losses`

I pesi premiano le giocate a maggiore valore aggiunto (assist, recuperi, stoppate) e penalizzano le palle perse.

---

## Struttura dell'analisi

### 1. Esplorazione del dataset
Analisi della struttura del dataset, individuazione delle variabili disponibili, analisi dei tipi di dati, controllo di valori mancanti e duplicati.

### 2. Pulizia e preparazione dei dati
Gestione dei valori mancanti, eliminazione di eventuali duplicati, conversione delle variabili nei formati appropriati e preparazione dei dati necessari all'analisi.

Scelte adottate:
- valori mancanti in `wins` / `losses` trattati come 0 partite giocate;
- giocatori con 0 partite giocate esclusi dal calcolo delle medie (`NaN` invece di divisione per zero).

### 3. Calcolo dell'Impact Score
Applicazione della formula predefinita, tenendo conto dei diversi pesi assegnati alle statistiche dei giocatori. Il risultato viene memorizzato nella nuova variabile `impact_score`.

### 4. Analisi della Top 10
Ordinamento dei giocatori in base all'Impact Score e individuazione dei 10 giocatori con il punteggio più elevato. Per la Top 10 vengono calcolati **Impact Score medio** ed **età media**.

### 5. Analisi per fascia d'età
Suddivisione dei giocatori nelle fasce **19–22**, **23–26**, **27–30**, **31–34**, **35+** anni. Per ogni fascia: numero di giocatori, Impact Score medio, Impact Score massimo, età media.

### 6. Relazione tra età e Impact Score
Scatter plot, coefficiente di correlazione e analisi della relazione tra le due variabili.

### 7. Confronto tra i giocatori
Confronto dei giocatori della Top 10 attraverso le principali statistiche individuali, con tabella comparativa e visualizzazione degli Impact Score.

### 8. Analisi dell'Impact Score per ruolo
Analisi dell'Impact Score medio in relazione al ruolo (`position`), per individuare eventuali differenze di impatto tra i diversi ruoli.

### 9. Conclusioni
I risultati vengono utilizzati per determinare:
- quali giocatori presentano il maggiore impatto;
- qual è l'Impact Score medio dei migliori giocatori;
- qual è la loro età media;
- quale fascia d'età presenta il maggiore Impact Score;
- quale relazione esiste tra età e Impact Score;
- quale ruolo presenta mediamente il maggiore impatto.

---

## Stato di avanzamento

| Sezione | Stato |
|---|---|
| 1. Esplorazione del dataset | ✅ implementata |
| 2. Pulizia e preparazione dei dati | ✅ implementata |
| 3. Calcolo dell'Impact Score | ✅ implementata |
| 4. Analisi della Top 10 | ✅ implementata |
| 5. Analisi per fascia d'età | 🔜 da implementare |
| 6. Relazione tra età e Impact Score | 🔜 da implementare |
| 7. Confronto tra i giocatori | 🔜 da implementare |
| 8. Impact Score per ruolo | 🔜 da implementare |
| 9. Conclusioni | 🔜 da implementare |

---

## Struttura del progetto

```
nba_analysis_exercise/
├── analisi_nba.py                                    # script di analisi
├── nba_players_25_26_regular_season_wide_data.csv    # dataset
└── README.md
```

### Funzioni principali (`analisi_nba.py`)

| Funzione | Descrizione |
|---|---|
| `visualize_dataset(data)` | Esplorazione iniziale: `head`, `tail`, tipi di dato |
| `visualize_impact_dataset(data_impact)` | Costruzione del dataset di lavoro con `games_played`, `PTS`, `REB` |
| `calculate_per_game(data_impact)` | Calcolo delle medie per partita di tutte le statistiche |
| `impact_score_calculator(data_impact)` | Applicazione della formula e ordinamento decrescente |
| `average_top10_calc(data_impact)` | Impact Score medio della Top 10 |
| `age_average_calc(data_impact)` | Età media della Top 10 |

---

## Tecnologie

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook

---

## Come eseguire l'analisi

```bash
pip install pandas numpy matplotlib seaborn
python analisi_nba.py
```

Lo script va eseguito dalla cartella del progetto, dove si trova il file CSV.

---

## Nota

L'analisi ha finalità esplorative: l'Impact Score rappresenta un indicatore costruito sulla base della formula e dei pesi definiti nel progetto e **non costituisce necessariamente una misura ufficiale dell'impatto utilizzata dalla NBA**.
