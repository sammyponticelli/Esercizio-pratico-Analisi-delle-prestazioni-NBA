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
| `position` | Ruolo (G / F / C e combinazioni) — non entra nella formula, ma è la variabile di raggruppamento della fase 8 |

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
Confronto dei giocatori della Top 10 attraverso le principali statistiche individuali (`PTS`, `REB`, `AST`, `STL`, `BLK`, `TOV`, `MIN` medi per partita), con una tabella comparativa per ciascuna versione dell'indicatore e due **bar chart** delle rispettive Top 10.

Tabelle e grafici sono costruiti sul dataset **filtrato** dalla fase 3, quindi le classifiche coincidono con quelle della fase 4. Le due tabelle sono indipendenti l'una dall'altra: ciascuna lavora su una propria copia del dataset filtrato.

### 8. Analisi dell'Impact Score per ruolo
Impact Score medio raggruppato per ruolo (`position`), calcolato su entrambe le versioni dell'indicatore, con **bar chart affiancato** che mette a confronto le due medie ruolo per ruolo (ruoli ordinati lungo il continuum guardia → centro: `G`, `G-F`, `F-G`, `F`, `F-C`, `C-F`, `C`).

Risultati:

| Ruolo | Impact Score per partita | Impact Score per 40 minuti |
|---|---|---|
| `G` | 19.74 | 33.96 |
| `G-F` | 20.61 | 33.27 |
| `F-G` | **28.54** | 38.49 |
| `F` | 18.63 | 34.18 |
| `F-C` | 21.87 | 38.84 |
| `C-F` | 24.45 | **41.72** |
| `C` | 22.21 | 40.44 |

Il confronto tra le due colonne cambia la lettura: per partita il valore più alto è quello degli `F-G`, ma si tratta di un gruppo poco numeroso e trainato dai minutaggi elevati dei suoi giocatori di punta; una volta normalizzato per 40 minuti l'impatto si sposta stabilmente verso i ruoli interni (`C-F`, `C`, `F-C`), coerentemente con il peso che la formula assegna a rimbalzi e stoppate.

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
| 7. Confronto tra i giocatori | ✅ implementata — tabelle comparative e bar chart delle Top 10, su entrambe le versioni |
| 8. Impact Score per ruolo | ✅ implementata — medie per ruolo e bar chart di confronto tra le due versioni |
| 9. Conclusioni | 🔜 da implementare |

---

## Struttura del progetto

```
nba_analysis_exercise/
├── analisi_nba.py                                    # script di analisi
├── nba_players_25_26_regular_season_wide_data.csv    # dataset
├── .gitignore
└── README.md
```

### Funzioni principali (`analisi_nba.py`)

| Funzione | Descrizione |
|---|---|
| `explore_dataset(raw_data)` | Esplorazione iniziale: `head`, tipi di dato |
| `build_season_totals(season_stats)` | Vista dei totali di stagione con `games_played`, `PTS`, `REB` |
| `calculate_per_game_averages(season_stats)` | Calcolo delle medie per partita di tutte le statistiche |
| `filter_by_games_played(per_game_stats)` | Filtro sui giocatori con almeno 1/3 delle partite del più utilizzato |
| `calculate_impact_score_40(qualified_players)` | Formula con normalizzazione per 40 minuti (`impact_score_40`) e ordinamento decrescente |
| `calculate_impact_score_game(qualified_players)` | Formula sulle medie per partita (`impact_score_game`) e ordinamento decrescente |
| `calculate_top10_average_score_40` / `..._game` | Impact Score medio della Top 10, per ciascuna versione |
| `calculate_top10_average_age_40` / `..._game` | Età media della Top 10, per ciascuna versione |
| `build_age_group_table_40` / `..._game` | Tabella riepilogativa per fascia d'età (numero giocatori, media, massimo) |
| `calculate_minutes_correlation_40` / `..._game` | Coefficiente di correlazione di Pearson tra minuti giocati e Impact Score |
| `collect_correlations(ranking_game, ranking_40)` | Raccoglie le due correlazioni in un dizionario |
| `plot_minutes_vs_score_40` / `..._game` | Scatter plot minuti/Impact Score con retta di regressione lineare |
| `plot_cluster_analysis_40` / `..._game` | Cluster analysis K-Means (3 cluster) su minuti e Impact Score standardizzati |
| `build_top10_comparison_game` / `..._40` | Tabella comparativa della Top 10 con le statistiche medie per partita |
| `plot_top10_bar_chart_40` / `..._game` | Bar chart della Top 10 per ciascuna versione dell'indicatore |
| `calculate_score_by_position_game` / `..._40` | Impact Score medio per ruolo, ordinato in senso decrescente |
| `plot_position_comparison(scores_game, scores_40)` | Bar chart affiancato delle due medie per ruolo, con ruoli ordinati da `G` a `C` |

Convenzione dei nomi: le funzioni iniziano con un verbo (`calculate_`, `build_`, `plot_`, `filter_`, `explore_`), le variabili sono sostantivi. Le funzioni che esistono in due versioni portano il suffisso `_game` o `_40`. I DataFrame che attraversano l'analisi si chiamano `season_stats` (totali di stagione) → `per_game_stats` (medie per partita) → `qualified_players` (dopo il filtro) → `ranking_game` / `ranking_40` (con l'Impact Score calcolato e ordinato).

### Note implementative

Scelte ricorrenti nel codice, raccolte qui per tenere i commenti nel file al minimo.

**Copie difensive.** Ogni funzione di analisi apre con una `.copy()` del DataFrame ricevuto e lavora sulla copia: il DataFrame del chiamante conserva le sue colonne originali, così le funzioni possono essere richiamate in qualunque ordine senza dipendere l'una dall'altra.

**Divisioni per zero.** Le medie non vengono mai calcolate su un denominatore nullo. Prima di dividere, il denominatore passa per `.where(colonna > 0)`, che trasforma gli zeri in `NaN`: un giocatore con 0 partite (o 0 minuti) esce dall'analisi come dato mancante invece di generare un `inf`.

**Valori mancanti nei grafici.** `np.polyfit` restituisce coefficienti `NaN` se anche una sola riga è incompleta, e `KMeans` non accetta `NaN` del tutto: entrambe le funzioni fanno quindi `dropna` sulle due colonne che usano prima di calcolare.

**Retta di regressione.** La retta viene tracciata su `np.sort(x.unique())` e non sulla `x` originale: senza ordinare, `plot` ripercorre la linea avanti e indietro seguendo l'ordine delle righe.

**Figure separate.** Ogni funzione grafica apre la propria `plt.figure()` prima di disegnare, altrimenti i grafici finirebbero sovrapposti sugli stessi assi.

**Standardizzazione prima del K-Means.** Minuti e Impact Score vivono su scale diverse: senza `StandardScaler` la distanza euclidea sarebbe dominata dai minuti. Il numero di cluster (3) è quello con il miglior silhouette score su questo dataset, e `random_state=42` rende i cluster identici a ogni esecuzione.

**`minutes_played` nascosto ma presente.** La colonna resta nei DataFrame perché correlazioni, scatter plot e cluster analysis sono costruiti su di essa; viene tolta solo al momento della `print`, per non appesantire le tabelle a console.

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

L'esecuzione stampa a console le tabelle riepilogative e apre **sette finestre Matplotlib**:

| # | Grafico |
|---|---|
| 1 | Scatter plot minuti / `impact_score_40` con retta di regressione |
| 2 | Scatter plot minuti / `impact_score_game` con retta di regressione |
| 3 | Cluster analysis su minuti e `impact_score_40` |
| 4 | Cluster analysis su minuti e `impact_score_game` |
| 5 | Bar chart Top 10 per `impact_score_40` |
| 6 | Bar chart Top 10 per `impact_score_game` |
| 7 | Bar chart di confronto dell'Impact Score medio per ruolo |

Il main program è diviso in due blocchi: prima tutte le tabelle stampate a console nell'ordine delle fasi 1-8, poi tutti i grafici raggruppati per tipo (i due scatter, i due cluster, le due Top 10, il confronto per ruolo). Le finestre si aprono tutte insieme su `plt.show()`, quindi tenerle raggruppate rende prevedibile l'ordine in cui compaiono.

---

## Nota

L'analisi ha finalità esplorative: l'Impact Score rappresenta un indicatore costruito sulla base della formula e dei pesi definiti nel progetto e **non costituisce necessariamente una misura ufficiale dell'impatto utilizzata dalla NBA**.
