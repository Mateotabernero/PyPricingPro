import numpy as np 
import matplotlib.pyplot as plt 
import math 
import helpFunctions
import PayOffs


def GBM(r, sigma, S_0, num_steps, T, num_simulations = 10000, integration_method = 'E', ant_variates = False):

    """
    Calculate sample paths of GBM 

    : param r                  : The drift 
    : param sigma              : The volatility 
    : param S_0                : The initial price 
    : param num_steps          : Number of steps for the random path generation  
    : param T                  : Time length of the generated path 
    : param num_simulations    : The number of paths generated (default value: 10000) 
    : param integration_method : The SDE integration method used. Choose from 'E' (Euler-Maruyama), 'M' (Milstein) or 'RK' (Runge-Kutta) (default value: 'E')
    : param ant_variates       : Boolean indicating whether antithetic variates are to be used 
    : returns                  : A numpy array containing the generated paths      
    
    """

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


    
#This function uses the paths generated by the previous function to price european options through 
def eu_GBM(r, sigma, S_0, K, num_steps, T, call_or_put, num_simulations = 10000, integration_method = 'E', ant_variates = False): 
    """
    Computes the value of an European option under GBM using Monte Carlo method 

    : param r                   : Risk-free interest rate 
    : param sigma               : Volatility 
    : param S_0                 : Spot price
    : param K                   : Strike price 
    : param num_steps           : Number of steps on the generation of paths
    : param T                   : Maturity 
    : param call_or_put         : Whether the option is a call ('C') or a put ('P') 
    : param num_simulations     : Number of paths generated for MC 
    : param integration_method  : SDE integration method to be used in the generation of paths (Euler-Maruyama ('E'), Milstein ('M') or Runge-Kutta ('RK')) 
    : param ant_variates        : Boolean indicating whether antithetic variates are to be used
    : returns                   : Value of the option 
    
    """

    
    S = GBM(r, sigma, S_0, num_steps, T, num_simulations = num_simulations, integration_method = 'E', ant_variates = False)
    Vs = payOffs.EuPayOff(S, K, call_or_put)
    V = np.exp(-r*T)*np.mean(Vs) 
    return V 

def as_GBM(r, sigma, S_0, K, num_steps, T, put_or_call, num_simulations = 10000, integration_method = 'E', ant_variates = False):

    """
    Computes the value of an Asian option under GBM using Monte Carlo method 

    : param r                   : Risk-free interest rate 
    : param sigma               : Volatility 
    : param S_0                 : Spot price 
    : param K                   : Strike price 
    : param num_steps           : Number of steps on the generation of paths
    : param T                   : Maturity 
    : param call_or_put         : Whether the option is a Price call('PC'), a price put ('PP'), a strike call ('SK') or a strike put ('SK') 
    : param num_simulations     : Number of paths generated for MC 
    : param integration_method  : SDE integration method to be used in the generation of paths (Euler-Maruyama ('E'), Milstein ('M') or Runge-Kutta ('RK')) 
    : param ant_variates        : Boolean indicating whether antithetic variates are to be used
    : returns                   : Value of the option 
    """
    
    S  = GBM(r, sigma, S_0, num_steps, T, num_simulations = num_simulations, integration_method = 'E', ant_variates = False)
    Vs = payOffs.AsPayOff(S, K, call_or_put) 
    V  = np.exp(-r*T)*np.mean(Vs) 
    return V 



