import itertools
import numpy as np
import pandas as pd
import time
from joblib import Parallel, delayed

from src.elo import simulate_elos, simulate_elos_valid
from src.model import train_model, expected_goals

def generate_dict_k_combinations(dict_search):
    keys = []
    value_lists = []
    
    for key, val in dict_search.items():
        if isinstance(val, dict):
            for subkey, subval in val.items():
                keys.append((key, subkey))
                value_lists.append(subval)
        else:
            keys.append((key,))
            value_lists.append(val)
            
    combinations = list(itertools.product(*value_lists))
    
    config_list = []
    for combo in combinations:
        # Reconstruimos la estructura de dict_k para cada combinación
        new_dict_k = {
            'eta' : 0.0,
            'k_0': 0.0,
            'intercontinental': {},
            'stage': {},
            'competition': {}
        }
        
        for i, path in enumerate(keys):
            if len(path) == 1:
                new_dict_k[path[0]] = combo[i]
            else:
                new_dict_k[path[0]][path[1]] = combo[i]
        
        config_list.append(new_dict_k)
        
    return config_list

def grid_search_optimized(folds, team_conf_dict, dict_search):
    best_score = np.inf
    best_config = None

    configs = generate_dict_k_combinations(dict_search)
    print(f"Nombre total de combinacions: {len(configs)}")
    start_time = time.time()

    for i, config in enumerate(configs):
        score_sum = 0
        for df_train, df_valid in folds.values():
            
            # ───── 1. Entrenament: parteix de 0 ─────
            df_train_res, df_ranking_train, df_confs_train = simulate_elos(
                df_train, team_conf_dict, config, params=None, eta=config['eta']
            )
            parameters = train_model(df_train_res)
            
            # ───── 2. Converteix l'estat final a dicts ─────
            init_team_elos = {
                row["Team"]: {"off": row["Off_ELO"], "def": row["Def_ELO"]}
                for _, row in df_ranking_train.iterrows()
            }
            init_conf_elos = dict(zip(df_confs_train["Confederation"], df_confs_train["Meta_ELO"]))
            
            # ───── 3. Validació: hereta l'estat de l'entrenament ─────
            df_valid_res, _, _ = simulate_elos_valid(
                df_valid, team_conf_dict, config, parameters, config['eta'],
                init_team_elos, init_conf_elos
            )
            
            # ───── 4. Càlcul de la NLL (igual que abans) ─────
            h_adv = 1 - df_valid_res["neutral"]
            diff_gamma = df_valid_res["Home_Conf_ELO"] - df_valid_res["Away_Conf_ELO"]

            y_pred_h = expected_goals(parameters, df_valid_res["Home_Offensive_ELO"],
                                      df_valid_res["Away_Defensive_ELO"], h_adv, diff_gamma)
            y_pred_a = expected_goals(parameters, df_valid_res["Away_Offensive_ELO"],
                                      df_valid_res["Home_Defensive_ELO"], -h_adv, -diff_gamma)

            y_true_h = df_valid_res["home_score"].values
            y_true_a = df_valid_res["away_score"].values

            nll_home = y_pred_h - y_true_h * np.log(y_pred_h + 1e-10)
            nll_away = y_pred_a - y_true_a * np.log(y_pred_a + 1e-10)

            score = np.mean(nll_home + nll_away)
            score_sum += score

        avg_score = score_sum / len(folds)
        if avg_score < best_score:
            best_score = avg_score
            best_config = config
        
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            vel = elapsed / (i + 1)
            faltan_horas = ((len(configs) - (i + 1)) * vel) / 3600
            print(f"[{i + 1}/{len(configs)}] | Quedan aprox: {faltan_horas:.2f} h. | Mejor NLL: {best_score:.4f}")
    
    print(f"\nBúsqueda finalizada. Mejor NLL: {best_score}")
    return best_config, best_score
            
def csv_to_dict(csv_path):
    # 1. Leemos el CSV
    df = pd.read_csv(csv_path)
    
    # 2. Tomamos la primera fila (o la que te interese)
    row = df.iloc[0]
    
    # 3. Estructura base para el diccionario
    # Inicializamos las categorías anidadas
    nested_dict = {
        'intercontinental': {},
        'stage': {},
        'competition': {}
    }
    
    # 4. Iteramos sobre las columnas
    for col, value in row.items():
        if '.' in col:
            # Es una variable anidada (ej: competition.World_Cup)
            parent, child = col.split('.')
            if parent in nested_dict:
                nested_dict[parent][child] = value
        else:
            # Es una variable simple (ej: eta, k_0)
            nested_dict[col] = value
            
    return nested_dict

from joblib import Parallel, delayed
import time


def _evaluate_config(config, folds, team_conf_dict):
    """Avalua una sola configuració sobre tots els folds. Funció al nivell de mòdul (requisit de joblib)."""
    score_sum = 0
    for df_train, df_valid in folds.values():
        
        df_train_res, df_ranking_train, df_confs_train = simulate_elos(
            df_train, team_conf_dict, config, params=None, eta=config['eta']
        )
        parameters = train_model(df_train_res)
        
        init_team_elos = {
            row["Team"]: {"off": row["Off_ELO"], "def": row["Def_ELO"]}
            for _, row in df_ranking_train.iterrows()
        }
        init_conf_elos = dict(zip(df_confs_train["Confederation"], df_confs_train["Meta_ELO"]))
        
        df_valid_res, _, _ = simulate_elos_valid(
            df_valid, team_conf_dict, config, parameters, config['eta'],
            init_team_elos, init_conf_elos
        )
        
        h_adv = 1 - df_valid_res["neutral"]
        diff_gamma = df_valid_res["Home_Conf_ELO"] - df_valid_res["Away_Conf_ELO"]

        y_pred_h = expected_goals(parameters, df_valid_res["Home_Offensive_ELO"],
                                  df_valid_res["Away_Defensive_ELO"], h_adv, diff_gamma)
        y_pred_a = expected_goals(parameters, df_valid_res["Away_Offensive_ELO"],
                                  df_valid_res["Home_Defensive_ELO"], -h_adv, -diff_gamma)

        y_true_h = df_valid_res["home_score"].values
        y_true_a = df_valid_res["away_score"].values

        nll_home = y_pred_h - y_true_h * np.log(y_pred_h + 1e-10)
        nll_away = y_pred_a - y_true_a * np.log(y_pred_a + 1e-10)

        score = np.mean(nll_home + nll_away)
        score_sum += score
    
    return config, score_sum / len(folds)


def grid_search_parallel(folds, team_conf_dict, dict_search, n_jobs=-1):
    configs = generate_dict_k_combinations(dict_search)
    n_configs = len(configs)
    print(f"Nombre total de combinacions: {n_configs}")
    print(f"Cores en ús: {'tots' if n_jobs == -1 else n_jobs}")
    
    start_time = time.time()
    
    # Paral·lelització
    results = Parallel(n_jobs=n_jobs, verbose=5)(
        delayed(_evaluate_config)(c, folds, team_conf_dict) for c in configs
    )
    
    elapsed = time.time() - start_time
    print(f"\nTemps total: {elapsed/60:.2f} min")
    
    # Troba el millor
    best_config, best_score = min(results, key=lambda x: x[1])
    print(f"Mejor NLL: {best_score:.4f}")
    print(f"Mejor config: {best_config}")
    
    
    return best_config, best_score