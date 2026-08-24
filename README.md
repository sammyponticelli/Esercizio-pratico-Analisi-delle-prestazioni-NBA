# NBA Impact Analysis

Analisi dell'impatto dei giocatori NBA sulle prestazioni in partita attraverso un indicatore sintetico, denominato **Impact Score**.

L'Impact Score viene calcolato con una formula predefinita nella quale ogni statistica individuale presenta un peso specifico. L'analisi produce **due versioni** dell'indicatore, calcolate in parallelo e confrontate tra loro:

- **`impact_score_game`** — impatto medio *per partita* (misura il volume complessivo di produzione);
- **`impact_score_40`** — impatto normalizzato *per 40 minuti* di gioco (misura l'efficienza per unità di tempo).

---

## Dataset

`nba_players_25_26_regular_season_wide_data.csv` — statistiche individuali della **Regular Season NBA 2025-26** (582 giocatori, 28 variabili).

Variabili principali utilizzate nell'analisi:

| Variabile | Descrizione |
|---|---|
| `player_name` | Nome del giocatore |
| `age_completed_years` | Età (anni compiuti) |
| `team` | Squadra |
| `minutes_played` | Minuti giocati (totali di stagione) |
| `one_point_made`, `two_point_made`, `three_point_made` | Canestri realizzati per tipologia |
| `offensive_rebounds`, `defensive_rebounds` | Rimbalzi offensivi e difensivi |
| `assists`, `steals`, `blocks`, `turnovers` | Assist, palle rubate, stoppate, palle perse |
| `wins`, `losses` | Vittorie e sconfitte (usate per derivare le partite giocate) |

Variabili presenti nel dataset ma **non** utilizzate nel calcolo dell'Impact Score (utili per la ricerca di correlazioni della fase 6):

| Variabile | Descrizione |
|---|---|
| `position` | Ruolo (G / F / C e combinazioni) — sarà reintrodotto nella fase 8 |
| `height_m`, `weight_kg` | Altezza e peso |
| `experience` | Anni di esperienza in NBA |
| `country` | Nazionalità |
| `personal_fouls` | Falli personali |
| `one_point_attempted`, `two_point_attempted`, `three_point_attempted` | Tiri tentati per tipologia (da cui derivare le percentuali di realizzazione) |

I dati sono di stagione (totali): le medie per partita vengono derivate nel corso dell'analisi.

---

## Formula dell'Impact Score

Le statistiche sono espresse come **medie per partita**. Da questa base si ricavano le due versioni dell'indicatore.

**Impact Score per partita:**

```
impact_score_game = PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV
```

**Impact Score normalizzato per 40 minuti:**

```
impact_score_40 = (PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV) / MIN · 40
```

dove:

- `PTS = one_point_made + 2 · two_point_made + 3 · three_point_made`
- `REB = offensive_rebounds + defensive_rebounds`
- `games_played = wins + losses`
- `MIN` = minuti medi per partita

I pesi premiano le giocate a maggiore valore aggiunto (assist, recuperi, stoppate) e penalizzano le palle perse.

Le due versioni rispondono a domande diverse: `impact_score_game` misura **quanto un giocatore produce complessivamente**, ed è quindi legato al minutaggio concesso dall'allenatore; `impact_score_40` rende confrontabili giocatori con minutaggi molto diversi, misurando l'impatto **per unità di tempo**. Il confronto tra le due permette di distinguere i giocatori che producono molto perché giocano molto da quelli che risultano efficienti a prescindere dal tempo in campo.

### Filtro sulle partite giocate

Poiché la normalizzazione per minuti tende a premiare i giocatori con pochissimo utilizzo (campioni molto piccoli), l'analisi considera solo i giocatori che hanno disputato almeno **1/3 delle partite del giocatore più utilizzato** del dataset. Si tratta di una soglia *relativa*: funziona anche su una stagione ancora in corso, senza dover fissare un numero di partite predefinito.

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
Applicazione della formula predefinita, tenendo conto dei diversi pesi assegnati alle statistiche dei giocatori. Prima del calcolo viene applicato il filtro sulle partite giocate. Il risultato viene memorizzato nelle due nuove variabili `impact_score_game` e `impact_score_40`.

### 4. Analisi della Top 10
Ordinamento dei giocatori in base all'Impact Score e individuazione dei 10 giocatori con il punteggio più elevato. Per la Top 10 vengono calcolati **Impact Score medio** ed **età media**. L'analisi viene eseguita separatamente sulle due versioni dell'indicatore, ottenendo così due classifiche distinte.

### 5. Analisi per fascia d'età
Suddivisione dei giocatori nelle fasce **19–22**, **23–26**, **27–30**, **31–34**, **35+** anni. Per ogni fascia: numero di giocatori, Impact Score medio, Impact Score massimo. Anche in questo caso la tabella viene costruita per entrambe le versioni dell'indicatore.

### 6. Ricerca correlazioni significative
Analisi della relazione tra i **minuti giocati** e ciascuna delle due versioni dell'Impact Score: coefficiente di correlazione di Pearson, scatter plot e retta di regressione lineare sovrapposta al grafico.

A completamento della fase viene eseguita una **cluster analysis** (K-Means, 3 cluster, su minuti giocati e Impact Score standardizzati) per individuare gruppi di giocatori con profili simili di utilizzo e impatto. Anche le due cluster analysis vengono prodotte in parallelo, una per versione dell'indicatore.

Il confronto tra le due correlazioni è di per sé un risultato dell'analisi:

| Relazione | Pearson |
|---|---|
| `minutes_played` ↔ `impact_score_game` | **0.76** |
| `minutes_played` ↔ `impact_score_40` | **0.39** |

La correlazione forte sul punteggio per partita conferma che la produzione complessiva dipende in larga misura dal minutaggio; la normalizzazione per 40 minuti ne rimuove buona parte, pur lasciando una correlazione positiva residua — segno che gli allenatori tendono comunque a concedere più minuti ai giocatori più efficienti.

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
- quale relazione esiste tra minuti giocati e Impact Score, e quanto la normalizzazione per 40 minuti modifica il quadro;
- quali altre variabili risultano significativamente correlate con l'Impact Score;
- quale ruolo presenta mediamente il maggiore impatto.

---

## Stato di avanzamento

| Sezione | Stato |
|---|---|
| 1. Esplorazione del dataset | ✅ implementata |
| 2. Pulizia e preparazione dei dati | ✅ implementata |
| 3. Calcolo dell'Impact Score | ✅ implementata — entrambe le versioni (per partita e per 40 minuti) |
| 4. Analisi della Top 10 | ✅ implementata — su entrambe le versioni |
| 5. Analisi per fascia d'età | ✅ implementata — su entrambe le versioni |
| 6. Ricerca correlazioni significative | 🟡 parziale — correlazione minuti/impact, scatter con regressione e cluster analysis implementati per entrambe le versioni; correlazioni con altre variabili da implementare |
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
| `visualize_dataset(data)` | Esplorazione iniziale: `head`, tipi di dato |
| `visualize_impact_dataset(data_impact)` | Costruzione del dataset di lavoro con `games_played`, `PTS`, `REB` |
| `calculate_per_game(data_impact)` | Calcolo delle medie per partita di tutte le statistiche |
| `filter_by_games_played(data_impact)` | Filtro sui giocatori con almeno 1/3 delle partite del più utilizzato |
| `impact_score_40_minutes_calculator(data_impact)` | Formula con normalizzazione per 40 minuti (`impact_score_40`) e ordinamento decrescente |
| `impact_score_game(data_impact)` | Formula sulle medie per partita (`impact_score_game`) e ordinamento decrescente |
| `average_top10_40_calc` / `average_top10_game_calc` | Impact Score medio della Top 10, per ciascuna versione |
| `age_average_40_calc` / `age_average_game_calc` | Età media della Top 10, per ciascuna versione |
| `age_group_40_build` / `age_group_game_build` | Tabella riepilogativa per fascia d'età (numero giocatori, media, massimo) |
| `correlation_minutes_impact_score_40` / `..._game` | Coefficiente di correlazione di Pearson tra minuti giocati e Impact Score |
| `correlation_analysis(data_impact_game, data_impact)` | Raccoglie le due correlazioni in un dizionario |
| `scatter_plot_minutes_impact_score_40` / `..._game` | Scatter plot minuti/Impact Score con retta di regressione lineare |
| `cluster_analysis_minutes_impact_score_40` / `..._game` | Cluster analysis K-Means (3 cluster) su minuti e Impact Score standardizzati |

---

## Tecnologie

- Python
- Pandas
- NumPy
- Matplotlib
- scikit-learn (`StandardScaler`, `KMeans`)
- Seaborn (previsto per la heatmap della matrice di correlazione, non ancora utilizzato)

---

## Come eseguire l'analisi

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
python analisi_nba.py
```

Lo script va eseguito dalla cartella del progetto, dove si trova il file CSV.

L'esecuzione stampa a console le tabelle riepilogative e apre **quattro finestre Matplotlib**: scatter plot e cluster analysis per `impact_score_game`, scatter plot e cluster analysis per `impact_score_40`.

---

## Nota

L'analisi ha finalità esplorative: l'Impact Score rappresenta un indicatore costruito sulla base della formula e dei pesi definiti nel progetto e **non costituisce necessariamente una misura ufficiale dell'impatto utilizzata dalla NBA**.
