# Posibles problemas:
# Las simulaciones de milstein parecen ser más altas. bueno creo que ha sido solo casualidad. He hecho 1000 simulaciones de euler y 1000 de milstein (mirar últimas líneas) y las medias en 250 eran 52.5038 (Euler), 52.4973 (Milstein) 
# Otroas simulaciones dan  53.0484 (Euler), 52.0673 (Milstein), 52.5674 (Rudge-kutta) 
import numpy as np 
import matplotlib.pyplot as plt 
import math 
import helpFunctions


# Space inefficient, but allows for an easier treatment of path-dependent payoffs 

def GBM(r, sigma, S_0, num_steps, T, num_simulations = 10000, integration_method = 'E', ant_variates = False):
    delta_t = T/num_steps 

    S = np.zeros((num_simulations, num_steps +1))
    W = np.sqrt(delta_t)*np.random.normal(0,1,(num_simulations, num_steps)) 


    for i in range(num_simulations):
        S[i,0] = S_0 
    
    if ant_variates: 
        ant_S = S 


    for j in range(num_steps):
        deterministic_term = r*S[:,j]*delta_t
        random_term = sigma*S[:,j]*W[:,j]
    
        if ant_variates:
            ant_deterministic_term = r*ant_S[:,j]*delta_t
            ant_random_term   = sigma*ant_S[:,j]*(-W[:,j])
        
        if integration_method == 'E': 
            S[:,j+1] = S[:,j] + deterministic_term + random_term 
            
            if ant_variates: 
                ant_S[:,j+1] = ant_S[:,j] + ant_deterministic_term + ant_random_term
            
        
        elif integration_method == 'M': 
            milstein_term = 1/2 * (sigma**2)*S[:,j]*(W[:,j]**2 -delta_t)
            S[:,j+1] = S[:,j] + deterministic_term + random_term + milstein_term 

            if ant_variates: 
                ant_milstein_term = 1/2 * (sigma**2)*ant_S[:,j]*(W[:,j]**2 -delta_t)
                ant_S[:,j+1] = ant_S[:,j] + ant_deterministic_term + ant_random_term + ant_milstein_term
        

        elif integration_method == 'RK': 
            y_hat = S[:,j] + r*S[:,j]*delta_t + sigma*np.sqrt(delta_t) 
            rk_term = (W[:,j]**2 - delta_t) * sigma*(y_hat - S[:,j])/(2*np.sqrt(delta_t))
            S[:,j+1] = S[:,j] + deterministic_term + random_term + rk_term 

            if ant_variates: 
                ant_y_hat = S[:,j] + r*S[:,j]*delta_t + sigma*np.sqrt(delta_t) 
                ant_rk_term = (W[:,j]**2 - delta_t) * sigma*(y_hat - ant_S[:,j])/(2*np.sqrt(delta_t))
                ant_S[:,j+1] = ant_S[:,j] + deterministic_term + random_term + rk_term
            
        else: 
            raise ValueError("Please choose an appropiate SDE integration method (Euler ('E'), Milstein('M') or Rudge-Kutta('RK'))")

        if ant_variates: 
            return np.vstack((S, ant_S)) 
    return S


def EuPayOff(S, K, call_or_put): 
    if call_or_put == 'C':
        return np.maximum(S - K, 0) 
    elif call_or_put =='P': 
        return np.maximum(K - S, 0) 
    else: 
        raise ValueError("Please choose an appropiate value for call_or_put (Call ('C') or Put ('P')") 

#This function uses the paths generated by the previous function to price european options through 
def eu_GBM(r, sigma, S_0, K, num_steps, T, put_or_call, num_simulations = 10000, integration_method = 'E', ant_variates = False, payOff = helpFunctions.payOff): 
    S = GBM(r, sigma, S_0, num_steps, T, num_simulations = num_simulations, integration_method = 'E', ant_variates = False)
    Vs = np.vectorize(payOff) (S[:, num_steps], K, put_or_call)
    V = math.exp(-r*T)*np.mean(Vs) 
    return V 

def as_GBM(r, sigma, S_0, K, num_steps, T, put_or_call, num_simulations = 10000, integration_method = 'E', ant_variates = False, payOff = helpFunctions.asianPayOff):
    S = GBM(r, sigma, S_0, num_steps, T, num_simulations = num_simulations, integration_method = 'E', ant_variates = False)
    # Hay que definir mejor la media porque seguro que hay una forma mucho mejor 
    price_mean = np.zeros(num_simulations)
    for i in range(num_simulations):
        price_mean[i] = np.mean(S[i,:]) 
    Vs = np.vectorize(payOff)(S[:, num_steps], K, price_mean, put_or_call)
    # Y supongo que luego hay que hacer lo mismo que con las europeas pero debería comprobarlo
    V = math.exp(-r*T)*np.mean(Vs) 
    return V 

