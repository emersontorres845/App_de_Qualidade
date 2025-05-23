
import pytest
import requests 
import subprocess 
import time
import os
import sys 


BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session", autouse=True)
def start_flask_app():
    """
    Fixture para iniciar o servidor Flask antes dos testes
    e pará-lo depois que todos os testes da sessão forem concluídos.
    O 'autouse=True' garante que esta fixture seja usada automaticamente.
    'scope="session"' garante que ela seja executada apenas uma vez por sessão de teste.
    """
    
    app_file_path = os.path.join(os.path.dirname(__file__), "app.py")

    
    process = subprocess.Popen(
        [sys.executable, app_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    
    max_retries = 20 
    retry_delay = 0.5  
    server_ready = False
    
    print("\nAguardando o servidor Flask iniciar...")
    for i in range(max_retries):
        try:
            
            response = requests.get(f"{BASE_URL}/items", timeout=1) 
            if response.status_code == 200: 
                server_ready = True
                print("Servidor Flask iniciado e pronto.")
                break
            else:
                
                print(f"Tentativa {i+1}/{max_retries}: Servidor respondeu com status {response.status_code}. Tentando novamente...")
        except requests.exceptions.ConnectionError:
            print(f"Tentativa {i+1}/{max_retries}: Conexão recusada. Tentando novamente...")
        except requests.exceptions.Timeout:
            print(f"Tentativa {i+1}/{max_retries}: Timeout na conexão. Tentando novamente...")
        
        time.sleep(retry_delay)
            
    if not server_ready:
        
        try:
            stdout, stderr = process.communicate(timeout=1) 
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            stdout = stdout + b"[communicate timeout after kill]"
            stderr = stderr + b"[communicate timeout after kill]"
            
        process.terminate() 
        process.wait()
        pytest.fail(
            f"O servidor Flask falhou ao iniciar em {max_retries * retry_delay} segundos.\n"
            f"Comando: {' '.join([sys.executable, app_file_path])}\n"
            f"STDOUT: {stdout.decode(errors='replace')}\n"
            f"STDERR: {stderr.decode(errors='replace')}",
            pytrace=False 
        )

    yield 

    
    print("\nParando o servidor Flask...")
    process.terminate()
    try:
        process.wait(timeout=5) 
        print("Servidor Flask parado.")
    except subprocess.TimeoutExpired:
        print("Timeout ao esperar o servidor Flask parar. Forçando o encerramento...")
        process.kill()
        process.wait()
        print("Servidor Flask forçado a parar.")


def test_get_items_empty():
    """Testa o endpoint GET /items quando não há itens."""
    response = requests.get(f"{BASE_URL}/items")
    assert response.status_code == 200
    
    assert response.json() == []

def test_post_item():
    """Testa o endpoint POST /items para adicionar um novo item."""
    payload = {"name": "Test Item 1"}
    response = requests.post(f"{BASE_URL}/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Item 1"
    

def test_post_item_missing_name():
    """Testa o endpoint POST /items com dados faltando."""
    payload = {} 
    response = requests.post(f"{BASE_URL}/items", json=payload)
    assert response.status_code == 400
    assert response.json() == {"error": "Missing name in request body"}

def test_get_specific_item():
    """Testa o endpoint GET /items/<item_id> para um item específico."""
    
    payload_post = {"name": "Specific Item for GET"}
    response_post = requests.post(f"{BASE_URL}/items", json=payload_post)
    assert response_post.status_code == 201, f"Falha ao criar item: {response_post.text}"
    item_id = response_post.json()["id"]

    
    response_get = requests.get(f"{BASE_URL}/items/{item_id}")
    assert response_get.status_code == 200, f"Item não encontrado: {response_get.text}"
    data_get = response_get.json()
    assert data_get["id"] == item_id
    assert data_get["name"] == "Specific Item for GET"

def test_get_specific_item_not_found():
    """Testa o endpoint GET /items/<item_id> para um item que não existe."""
    non_existent_id = 99999 
    response = requests.get(f"{BASE_URL}/items/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"error": "Item not found"}

def test_get_items_after_adding_multiple():
    """Testa o endpoint GET /items depois de adicionar alguns itens."""
    
    initial_items_count = len(requests.get(f"{BASE_URL}/items").json())

    item_a_payload = {"name": "Item A"}
    item_b_payload = {"name": "Item B"}
    
    response_a = requests.post(f"{BASE_URL}/items", json=item_a_payload)
    assert response_a.status_code == 201
    
    response_b = requests.post(f"{BASE_URL}/items", json=item_b_payload)
    assert response_b.status_code == 201

    response_get_all = requests.get(f"{BASE_URL}/items")
    assert response_get_all.status_code == 200
    items = response_get_all.json()
    
    
    assert len(items) == initial_items_count + 2
    
    item_names = [item['name'] for item in items]
    assert "Item A" in item_names
    assert "Item B" in item_names


