import requests

def send_message(message):
    """Gửi một câu hỏi đến Rasa server và nhận kết quả."""
    response = requests.post('http://localhost:5005/model/parse', json={'query': message})
    return response.json()

if __name__ == "__main__":
    result = send_message("Tôi cần tìm laptop dell")
    print("Intent:", result['intent']['name'])
    print("Entities:", result['entities'])