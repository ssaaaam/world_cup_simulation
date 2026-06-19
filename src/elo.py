import numpy as np
import pandas as pd
from src.model import expected_goals

def simulate_elos(df_matches, team_to_conf, dict_k, params = None):
    teams = pd.concat([df_matches["home"], df_matches["away"]]).unique()
    elos = {t: {"off" : 0.0, "def" : 0.0} for t in teams}

    conf_elos = {
        "UEFA" : 0.0, "CONMEBOL" : 0.0, "AFC" : 0.0,
        "CAF" : 0.0, "CONCACAF" : 0.0, "OFC" : 0.0
    }
    eta = dict_k["eta"]

    conf_members = {c: [t for t in teams if team_to_conf.get(t) == c] for c in conf_elos.keys()}

    n_matches = len(df_matches)
    h_off_hist, h_def_hist = np.zeros(n_matches), np.zeros(n_matches)
    a_off_hist, a_def_hist = np.zeros(n_matches), np.zeros(n_matches)
    h_meta_hist, a_meta_hist = np.zeros(n_matches), np.zeros(n_matches)

    ht_arr, at_arr = df_matches["home"].values, df_matches["away"].values
    hg_arr, ag_arr = df_matches["home_score"].values, df_matches["away_score"].values
    conf_h_arr, conf_a_arr = df_matches["home_confederation"].values, df_matches["away_confederation"].values
    stages = df_matches["stage"].values
    is_neutral = df_matches["neutral"].values
    years = df_matches["date"].dt.year.values
    comp_arr = df_matches["competition"].values
    is_inter = df_matches["is_intercontinental"].values

    if params == None:
        exp_hg_const = hg_arr.mean()
        exp_ag_const = ag_arr.mean()

    year_act = years[0]
    last_year_lap = years[0]

    for i in range(n_matches):
        ht, at = ht_arr[i], at_arr[i]
        conf_h, conf_a = conf_h_arr[i], conf_a_arr[i]
        comp = comp_arr[i]
        year = years[i]
        # Guardamos los valores de los ELOs

        # Centralizamos los valores de las confederaciones cada año
        if year != year_act:
            for conf, members in conf_members.items():
                if members:
                    mu_off = np.mean([elos[t]["off"] for t in members])
                    mu_def = np.mean([elos[t]["def"] for t in members])
                    for t in members:
                        elos[t]["off"] -= mu_off
                        elos[t]["def"] -= mu_def
            year_act = year
        
        

        h_off_hist[i], h_def_hist[i] = elos[ht]["off"], elos[ht]["def"]
        a_off_hist[i], a_def_hist[i] = elos[at]["off"], elos[at]["def"]
        h_meta_hist[i], a_meta_hist[i] = conf_elos[conf_h], conf_elos[conf_a]

        h_adv = 1 - is_neutral[i] 
        diff_gamma = conf_elos[conf_h] - conf_elos[conf_a]

        if params != None:
            exp_hg = expected_goals(params, elos[ht]["off"], elos[at]["def"], h_adv, diff_gamma)
            exp_ag = expected_goals(params, elos[at]["off"], elos[ht]["def"], -h_adv, -diff_gamma)
        else:
            exp_hg, exp_ag = exp_hg_const, exp_ag_const
        
        err_h = hg_arr[i] - exp_hg
        err_a = ag_arr[i] - exp_ag
        omega = err_h - err_a

        # Lógica de K y G
        k = dict_k["k_0"] * dict_k["stage"][stages[i]] * dict_k["competition"][comp]* dict_k["intercontinental"][str(is_inter[i])]

        diff_goals = abs(hg_arr[i] - ag_arr[i])
        if diff_goals < 2: g = 1.0
        elif diff_goals == 2: g = 1.5
        else: g = (diff_goals + 11) / 8
        
        # Actualización de Elos
        elos[ht]["off"] += k * g * err_h
        elos[at]["def"] -= k * g * err_h
        elos[at]["off"] += k * g * err_a
        elos[ht]["def"] -= k * g * err_a

        if conf_h != conf_a:
            delta = g * k * eta * omega
            conf_elos[conf_h] += delta
            conf_elos[conf_a] -= delta
            
            # Ripple Effect
            for team in conf_members[conf_h]:
                elos[team]["off"] += delta
                elos[team]["def"] += delta
            for team in conf_members[conf_a]:
                elos[team]["off"] -= delta
                elos[team]["def"] -= delta

    df_res = df_matches.copy()
    df_res["Home_Offensive_ELO"] = h_off_hist
    df_res["Home_Defensive_ELO"] = h_def_hist
    df_res["Away_Offensive_ELO"] = a_off_hist
    df_res["Away_Defensive_ELO"] = a_def_hist
    df_res["Home_Conf_ELO"] = h_meta_hist
    df_res["Away_Conf_ELO"] = a_meta_hist
    
    df_ranking = pd.DataFrame([
        {"Team": t, "Off_ELO": elos[t]["off"], "Def_ELO": elos[t]["def"], "Conf": team_to_conf.get(t, "Other")} 
        for t in teams
    ])

    df_confs = pd.DataFrame(list(conf_elos.items()), columns=["Confederation", "Meta_ELO"])
    
    return df_res, df_ranking, df_confs


def simulate_elos_valid(df_valid, team_to_conf, dict_k, params, eta,
                         init_team_elos, init_conf_elos):
    """
    Simulació seqüencial dels ELOs sobre el conjunt de validació,
    partint dels ELOs finals de l'entrenament.
    """
    
    # ───── Hereda l'estat final de l'entrenament ─────
    elos = {t: {"off": e["off"], "def": e["def"]} 
            for t, e in init_team_elos.items()}
    conf_elos = init_conf_elos.copy()
    
    # Equips nous que apareixen només en validació: inicialitzats a 0
    teams_in_valid = pd.concat([df_valid["home"], df_valid["away"]]).unique()
    for t in teams_in_valid:
        if t not in elos:
            elos[t] = {"off": 0.0, "def": 0.0}
    
    # conf_members ha de cobrir TOTS els equips coneguts (no només els de valid)
    all_teams = list(elos.keys())
    conf_members = {c: [t for t in all_teams if team_to_conf.get(t) == c]
                    for c in conf_elos.keys()}
    
    n_matches = len(df_valid)
    h_off_hist, h_def_hist = np.zeros(n_matches), np.zeros(n_matches)
    a_off_hist, a_def_hist = np.zeros(n_matches), np.zeros(n_matches)
    h_meta_hist, a_meta_hist = np.zeros(n_matches), np.zeros(n_matches)
    
    ht_arr, at_arr = df_valid["home"].values, df_valid["away"].values
    hg_arr, ag_arr = df_valid["home_score"].values, df_valid["away_score"].values
    conf_h_arr, conf_a_arr = df_valid["home_confederation"].values, df_valid["away_confederation"].values
    stages = df_valid["stage"].values
    is_neutral = df_valid["neutral"].values
    years = df_valid["date"].dt.year.values
    comp_arr = df_valid["competition"].values
    is_inter = df_valid["is_intercontinental"].values
    
    # year_act inicialitzat a l'any anterior al primer partit,
    # perquè el re-centrat anual triggi en el primer canvi d'any de validació
    year_act = years[0] - 1
    
    for i in range(n_matches):
        ht, at = ht_arr[i], at_arr[i]
        conf_h, conf_a = conf_h_arr[i], conf_a_arr[i]
        comp = comp_arr[i]
        year = years[i]
        
        # Re-centrat anual intra-confederació
        if year != year_act:
            for conf, members in conf_members.items():
                if members:
                    mu_off = np.mean([elos[t]["off"] for t in members])
                    mu_def = np.mean([elos[t]["def"] for t in members])
                    for t in members:
                        elos[t]["off"] -= mu_off
                        elos[t]["def"] -= mu_def
            year_act = year   # ← arreglat el bug del simulate_elos original
        
        # ELOs ABANS del partit (per a predir)
        h_off_hist[i], h_def_hist[i] = elos[ht]["off"], elos[ht]["def"]
        a_off_hist[i], a_def_hist[i] = elos[at]["off"], elos[at]["def"]
        h_meta_hist[i], a_meta_hist[i] = conf_elos[conf_h], conf_elos[conf_a]
        
        h_adv = 1 - is_neutral[i]
        diff_gamma = conf_elos[conf_h] - conf_elos[conf_a]
        
        # Predicció (sempre amb params entrenats)
        exp_hg = expected_goals(params, elos[ht]["off"], elos[at]["def"], h_adv, diff_gamma)
        exp_ag = expected_goals(params, elos[at]["off"], elos[ht]["def"], -h_adv, -diff_gamma)
        
        err_h = hg_arr[i] - exp_hg
        err_a = ag_arr[i] - exp_ag
        omega = err_h - err_a
        
        # Càlcul de k i g
        k = dict_k["k_0"] * dict_k["stage"][stages[i]] * dict_k["competition"][comp] * dict_k["intercontinental"][str(is_inter[i])]
        
        diff_goals = abs(hg_arr[i] - ag_arr[i])
        if diff_goals < 2: g = 1.0
        elif diff_goals == 2: g = 1.5
        else: g = (diff_goals + 11) / 8
        
        # Actualització dels ELOs (després de la predicció)
        elos[ht]["off"] += k * g * err_h
        elos[at]["def"] -= k * g * err_h
        elos[at]["off"] += k * g * err_a
        elos[ht]["def"] -= k * g * err_a
        
        # Efecte de propagació intercontinental
        if conf_h != conf_a:
            delta = g * k * eta * omega
            conf_elos[conf_h] += delta
            conf_elos[conf_a] -= delta
            
            for team in conf_members[conf_h]:
                elos[team]["off"] += delta
                elos[team]["def"] += delta
            for team in conf_members[conf_a]:
                elos[team]["off"] -= delta
                elos[team]["def"] -= delta
    
    # Construcció dels DataFrames de sortida
    df_res = df_valid.copy()
    df_res["Home_Offensive_ELO"] = h_off_hist
    df_res["Home_Defensive_ELO"] = h_def_hist
    df_res["Away_Offensive_ELO"] = a_off_hist
    df_res["Away_Defensive_ELO"] = a_def_hist
    df_res["Home_Conf_ELO"] = h_meta_hist
    df_res["Away_Conf_ELO"] = a_meta_hist
    
    df_ranking = pd.DataFrame([
        {"Team": t, "Off_ELO": elos[t]["off"], "Def_ELO": elos[t]["def"],
         "Conf": team_to_conf.get(t, "Other")}
        for t in elos.keys()
    ])
    
    df_confs = pd.DataFrame(list(conf_elos.items()), columns=["Confederation", "Meta_ELO"])
    
    return df_res, df_ranking, df_confs