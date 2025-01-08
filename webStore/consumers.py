from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Pobierz `conversation_id` z URL
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"

        # Dołącz do grupy kanałów
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Opuść grupę kanałów
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Odbieranie wiadomości od WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("content")
        sender = self.scope["user"].username  # Pobierz nazwę użytkownika zalogowanego

        # Wyślij wiadomość do grupy kanałów
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "content": content,
                "sender": sender,
            }
        )

    # Obsługa wiadomości z grupy kanałów
    async def chat_message(self, event):
        content = event["content"]
        sender = event["sender"]

        # Wyślij wiadomość do WebSocket
        await self.send(text_data=json.dumps({
            "content": content,
            "sender": sender,
        }))
