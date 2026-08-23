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

Variabili presenti nel dataset ma **non** utilizzate nel calcolo dell'Impact Score (utili per la ricerca di correlazioni della fase 6):

| Variabile | Descrizione |
|---|---|
| `height_m`, `weight_kg` | Altezza e peso |
| `experience` | Anni di esperienza in NBA |
| `country` | Nazionalità |
| `personal_fouls` | Falli personali |
| `one_point_attempted`, `two_point_attempted`, `three_point_attempted` | Tiri tentati per tipologia (da cui derivare le percentuali di realizzazione) |

I dati sono di stagione (totali): le medie per partita vengono derivate nel corso dell'analisi.

---

## Formula dell'Impact Score

Le statistiche sono espresse come **medie per partita** e il risultato viene poi **normalizzato per 40 minuti** di gioco:

```
Impact_Score = (PTS + 1.2 · REB + 1.5 · AST + 2 · STL + 2 · BLK − TOV) / MIN · 40
```

dove:

- `PTS = one_point_made + 2 · two_point_made + 3 · three_point_made`
- `REB = offensive_rebounds + defensive_rebounds`
- `games_played = wins + losses`
- `MIN` = minuti medi per partita

I pesi premiano le giocate a maggiore valore aggiunto (assist, recuperi, stoppate) e penalizzano le palle perse. La normalizzazione per 40 minuti rende confrontabili giocatori con minutaggi molto diversi, misurando l'impatto **per unità di tempo** anziché il volume complessivo di produzione.

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
Applicazione della formula predefinita, tenendo conto dei diversi pesi assegnati alle statistiche dei giocatori e della normalizzazione per 40 minuti. Prima del calcolo viene applicato il filtro sulle partite giocate. Il risultato viene memorizzato nella nuova variabile `impact_score`.

### 4. Analisi della Top 10
Ordinamento dei giocatori in base all'Impact Score e individuazione dei 10 giocatori con il punteggio più elevato. Per la Top 10 vengono calcolati **Impact Score medio** ed **età media**.

### 5. Analisi per fascia d'età
Suddivisione dei giocatori nelle fasce **19–22**, **23–26**, **27–30**, **31–34**, **35+** anni. Per ogni fascia: numero di giocatori, Impact Score medio, Impact Score massimo, età media.

### 6. Ricerca correlazioni significative
Scatter plot, coefficiente di correlazione di Pearson e analisi della relazione tra le due variabili, con retta di regressione lineare sovrapposta al grafico.

A completamento della fase è prevista una **cluster analysis** (K-Means su età e Impact Score standardizzati, 3 cluster) per individuare gruppi di giocatori con profili simili di età e impatto.

La fase comprende inoltre la **ricerca di correlazioni significative tra l'Impact Score e variabili diverse da quelle già utilizzate nella sua formula** (da implementare). Le statistiche che compongono l'Impact Score (punti, rimbalzi, assist, recuperi, stoppate, palle perse) sono escluse per costruzione, perché correlate con esso per definizione.

Variabili candidate:

- `height_m` e `weight_kg` — caratteristiche fisiche;
- `experience` — anni di esperienza in NBA (da confrontare con l'età, con cui è collineare);
- `personal_fouls` (per partita o per 40 minuti) — aggressività / disciplina difensiva;
- percentuali di realizzazione derivate dai tiri tentati (`*_made / *_attempted`) — efficienza al tiro;
- `minutes_played` / minuti per partita — utilizzo da parte dell'allenatore;
- `games_played` — continuità e disponibilità;
- variabili categoriali come `position`, `team` o `country`, da trattare con confronti tra gruppi anziché con la correlazione di Pearson.

Approccio previsto:

1. costruire le variabili derivate necessarie (percentuali al tiro, falli per 40 minuti, ecc.);
2. calcolare la matrice di correlazione tra `impact_score` e le variabili candidate, visualizzandola con una heatmap;
3. selezionare le correlazioni più forti e rappresentarle con scatter plot e retta di regressione;
4. valutare la **significatività statistica** (p-value) oltre all'intensità del coefficiente, per distinguere le relazioni reali da quelle casuali;
5. commentare i risultati, tenendo presente che la correlazione non implica un rapporto di causa-effetto.

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
- quali altre variabili risultano significativamente correlate con l'Impact Score;
- quale ruolo presenta mediamente il maggiore impatto.

---

## Stato di avanzamento

| Sezione | Stato |
|---|---|
| 1. Esplorazione del dataset | ✅ implementata |
| 2. Pulizia e preparazione dei dati | ✅ implementata |
| 3. Calcolo dell'Impact Score | ✅ implementata |
| 4. Analisi della Top 10 | ✅ implementata |
| 5. Analisi per fascia d'età | ✅ implementata |
| 6. Ricerca correlazioni significative | 🟡 parziale — scatter, correlazione età/impact, regressione e cluster analysis implementati; correlazioni con altre variabili da implementare |
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
| `impact_score_calculator(data_impact)` | Applicazione della formula, normalizzazione per 40 minuti e ordinamento decrescente |
| `average_top10_calc(data_impact)` | Impact Score medio della Top 10 |
| `age_average_calc(data_impact)` | Età media della Top 10 |
| `age_group_build(data_impact)` | Tabella riepilogativa per fascia d'età (numero giocatori, media, massimo) |
| `correlation_age_impact_score(data_impact)` | Coefficiente di correlazione di Pearson tra età e Impact Score |
| `scatter_plot_age_impact_score(data_impact, correlation)` | Scatter plot con retta di regressione lineare |
| `cluster_analysis_build(data_impact)` | Cluster analysis K-Means (3 cluster) su età e Impact Score standardizzati |

---

## Tecnologie

- Python
- Pandas
- NumPy
- Matplotlib
- scikit-learn (`StandardScaler`, `KMeans`)
- Seaborn

---

## Come eseguire l'analisi

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
python analisi_nba.py
```

Lo script va eseguito dalla cartella del progetto, dove si trova il file CSV.

---

## Nota

L'analisi ha finalità esplorative: l'Impact Score rappresenta un indicatore costruito sulla base della formula e dei pesi definiti nel progetto e **non costituisce necessariamente una misura ufficiale dell'impatto utilizzata dalla NBA**.
