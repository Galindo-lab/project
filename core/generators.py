from django.template.loader import render_to_string
from django.shortcuts import render
from .llmshet import GeminiShet  
from .models import Goal, Project

class GeminiGenerator:
    def generate_goal(self, proyect:Project, context:str, pk:int) -> Goal:
        gemini = GeminiShet()
        
        prompt = render_to_string("prompts/generate_goal.txt", {
            "project": proyect,
            "pk": pk
        })
        
        print(prompt)        
        
        response = gemini.generate_content(prompt)
        
        print("Respuesta: ", response)
        
        # Aquí puedes procesar la respuesta y crear una instancia de Goal
        # Por ejemplo, si la respuesta es un string con el nombre y descripción separados por '|':
        name, description = response.split('|')
        
        goal = Goal(name=name, description=description, project=proyect)    
        return goal

    def generate_task(self, goal:Goal, context:str) -> dict:
        gemini = GeminiShet()
        prompt = render_to_string("prompts/generate_task.txt", {
            "goal": goal,
            "context": context
        })
        print(prompt)
        response = gemini.generate_content(prompt)
        print("Respuesta: ", response)
        # Espera formato: nombre|descripcion|duracion
        name, description, duration = response.split('|')
        return {
            "name": name.strip(),
            "description": description.strip(),
            "duration_hours": float(duration.strip())
        }
