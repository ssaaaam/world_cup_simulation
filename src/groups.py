import itertools
from collections import defaultdict
import random
from turtle import pd

class Group():
    def __init__(self, name, teams):
        self.name = name
        self.teams = teams
        self.matches = list(itertools.combinations(teams, 2))
        self.reset()

    def reset(self):
        self.points = {team : 0 for team in self.teams}
        self.results = {}
        self.goals_scored = {team : 0 for team in self.teams}
        self.goals_conceded = {team : 0 for team in self.teams}
        self.goal_difference = {team : 0 for team in self.teams}
    
    def update_match_result(self, team_h, team_a, gh, ga):
        self.results[(team_h, team_a)] = (gh, ga)

        if gh > ga:
            self.points[team_h] += 3
        elif gh < ga:
            self.points[team_a] += 3
        else:
            self.points[team_h] += 1
            self.points[team_a] += 1

        self.goals_scored[team_h] += gh
        self.goals_conceded[team_h] += ga
        self.goals_scored[team_a] += ga
        self.goals_conceded[team_a] += gh
        
        self.goal_difference[team_h] = self.goals_scored[team_h] - self.goals_conceded[team_h]
        self.goal_difference[team_a] = self.goals_scored[team_a] - self.goals_conceded[team_a]

    def get_table(self, current_elo_dict):
        """
        Genera la tabla clasificada usando el diccionario de ELO dinámico.
        """
        teams_by_points = defaultdict(list)
        for team, pts in self.points.items():
            teams_by_points[pts].append(team)
        
        final_table = []
        
        # Ordenamos los grupos de puntos de mayor a menor
        for pts_value in sorted(teams_by_points.keys(), reverse=True):
            tied_teams = teams_by_points[pts_value]
            
            if len(tied_teams) > 1:
                # Lógica de desempate
                mini_stats = self._get_stats_for_teams(tied_teams, use_mini_league=True)
                
                tied_teams.sort(key=lambda t: (
                    mini_stats[t]["pts"],        # (a) Puntos mini-liga
                    mini_stats[t]["gd"],         # (b) GD mini-liga
                    mini_stats[t]["gf"],         # (c) GF mini-liga
                    self.goal_difference[t],     # (d) GD global
                    self.goals_scored[t],        # (e) GF global
                    # CAMBIO AQUÍ: Acceso al diccionario en lugar de .loc
                    # current_elo_dict[t]['ELO'],  
                    random.random()              # (g) Sorteo
                ), reverse=True)
                
            final_table.extend(tied_teams)
            
        return [
            {
                "team": t,
                "points": self.points[t],
                "goal_difference": self.goal_difference[t],
                "goals_scored": self.goals_scored[t],
                # "ranking_fifa" : current_elo_dict[t]['ELO']
            } 
            for t in final_table
        ]
    
    def _get_stats_for_teams(self, teams_to_check, use_mini_league=False):
        stats = {t: {"pts": 0, "gd": 0, "gf": 0} for t in teams_to_check}
        
        for (t1, t2), (g1, g2) in self.results.items():
            if use_mini_league:
                if t1 not in teams_to_check or t2 not in teams_to_check:
                    continue
            
            if t1 in stats:
                stats[t1]["gf"] += g1
                stats[t1]["gd"] += (g1 - g2)
                if g1 > g2: stats[t1]["pts"] += 3
                elif g1 == g2: stats[t1]["pts"] += 1
                
            if t2 in stats:
                stats[t2]["gf"] += g2
                stats[t2]["gd"] += (g2 - g1)
                if g2 > g1: stats[t2]["pts"] += 3
                elif g2 == g1: stats[t2]["pts"] += 1
                
        return stats
    
    import pandas as pd

    def print_pretty_tables(self, df_ranking):
        table_data = self.get_table(df_ranking) # O la variable de ranking que uses
        
        header = f"\n=== CLASIFICACIÓN GRUPO {self.name} ==="
        print(header)
        
        # Definimos el ancho de las columnas para que todo quede alineado
        # {Pos:<4} -> Posición alineada a la izquierda, 4 espacios
        # {Equipo:<20} -> Nombre alineado a la izquierda, 20 espacios
        print(f"{'Pos':<4} {'Equipo':<22} {'Pts':<5} {'DG':<5} {'GF':<5}")
        print("-" * len(header) * 2) # Línea divisoria
        
        for i, row in enumerate(table_data, 1):
            team = row['team']
            pts = row['points']
            dg = row['goal_difference']
            gf = row['goals_scored']
            
            # Formateamos cada fila
            print(f"{i:<4} {team:<22} {pts:<5} {dg:<5} {gf:<5}")
