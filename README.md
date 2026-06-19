# Modelització probabilística en futbol internacional: el cas del Mundial 2026

Treball Final de Grau del **Grau en Matemàtica Computacional i Analítica de Dades** (UAB).

- **Autor:** Sergi Almendros Montoya
- **Coautor:** Llorenç Badiella Busquets
- **Data:** Juny de 2026

## Resum

Aquest projecte desenvolupa un model probabilístic per al futbol internacional deseleccions amb l'objectiu d'estimar la probabilitat de cada selecció de guanyar la Copa del Món de 2026. El model estén el sistema ELO clàssic de tres maneres:

1. Descompon la força de cada selecció en una component **ofensiva** i una **defensiva**.
2. Modela els gols com dues distribucions de **Poisson independents**.
3. Incorpora un **rating de confederació** amb propagació intercontinental.

Els paràmetres s'estimen amb un algorisme iteratiu inspirat en *Expectation–Maximization*, i la Copa del Món 2026 es simula **100.000 vegades** pel mètode de Monte Carlo per obtenir les probabilitats de cada selecció a cada fase del torneig.

## Resultats principals

| Selecció    | P(Campió) |
|-------------|-----------|
| Espanya     | 17,6 %    |
| Anglaterra  | 13,1 %    |
| Brasil      | 10,8 %    |
| França      | 9,5 %     |
| Argentina   | 9,2 %     |

Mètriques de validació sobre el conjunt 2023–2026: 
**Brier Score = 0,508**
**log-loss = 0,865**
 **RPS = 0,167**
  **ECE mitjà = 0,041**

## Estructura del repositori

```
.
├── data/                       # Dades originals i fitxers generats per a la simulació
├── src/                        # Implementació de les funcions principals del model
│   ├── elo.py                  # Simulació i actualització dels ratings ELO
│   ├── model.py                # Entrenament del GLM de Poisson
│   ├── convergence.py          # Algorisme iteratiu d'estimació conjunta (EM)
│   ├── grid_search.py          # Optimització dels learning rates (k, k_Γ)
│   ├── groups.py               # Construcció dels grups de la simulació
│   ├── make_dataset.py         # Neteja de dades i creació del conjunt de treball
│   ├── make_third_place_table.py  # Combinacions dels 8 millors tercers
│   └── verification.py         # Verificació manual d'una mostra aleatòria de partits
├── notebooks/                  # Flux d'execució complet (entrenament, validació, simulació)
├── results/                    # Paràmetres estimats i resultats de les simulacions
├── requirements.txt            # Dependències de Python
└── README.md
```

## Dades

Les dades provenen del conjunt *International football results from 1872 to 2024*, disponible a [Kaggle](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017). A partir del fitxer original ('results.csv', 49.287 partits) es filtren els partits
des de l'any 2000 i s'eliminen seleccions extintes o no reconegudes per la FIFA, obtenint un conjunt de treball de **21.127 partits** (període 2000–2026).

## Instal·lació

Requereix Python 3.10 o superior. Es recomana fer servir un entorn virtual:

```bash
git clone https://github.com/ssaaaam/<NOM_DEL_REPOSITORI>.git
cd <NOM_DEL_REPOSITORI>

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Reproducció dels resultats

Després d'instal·lar les dependències executa els notebooks de la carpeta 'notebooks/':

1. Entrenament del model (estimació dels paràmetres del model i del learning rate).
2. Validació (mètriques de calibració i comparativa amb baselines).
3. Simulació de la Copa del Món 2026 (Monte Carlo).

Els resultats es desen a `results/`.

## Citació

Si fas servir aquest treball, pots citar-lo com:

```
Almendros Montoya, S., Badiella L. (2026). Modelització probabilística en futbol internacional: el cas del Mundial 2026. Treball Final de Grau, Universitat Autònoma de Barcelona.
```
