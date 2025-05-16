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

    def generate_project_description(self, answers: dict) -> str:
        """
        Genera una descripción de proyecto emprendedor usando IA a partir de un cuestionario de 10 preguntas.
        :param answers: Diccionario con las respuestas del formulario.
        :return: Descripción generada por IA.
        """
        prompt = render_to_string("prompts/generate_project_description.txt", {
            "idea": answers.get("idea", ""),
            "experiencia": answers.get("experiencia", ""),
            "implementado": answers.get("implementado", ""),
            "objetivo": answers.get("objetivo", ""),
            "publico": answers.get("publico", ""),
            "problema": answers.get("problema", ""),
            "solucion": answers.get("solucion", ""),
            "diferenciador": answers.get("diferenciador", ""),
            "recursos": answers.get("recursos", ""),
            "proximo_paso": answers.get("proximo_paso", ""),
        })
        gemini = GeminiShet()
        descripcion = gemini.generate_content(prompt)
        return descripcion