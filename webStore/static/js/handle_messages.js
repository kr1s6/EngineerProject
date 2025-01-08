$(document).ready(function () {
    let currentConversationId = null;
    let lastMessageId = 0;
    let socket = null;

    // Automatyczne ładowanie ostatniej otwartej konwersacji
    const lastConversationId = $("#your_messages .list-group-item.active").data("conversation-id");
    if (lastConversationId) {
        currentConversationId = lastConversationId;
        connectToWebSocket(currentConversationId);
        loadMessages(currentConversationId);
    }

    // Obsługa zmiany konwersacji
    $(".list-group-item").click(function () {
        $(".list-group-item").removeClass("active");
        $(this).addClass("active");

        const newConversationId = $(this).data("conversation-id");
        if (currentConversationId !== newConversationId) {
            currentConversationId = newConversationId;

            // Rozłącz stare WebSocket połączenie i podłącz nowe
            if (socket) {
                socket.close();
            }
            connectToWebSocket(currentConversationId);

            $("#chat-title").text($(this).text());
            loadMessages(currentConversationId);
            saveLastOpenedConversation(currentConversationId);
        }
    });

    // Obsługa wysyłania wiadomości
    $("#message-form").submit(function (e) {
        e.preventDefault();
        const content = $("#message-input").val().trim();
        if (!content) return;

        if (!socket || socket.readyState !== WebSocket.OPEN) {
            alert("WebSocket nie jest podłączony. Spróbuj odświeżyć stronę.");
            return;
        }

        const messageData = {
            conversation_id: currentConversationId,
            content: content,
        };

        socket.send(JSON.stringify(messageData));
        $("#message-input").val(""); // Wyczyść pole tekstowe
    });

    // Funkcja do podłączenia WebSocket
    function connectToWebSocket(conversationId) {
        const wsUrl = `ws://${window.location.host}/ws/messages/${conversationId}/`;
        socket = new WebSocket(wsUrl);

        socket.onopen = function () {
            console.log("WebSocket podłączony do konwersacji:", conversationId);
        };

        socket.onmessage = function (event) {
            const data = JSON.parse(event.data);

            // Dodaj wiadomość do listy
            const isSentByUser = data.sender === loggedInUser;
            const messageHtml = `
                <div class="message ${isSentByUser ? "message-sent" : "message-received"}">
                    <p>${data.content}</p>
                    <span class="timestamp">${data.timestamp}</span>
                </div>`;
            $("#chat-messages").append(messageHtml);

            // Automatyczne przewinięcie na dół
            $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
        };

        socket.onclose = function () {
            console.log("WebSocket rozłączony.");
        };

        socket.onerror = function (error) {
            console.error("WebSocket error:", error);
        };
    }

    // Funkcja do ładowania wiadomości
    function loadMessages(conversationId) {
        if (!conversationId) return;

        $.ajax({
            url: `/messages/${conversationId}/load/`,
            method: "GET",
            success: function (data) {
                $("#chat-messages").empty();

                if (data.messages.length > 0) {
                    data.messages.forEach((message) => {
                        const messageHtml = `
                            <div class="message ${message.sender === loggedInUser ? "message-sent" : "message-received"}">
                                <p>${message.content}</p>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>`;
                        $("#chat-messages").append(messageHtml);
                        lastMessageId = message.id;
                    });

                    // Przewiń na dół
                    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
                } else {
                    $("#chat-messages").html('<p class="text-muted">Brak wiadomości w tej konwersacji.</p>');
                }
            },
            error: function () {
                alert("Nie udało się załadować wiadomości.");
            },
        });
    }

    // Funkcja do zapisywania ostatnio otwartej konwersacji
    function saveLastOpenedConversation(conversationId) {
        $.ajax({
            url: `/messages/${conversationId}/save-last-opened/`,
            method: "POST",
            headers: {
                "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function () {
                console.log(`Zapisano ostatnio otwartą konwersację: ${conversationId}`);
            },
            error: function () {
                console.error("Nie udało się zapisać ostatnio otwartej konwersacji.");
            },
        });
    }
});