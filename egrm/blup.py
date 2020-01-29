import numpy as np
import pandas as pd
import math

def BLUP(K, y_train, trains, tests, h2 = 0.9):
  N_train = len(trains)
  
  I = (1/h2 - h2) * np.identity(N_train)
  V = K[trains, trains] + I
  
  Kt = K[tests, :][:, trains]
  
  Vi = np.linalg.inv(V)
  y_ = np.dot(Kt, np.dot(Vi, y_train))
  return y_

def h_estimate(K, y, N):
  y_norm = y - y.mean(); y_norm = y_norm / y_norm.std()
  K2 = np.diag(np.dot(K, K)).sum()
  yTKy = np.dot(np.dot(np.transpose(y_norm), K), y_norm)
  yTy = np.dot(np.transpose(y_norm), y_norm)
  buffer = (yTKy - yTy) / (K2 - N)
  return buffer

def test(simulation, repeats = 1000):
  N = simulation["parameters"]["N"]
  K_cas = simulation["Ks"]["K_cas"]
  K_obs = simulation["Ks"]["K_obs"]
  Km = simulation["Ks"]["Km"]
  Km_relate = simulation["Ks"]["Km_relate"]
  Km_tsinfer = simulation["Ks"]["Km_tsinfer"]
  
  diags = np.diag_indices(N)
  non_diags = np.where(~np.eye(N,dtype=bool))
  
  table = {"K_cas":K_cas[non_diags].flatten(), "K_obs":K_obs[non_diags].flatten(),
           "Km":Km[non_diags].flatten(), "Km_relate":Km_relate[non_diags].flatten(),
           "Km_tsinfer":Km_tsinfer[non_diags].flatten()}
  
  table = pd.DataFrame(data=table)
  corr = table.corr(method ='pearson')
  
  y = simulation["phenotypes"]["y"]
  h_estimation = {'K_cas':h_estimate(K_cas, y, N), 
                  'K_obs':h_estimate(K_obs, y, N),
                  'Km':h_estimate(Km, y, N),
                  'Km_relate':h_estimate(Km_relate, y, N),
                  'Km_tsinfer':h_estimate(Km_tsinfer, y, N)} 
  
  a = []
  b = []
  c = []
  d = []
  e = []
  for i in range(1000):
    tests = np.random.choice(N, math.floor(N * 0.25), replace = False)
    tests.sort()
    trains = [i for i in range(N) if i not in tests]
    y_train = y[trains]
    y_test = y[tests]
    
    y_ = BLUP(K_cas, y_train, trains, tests, h2 = 0.9)
    a.append(np.corrcoef(y_, y_test)[0, 1])
    y_ = BLUP(K_obs, y_train, trains, tests, h2 = 0.9)
    b.append(np.corrcoef(y_, y_test)[0, 1])
    y_ = BLUP(Km, y_train, trains, tests, h2 = 0.9)
    c.append(np.corrcoef(y_, y_test)[0, 1])
    y_ = BLUP(Km_relate, y_train, trains, tests, h2 = 0.9)
    d.append(np.corrcoef(y_, y_test)[0, 1])
    y_ = BLUP(Km_tsinfer, y_train, trains, tests, h2 = 0.9)
    d.append(np.corrcoef(y_, y_test)[0, 1])
  
  a = np.array(a)
  b = np.array(b)
  c = np.array(c)
  d = np.array(d)
  e = np.array(e)
  blup = {"K_cas":a, "K_obs":b, "Km":c, "Km_relate":d, "Km_tsinfer":e}
  simulation["tests"] = {"corr":corr, "blup":blup, 'h_estimation':h_estimation}

def summary(simulation):
  summ = "==========\nparameters \n==========\n"
  summ += "\n".join([str(x) + "\t" + str(simulation["parameters"][x]) for x in simulation["parameters"].keys()]) + "\n"
  
  summ += "==========\nK matrix correlations \n==========\n"
  summ += str(simulation["tests"]["corr"]) + "\n"
  tmp = simulation["tests"]["blup"]["K_cas"]
  
  summ += "==========\nheritability estimation \n==========\n"
  summ += "K_cas\t" + str(round(simulation["tests"]["h_estimation"]["K_cas"], 4)) + "\n"
  summ += "K_obs\t" + str(round(simulation["tests"]["h_estimation"]["K_obs"], 4)) + "\n"
  summ += "Km\t" + str(round(simulation["tests"]["h_estimation"]["Km"], 4)) + "\n"
  summ += "Km_relate\t" + str(round(simulation["tests"]["h_estimation"]["Km_relate"], 4)) + "\n"
  summ += "Km_tsinfer\t" + str(round(simulation["tests"]["h_estimation"]["Km_tsinfer"], 4)) + "\n"
  
  summ += "==========\nBLUP accuracy \n==========\n"
  summ += "K_cas\t" + str(round(tmp.mean(), 4)) + " +- " + str(round(tmp.std(), 4)) + "\n"
  tmp = simulation["tests"]["blup"]["K_obs"]
  summ += "K_obs\t" + str(round(tmp.mean(), 4)) + " +- " + str(round(tmp.std(), 4)) + "\n"
  tmp = simulation["tests"]["blup"]["Km"]
  summ += "Km\t" + str(round(tmp.mean(), 4)) + " +- " + str(round(tmp.std(), 4)) + "\n"
  tmp = simulation["tests"]["blup"]["Km_relate"]
  summ += "Km_relate\t" + str(round(tmp.mean(), 4)) + " +- " + str(round(tmp.std(), 4)) + "\n"
  tmp = simulation["tests"]["blup"]["Km_tsinfer"]
  summ += "Km_tsinfer\t" + str(round(tmp.mean(), 4)) + " +- " + str(round(tmp.std(), 4)) + "\n"
  
  return(summ)

