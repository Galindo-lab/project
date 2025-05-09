
import os
import requests

class GeminiShet:
    _instance = None
    _api_key = os.getenv("GEMINI_API_KEY") 
    _default_model = "gemini-2.0-flash"  
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiShet, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def generate_content(self, prompt, model=None):
        """Genera contenido usando la API de Gemini y devuelve solo el texto de la respuesta.
        
        Args:
            prompt (str): Texto para enviar a Gemini.
            model (str, optional): Modelo a usar. Si es None, usa el modelo por defecto.
            
        Returns:
            str: El texto generado por Gemini o None si hay error.
        """
        model_to_use = model if model is not None else self._default_model
        url = f"{self.base_url}/{model_to_use}:generateContent?key={self._api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            json_response = response.json()
            
            # Extraer el texto de la respuesta
            if 'candidates' in json_response and len(json_response['candidates']) > 0:
                candidate = json_response['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                    return candidate['content']['parts'][0].get('text', '')
            
            return "No se pudo obtener el texto de la respuesta"
            
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API de Gemini: {e}")
            return None






# Ejemplo de uso
if __name__ == "__main__":
    gemini = GeminiShet()  
    
    respuesta = gemini.generate_content("Siguiendo exactamente sin listas ni bold el siguiente formato dame una lista de 10 metas de un proyecto de desarrollo de software: nombre|descripcion-")
    print(respuesta)