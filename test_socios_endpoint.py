import requests
import json

def test_socios_endpoint():
    try:
        # Probar el endpoint GET /socios
        response = requests.get("http://localhost:8000/socios")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito! Se encontraron {len(data)} socios")
            print("Primer socio:")
            if data:
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que uvicorn esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_socios_endpoint() 