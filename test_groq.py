from groq import Groq
import os   

# 1. Configuración
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

print("Enviando pregunta a Llama-3 en Groq (Gratis y ultra rápido)...")

try:
    # Usamos llama-3.3-70b que es equivalente a GPT-4 en inteligencia
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Hola, respondé: 'Conexión Groq exitosa'."}
        ]
    )
    
    print("-" * 30)
    print("Respuesta de la IA:", completion.choices[0].message.content)
    print("-" * 30)
except Exception as e:
    print("ERROR:", e)