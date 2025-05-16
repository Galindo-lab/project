from django.template.loader import render_to_string
from django.shortcuts import render
from .llmshet import GeminiShet
from .models import Goal, Project


class GeminiGenerator:
    def generate_goal(self, proyect: Project, context: str, pk: int) -> Goal:
        gemini = GeminiShet()

        prompt = render_to_string(
            "prompts/generate_goal.txt", {"project": proyect, "pk": pk}
        )

        response = gemini.generate_content(prompt)
        name, description = response.split("|")

        goal = Goal(name=name, description=description, project=proyect)
        return goal

    def generate_task(self, goal: Goal, context: str) -> dict:
        gemini = GeminiShet()
        prompt = render_to_string(
            "prompts/generate_task.txt", {"goal": goal, "context": context}
        )

        response = gemini.generate_content(prompt)

        name, description, duration = response.split("|")
        return {
            "name": name.strip(),
            "description": description.strip(),
            "duration_hours": float(duration.strip()),
        }

    def generate_project_description(self, answers: dict) -> str:
        prompt = render_to_string(
            "prompts/generate_project_description.txt",
            {
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
            },
        )
        gemini = GeminiShet()
        descripcion = gemini.generate_content(prompt)
        return descripcion

    def generate_resource(self, project: Project, context: str = "") -> dict:
        gemini = GeminiShet()
        existing_resources = project.resource_set.all()
        prompt = render_to_string(
            "prompts/generate_resource.txt",
            {
                "project": project,
                "context": context,
                "existing_resources": existing_resources,
            },
        )

        response = gemini.generate_content(prompt)

        name, tipo, costo = response.split("|")
        return {
            "name": name.strip(),
            "type": tipo.strip(),
            "cost_per_hour": float(costo.strip()),
        }
