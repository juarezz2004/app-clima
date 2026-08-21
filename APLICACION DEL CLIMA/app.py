import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Traducción de códigos del clima a texto y emoji
WMO_CODES = {
    0: ("Cielo despejado", "☀️"),
    1: ("Principalmente despejado", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Niebla", "🌫️"),
    48: ("Niebla con escarcha", "🌫️"),
    51: ("Llovizna ligera", "🌧️"),
    53: ("Llovizna moderada", "🌧️"),
    55: ("Llovizna intensa", "🌧️"),
    61: ("Lluvia ligera", "🌧️"),
    63: ("Lluvia moderada", "🌧️"),
    65: ("Lluvia fuerte", "🌧️"),
    71: ("Nieve ligera", "❄️"),
    73: ("Nieve moderada", "❄️"),
    75: ("Nieve fuerte", "❄️"),
    80: ("Chubascos ligeros", "🌦️"),
    81: ("Chubascos moderados", "🌦️"),
    82: ("Chubascos violentos", "⛈️"),
    95: ("Tormenta eléctrica", "🌩️"),
    96: ("Tormenta con granizo ligero", "⛈️"),
    99: ("Tormenta con granizo fuerte", "⛈️"),
}

def obtener_coordenadas(ciudad):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={ciudad}&limit=1"
    headers = {"User-Agent": "FlaskWeatherApp/1.0"}
    try:
        respuesta = requests.get(url, headers=headers, timeout=5)
        datos = respuesta.json()
        if datos:
            return {
                "lat": datos[0]["lat"],
                "lon": datos[0]["lon"],
                "nombre": datos[0]["display_name"].split(",")[0],
                "pais": datos[0]["display_name"].split(",")[-1].strip()
            }
    except Exception as e:
        print(f"Error al obtener coordenadas: {e}")
    return None

def obtener_clima(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&relativehumidity_2m=true"
    try:
        respuesta = requests.get(url, timeout=5)
        datos = respuesta.json()
        if "current_weather" in datos:
            clima_raw = datos["current_weather"]
            code = clima_raw.get("weathercode", 0)
            condicion, emoji = WMO_CODES.get(code, ("Desconocido", "🌡️"))
            
            return {
                "temperatura": round(clima_raw["temperature"]),
                "viento": clima_raw["windspeed"],
                "condicion": condicion,
                "emoji": emoji
            }
    except Exception as e:
        print(f"Error al obtener datos del clima: {e}")
    return None

@app.route("/", methods=["GET", "POST"])
def inicio():
    clima_data = None
    error = None
    ciudad_buscada = ""

    if request.method == "POST":
        ciudad_buscada = request.form.get("ciudad", "").strip()
        if ciudad_buscada:
            ubicacion = obtener_coordenadas(ciudad_buscada)
            if ubicacion:
                clima_info = obtener_clima(ubicacion["lat"], ubicacion["lon"])
                if clima_info:
                    clima_data = {
                        "ciudad": ubicacion["nombre"],
                        "pais": ubicacion["pais"],
                        "temperatura": clima_info["temperatura"],
                        "viento": clima_info["viento"],
                        "condicion": clima_info["condicion"],
                        "emoji": clima_info["emoji"]
                    }
                else:
                    error = "No se pudieron obtener los datos del clima."
            else:
                error = f'No se encontró la ciudad "{ciudad_buscada}". Verificá el nombre.'
        else:
            error = "Por favor, ingresá el nombre de una ciudad."

    return render_template("index.html", clima=clima_data, error=error, ciudad_buscada=ciudad_buscada)

if __name__ == "__main__":
    app.run(debug=True)