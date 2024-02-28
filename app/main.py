from fastapi import FastAPI, Response
from pydantic import BaseModel
import json

# Funkcja do odczytu danych z pliku
def read_data_from_file():
    try:
        with open("messages.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Funkcja do zapisu danych do pliku
def write_data_to_file(data):
    with open("messages.json", "w") as file:
        json.dump(data, file, indent=2)

messages_db = read_data_from_file()  # Wczytywanie danych z pliku
message_id_counter = max([message["id"] for message in messages_db], default=0) + 1  # Ustalanie aktualnego licznika ID

class Message(BaseModel):
    id: int = None
    text: str
    user: str

app = FastAPI()

def set_message_id_counter():
    global message_id_counter
    return message_id_counter


@app.post("/messages/", tags=["Post"])
async def send_message(
    text: str,
    user: str
):
    '''
        Dodawanie nowej wiadomosci
        Parametry: tekst, uzytkownik.
        ID jest automatycznie inkrementowane najnizsze z dostepnych
        Return: Informacja o wysłaniu wiadomosci oraz jej ID
    '''
    global message_id_counter
    message_id_counter = max([message["id"] for message in messages_db], default=0) + 1  # Aktualizacja licznika ID
    message = Message(id=message_id_counter, text=text, user=user)
    messages_db.append(message.dict())
    write_data_to_file(messages_db)  # Zapis danych do pliku
    return Response(content=f"Message sent successfully. ID: {message.id}", status_code=201)

@app.get("/messages/{message_id}", tags=["Get"])
def get_message(message_id: int):
    '''
        Pobieranie wiadomosci po ID
        Parametry: ID
        Return: wyswietlany jest json obiektu Message (tekst,user,ID)
    '''
    for message in messages_db:
        if message["id"] == message_id:
            return {"message": message}
    return ({"error": "Message not found"})


@app.get("/messages/", tags=["Get"])
def get_all_messages():
    '''
        Wyswietlanie calej bazy danych
        Return: wszystkie obiekty Message
    '''
    return {"messages": messages_db}

@app.put("/messages/{message_id}", tags=["Put"])
def update_message(
    message_id: int,
    text: str,
    user: str
):
    '''
        Edycja wiadomosci poprze ID
        Parametry: ID
        Return: Informacja o pomyslnej edycji wiadomosci
        Przy niepoprawnym ID informacja o braku takiej wiadomosci
    '''
    updated_message = {"id": message_id, "text": text, "user": user}
    for i, message in enumerate(messages_db):
        if message["id"] == message_id:
            messages_db[i] = updated_message
            write_data_to_file(messages_db)  # Zapis danych do pliku
            return {"message": "Message updated successfully"}
    return ({"error": "Message not found"})

@app.delete("/messages/{message_id}", tags=["Delete"])
def delete_message(message_id: int):
    '''
        Usuwanie wiadomosci po ID
        Parametry: ID
        Return: Potwierdzenie usuniecia wiadomosci nawet jesli nie ma takiej widomosci o takim ID
    '''
    global messages_db
    messages_db = [message for message in messages_db if message["id"] != message_id]
    write_data_to_file(messages_db)  # Zapis danych do pliku
    return {"message": "Message deleted successfully"}

@app.delete("/messages/", tags=["Delete"])
def delete_all_messages():
    '''
        Usuwanie calej bazy danych
        Return: potwierdzenie usuniecia calej bazy
    '''
    global messages_db
    messages_db = []
    write_data_to_file(messages_db)  # Zapis danych do pliku
    return {"message": "All messages deleted successfully"}
