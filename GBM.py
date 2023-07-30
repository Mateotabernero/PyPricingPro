# Posibles problemas:
# Las simulaciones de milstein parecen ser más altas. bueno creo que ha sido solo casualidad. He hecho 1000 simulaciones de euler y 1000 de milstein (mirar últimas líneas) y las medias en 250 eran 52.5038 (Euler), 52.4973 (Milstein) 
# Otroas simulaciones dan  53.0484 (Euler), 52.0673 (Milstein), 52.5674 (Rudge-kutta) 
import numpy as np 
import matplotlib.pyplot as plt 
import math 

# Podemos hacer la de cambiar X por y = log(x) y luego ya x = e^y. Lo dejamos para otra función
# Hay muchas mejoras (como por ejemplo separar la parte que realiza el update (cogiendo W como argumento) y así simplemente hay que correrlo dos veces para ant_S). Todo eso se irá haciendo 
# Voy a cambiar las W por lo que deberían ser (standar deviation = sqrt(delta_t))
#Con 10000 simulaciones se acercan un poquito más. Tampoco tienen que converger supongo xd 


# Dentro de lo que cabe parece ir bien. Habrá que revisar detalles y tal pero parece que todo bien
def GBM(r, sigma, S_0, num_steps, T, num_simulations = 10000, integration_method = 'E', ant_variates = False):
    delta_t = T/num_steps 

    S = np.zeros((num_simulations, num_steps +1))
    W = np.random.normal(0,1,(num_simulations, num_steps)) 

    if ant_variates: 
        ant_S = S 

    for i in range(num_simulations):
        S[i,0] = S_0 
    
    for i in range(num_simulations):
        for j in range(num_steps): 
            # This values are common to the three methods of integration 

            deterministic_term = r*S[i,j]*delta_t
            random_term = sigma*S[i,j]*(math.sqrt(delta_t)*W[i,j])

            if ant_variates :
                ant_deterministic_term = r*ant_S[i,j]*delta_t 
                ant_random_term  = sigma*ant_S[i,j]*(-math.sqrt(delta_t)*W[i,j]) 
            
            if integration_method == 'E': 
                S[i,j+1] = S[i,j] + deterministic_term + random_term
                
                if ant_variates:
                    ant_S[i,j+1] = ant_S[i,j] + ant_deterministic_term + ant_random_term
            
            elif integration_method == 'M':
                milstein_term = 1/2 * (sigma**2)*S[i,j]*((math.sqrt(delta_t)*W[i,j])**2 - delta_t)
                S[i,j+1] = S[i,j] + deterministic_term + random_term + milstein_term
                
                if ant_variates:
                    ant_milstein_term = 1/2 * (sigma**2)*ant_S[i,j]*((-math.sqrt(delta_t)*W[i,j])**2 - delta_t)
                    ant_S[i,j+1] = ant_S[i,j] + ant_deterministic_term + ant_random_term + ant_milstein_term
        
            elif integration_method == 'RK': 
                y_hat = S[i,j] + r*S[i,j]*delta_t + sigma*math.sqrt(delta_t) 
                rk_term = ((math.sqrt(delta_t)*W[i,j])**2 - delta_t) * sigma*(y_hat - S[i,j]) /(2*math.sqrt(delta_t))
                S[i, j+1] = S[i,j] + deterministic_term + random_term + rk_term 

                if ant_variates:
                    ant_y_hat =  ant_S[i,j] + r*ant_S[i,j]*delta_t + sigma*math.sqrt(delta_t)
                    ant_rk_term =((-math.sqrt(delta_t)*W[i,j])**2 - delta_t) * sigma*(ant_y_hat - ant_S[i,j]) /(2*math.sqrt(delta_t))
                    ant_S[i,j+1] = ant_S[i,j] + ant_deterministic_term + ant_random_term + ant_rk_term
            
            else: 
                raise ValueError ("Please choose an appropiate SDE integration method (Euler ('E'), Milstein ('M') or Rudge-Kutta ('RK'))")
    
    if ant_variates:
        return (S, ant_S)
    
    return S
    

(S, ant_S) = GBM (0.05,0.3, 50, 250, 1, num_simulations = 1000, integration_method='M', ant_variates= True)
for i in range(10):
    print("Estoy aquí")
    plt.plot(S[i, :], color = 'green')
    
(R, ant_R)  = GBM (0.05, 0.3, 50, 250, 1, num_simulations = 1000, integration_method= 'E', ant_variates = True)
for i in range(10):
    plt.plot(R[i, :], color = 'red')

(T, ant_T)  = GBM (0.05, 0.3, 50, 250, 1, num_simulations = 1000, integration_method = 'RK', ant_variates=True)
for i in range(10):
    plt.plot(T[i, :], color = 'blue')
plt.show() 

print("Euler mean: " + str((np.mean(R[:,250])+np.mean(ant_R[:,250]))/2))
print("Milstein mean: " + str((np.mean(S[:,250])+np.mean(ant_S[:,250]))/2))
print("Rudge-Kutta mean: " + str((np.mean(ant_T[:,250])+np.mean(ant_T[:,250]))/2))

# Esto no es muy útil pero voy a implementar un algoritmo que valore opciones europeas usando método de monte-carlo (por supuesto hay formas mucho mejores como directamente conseguir la solución (hay fórmula cerrada) (por cierto puedo usarla para ver qué tal funciona lo de arriba))
# Pero bueno es por pura práctica 


def payOff (S,K, put_or_call, bound = 0): 
    if (put_or_call == 'C'): 
        return max(S-K,bound) 
    elif (put_or_call == 'P'):
        return max (K-S, bound) 
    
def eu_GBM(r, sigma, S_0, K, num_steps, T, put_or_call, num_simulations = 10000, integration_method = 'E', ant_variates = False): 
    S = GBM(r, sigma, S_0, num_steps, T, num_simulations = num_simulations, integration_method = 'E', ant_variates = False)
    Vs = np.vectorize(payOff) (S[:, num_steps], K, put_or_call)
    V = math.exp(-r*T)*np.mean(Vs) 
    return V 

#Habría que añadir más payoffs. El vanilla es el más normal pero tampoco cuesta mucho. Es cambiar la fórmula payOff añadiendo un nuevo parámetro que sea predefinido como 'Vanilla'
# Adaptarlo para up-and-out barriers requiere modificar un poco así que se puede hacer una función diferente. SI el precio sube por encima de la barrera hay que dejar claro que la opción no se ejecuta y el payoff será cero  
# Definir otra función que sea up_out_eu_GBM y luego poner un if que si el payoff es ese se llame a esa función

# print(eu_GBM (0.06, 0.3, 5, 10, 250, 1, 'P'))


# Vamos! Da lo esperado!

def eu_cir_GBM (r_0, sigma, S_0, K, R, sigma_r, num_steps, T, put_or_call, num_simulations = 10000, integration = 'E', ant_variates = False, cir_integration = 'E', cir_ant_variates = False):

    # Esta función la tengo definida en el portátil 

    (S,r) = cir_GBM(r_0, sigma, S_0, sigma_r, num_steps,T, cir_integration, cir_ant_variates) 
    
    # Lo que viene ahora se puede hacer mejor vectorizando np.mean o algo así seguro
    
    average_r = np.zeros(num_simulations)
    for i in range(num_simulations):
        average_r[i] = np.mean(r[i, :])

    Vs = np.zeros (num_simulations)  
    for i in range(i):
        #esto creo que es correcto, cogemos la media de las r para cada valor y luego tomamos medias.
        Vs[i] = math.exp(-r[i]*T) *payOff(S[i, num_steps], K, put_or_call) 
    
    V = np.mean(Vs) 
    return V 

# Para esto hay que hacer lo de MLE para estimar los parámetros. Eso lo puedo implementar como una función a parte 

# La siguiente tarea que voy a hacer va a ser la de aproximar el valor de una opción americana con stopping prices horizontales y compararlo con  el valor por binomial option pricing 
def stopping_times (prices, beta):
    condition_array = prices > beta 
    (x,y) = prices.shape 
    stopping_times = np.zeros(x) 
    for i in range(x):
        first_index = int(np.argmax(condition_array[i]))
        if condition_array[i, first_index]:
            stopping_times[i] = int(first_index)
        else: 
            stopping_times[i] = int(y-1)  
    
    return stopping_times.astype(int) 

def value(prices, r, stopping_times, K, put_or_call): 
    (x,y) = prices.shape
    payOffs = np.zeros(x) 
    for i in range(x):
        payOffs[i] = math.exp (-r*stopping_times[i])*payOff(prices[i,stopping_times[i]], K, put_or_call) 
    mean_payOff = np.mean(payOffs) 
    return mean_payOff 

def am_GBM (S_0, r, sigma, K, put_or_call, T, num_steps):
    S = GBM (r, sigma, S_0, num_steps, T)
    betas = [K +0.1*i*K for i in range(1,20)]
    print(betas) 
    betas_values = np.zeros(19)
    for i in range(19):
        betas_values[i] = value(S, 0, stopping_times(S, betas[i]), K, put_or_call)
    return betas_values 

# Igual hay que cambiar un poco el enfoque y dedicar más tiempo a los otros dos apartados con respecto a este. Porque este aunque tiene muchos casos y tal, es menos utilizado en los casos sencillos que los otros. Aun asi sirve como base para cuando lea el libro más pro
# print(am_GBM (50, 0.1, 0.4, 50,'P', 5/12,250))
 
# Sale más precio del que debería pero se queda relativamente cerca xd (el valor real es 4.27 y el algoritmo calcula 4.30)
# Voy a probar si poniendo que si nunca hitea beta no se ejecuta la acción mejora la cosa. Aunque no debería