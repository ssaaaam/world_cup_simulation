from src.elo import simulate_elos
from src.model import train_model

def converge_model(df_matches, team_to_conf, dict_k, max_iterations=20, tolerance=1e-4):
    """Bucle de convergencia para estabilizar los parámetros del Meta-Elo y Poisson."""
    print("Iniciando convergencia del modelo final...")
    max_diff_array = []
    
    # 1. Iteración 1: Bootstrapping (Arranque sin parámetros)
    # simulate_elos ahora devuelve 3 cosas: df_res, df_ranking, df_confs
    df_temp, _, _ = simulate_elos(df_matches, team_to_conf, dict_k, params=None)
    current_params, current_se = train_model(df_temp)
    
    print(f"Iteración 1 (Bootstrap) completada.")
    
    for i in range(2, max_iterations + 1):
        # 2. Re-simular con los parámetros calculados en la vuelta anterior
        df_temp, df_ranking, df_confs = simulate_elos(df_matches, team_to_conf, dict_k, params=current_params)
        
        # 3. Re-entrenar para obtener nuevos parámetros
        new_params, new_se = train_model(df_temp)
        
        # 4. Calcular la diferencia máxima para verificar estabilidad
        # Comparamos alpha, beta_1, beta_2, theta y gamma
        diffs = [abs(current_params[k] - new_params[k]) for k in current_params.keys()]
        max_diff = max(diffs)
        max_diff_array.append(max_diff)
        print(f"Iteración {i} | Máxima variación: {max_diff:.6f}")
        
        current_params = new_params
        current_se = new_se
        
        if max_diff < tolerance:
            print(f"\n¡CONVERGENCIA ALCANZADA EN LA ITERACIÓN {i}!")
            df_temp, df_ranking, df_confs = simulate_elos(
            df_matches, team_to_conf, dict_k, params=current_params
        )

    # 2. Calculamos el ELO Global unificado
    # Usamos -current_params["beta_2"] porque beta_2 es negativo (la defensa resta goles recibidos)
    # Al restarlo, una buena defensa suma puntos al ranking.
            
    return df_temp, df_ranking, df_confs, current_params, current_se, max_diff_array