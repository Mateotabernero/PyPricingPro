
class MCGBMOption: 
    def __init__(self, spot_price, strike_price, maturity, option_type, call_or_put, risk_free_rate, volatility): 
        self.S   = spot_price 
        self.K   = strike_price 
        self.T   = maturity 
        self.r   = risk_free_rate
        self.sig = volatility 

        self.optionType = option_type
        self.CoP        = call_or_put

    # Aquí definiría las payOffs según el tipo de opción con la que estemos tratando y la definiría como un atributo de clase


    def generate_paths(self, num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False):
        S = GBM.GBM(self.r, self.sig, self.S, num_steps, self.T, num_simulations, integration_method, ant_variates)
     
        return S 
    

    def price(self, num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False): 

        # Aquí creo que da un poco igual si cogemos self.generate_paths o la función original GBM.GBM. Si al ginal son iguales 
        # Esta igual mejor porque no hay que meter tantos argumentos (como r, sigma, o T) 

        S =  self.generate_paths(num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False)
        
        return np.exp(-self.r*self.T)*(np.mean(self.payOff(S))) 

    def delta(self, num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False):
        new_S = self.S*1.01

        price = self.price(num_steps, num_simulations, integration_method, ant_variates) 

        new_S = GBM.GBM(self.r, self.sig, new_S, num_steps, self.T, num_simulations, integration_method, ant_variates)
        new_price = np.exp(-self.r*self.T)*(np.mean(self.payOff(new_S)))
         
        return (new_price - price)/(new_S - self.S) 

    def vega(self, num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False): 
        new_sig = self.sig*1.01

        price = self.price(num_steps, num_simulations, integration_method, ant_variates) 

        new_S = GBM.GBM(self.r, new_sig, self.S, num_steps, self.T, num_simulations, integration_method, ant_variates)
        new_price = np.exp(-self.r*self.T)*(np.mean(self.payOff(new_S)))

        return (new_price - price)/(new_S - self.S) 
    
    def theta(self, num_steps, num_simulations = 10**4, integration_method = 'E', ant_variates = False): 

        # Aquí hay varias formas de afrontarlo. Una es como las de arriba. Aunque puede ser más inteligente generar los caminos solamente una vez y coger los caminos salvo el ultimo punto como un valor para un T menor 
        
