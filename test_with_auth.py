import requests
import json

def test_with_auth():
    try:
        # 1. Hacer login para obtener el token
        login_data = {
            "correo_electronico": "admin@ceas.com",  # Ajusta según tu usuario
            "contrasena": "admin123"  # Ajusta según tu contraseña
        }
        
        print("🔐 Intentando hacer login...")
        login_response = requests.post("http://localhost:8000/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            print("✅ Login exitoso!")
            print(f"Token: {token[:50]}...")
            
            # 2. Probar el endpoint de socios con el token
            headers = {"Authorization": f"Bearer {token}"}
            print("\n📋 Probando endpoint de socios...")
            
            socios_response = requests.get("http://localhost:8000/socios", headers=headers)
            
            print(f"Status Code: {socios_response.status_code}")
            
            if socios_response.status_code == 200:
                socios_data = socios_response.json()
                print(f"✅ Éxito! Se encontraron {len(socios_data)} socios")
                print("Primer socio:")
                if socios_data:
                    print(json.dumps(socios_data[0], indent=2, ensure_ascii=False))
            else:
                print(f"❌ Error en socios: {socios_response.status_code}")
                print(f"Response: {socios_response.text}")
                
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que uvicorn esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_with_auth() 