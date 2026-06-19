import numpy as np
import pandas as pd
import statsmodels.api as sm

def expected_goals(params, off_elo, def_elo, home_adv, conf_diff):
    return np.exp(params["alpha"] + (params["gamma"] * home_adv) + (params["beta_1"] * off_elo) + (params["beta_2"] * def_elo) + (params["theta"]*conf_diff))


def train_model(df_res):
    """
    Calibra el modelo Poisson usando los Elos generados en la simulación.
    Modelo: log(lambda) = alpha + beta1*Off + beta2*Def + theta*Diff_Conf + gamma*HomeAdv
    """
    h_adv_h = df_res["neutral"]
    h_adv_a = -df_res["neutral"]

    conf_diff_h = df_res["Home_Conf_ELO"] - df_res["Away_Conf_ELO"]
    conf_diff_a = df_res["Away_Conf_ELO"] - df_res["Home_Conf_ELO"]

    df_train = pd.concat([
        pd.DataFrame({
            "Goals": df_res["home_score"],
            "Off_ELO": df_res["Home_Offensive_ELO"],
            "Def_ELO": df_res["Away_Defensive_ELO"],
            "Conf_Diff": conf_diff_h,
            "H_Adv": h_adv_h,
        }),
        pd.DataFrame({
            "Goals": df_res["away_score"],
            "Off_ELO": df_res["Away_Offensive_ELO"],
            "Def_ELO": df_res["Home_Defensive_ELO"],
            "Conf_Diff": conf_diff_a,
            "H_Adv": h_adv_a,
        })
    ], ignore_index=True)

    # 4. Regresión
    X = df_train[["Off_ELO", "Def_ELO", "Conf_Diff", "H_Adv"]]
    X = sm.add_constant(X)
    y = df_train["Goals"]

    
    model_obj = sm.GLM(y, X, family=sm.families.Poisson())
    
    # 2. Aplicamos fit_regularized
    # alpha: controla la fuerza de la regularización (prueba valores entre 0.01 y 1.0)
    # L1_wt: 0.0 es Ridge (L2), 1.0 es Lasso (L1). Usamos 0.0 para no eliminar variables.
    model = model_obj.fit()

    return {
        "alpha": model.params["const"],
        "beta_1": model.params["Off_ELO"],
        "beta_2": model.params["Def_ELO"],
        "theta": model.params["Conf_Diff"],
        "gamma": model.params["H_Adv"],
    }, {
        'alpha_se': model.bse["const"],
        'beta_1_se': model.bse["Off_ELO"],
        'beta_2_se': model.bse["Def_ELO"],
        'theta_se': model.bse["Conf_Diff"],
        'gamma_se': model.bse["H_Adv"],
    }