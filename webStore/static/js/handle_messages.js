$(document).ready(function () {
    let currentConversationId = null;
    let lastMessageId = 0;

    // Obsługa zmiany konwersacji
    $(".list-group-item").click(function () {
        $(".list-group-item").removeClass("active");
        $(this).addClass("active");

        currentConversationId = $(this).attr("data-conversation-id");
        $("#chat-title").text($(this).text());

        // Załaduj wiadomości
        loadMessages(currentConversationId);

        // Rozpocznij odpytywanie nowych wiadomości
        stopFetchingMessages(); // Zatrzymaj poprzedni interwał (jeśli istnieje)
        startFetchingMessages(); // Rozpocznij nowy interwał
    });

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
                        lastMessageId = message.id; // Zaktualizuj ostatnie ID wiadomości
                    });
                } else {
                    $("#chat-messages").html('<p class="text-muted">Brak wiadomości w tej konwersacji.</p>');
                }

                // Zapisz ostatnią otwartą konwersację
                $.ajax({
                    url: `/messages/${conversationId}/save-last-opened/`,  // Endpoint do zapisania konwersacji
                    method: "POST",
                    headers: {
                        "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
                    },
                });
            },
            error: function () {
                alert("Nie udało się załadować wiadomości.");
            },
        });
    }

    // Funkcja do automatycznego sprawdzania nowych wiadomości
    function fetchNewMessages() {
        if (!currentConversationId) return;

        $.ajax({
            url: `/messages/${currentConversationId}/fetch-new/`,
            method: "GET",
            data: { last_message_id: lastMessageId },
            success: function (data) {
                if (data.new_messages && data.new_messages.length > 0) {
                    data.new_messages.forEach((message) => {
                        const isSentByUser = message.sender === loggedInUser;
                        const messageHtml = `
                        <div class="message ${isSentByUser ? "message-sent" : "message-received"}">
                            <p>${message.content}</p>
                            <span class="timestamp">${message.timestamp}</span>
                        </div>`;

                        $("#chat-messages").append(messageHtml);
                        lastMessageId = message.id; // Zaktualizuj ostatnie ID wiadomości
                    });

                    // Automatyczne przewinięcie na dół
                    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
                }

                // Jeśli zamówienie jest zakończone, zatrzymaj odpytywanie
                if (data.is_completed) {
                    stopFetchingMessages(); // Zatrzymaj interwał
                    console.log("Zamówienie zakończone - odpytywanie zatrzymane.");
                }
            },
            error: function () {
                console.error("Nie udało się pobrać nowych wiadomości.");
            },
        });
    }

// Zmienna globalna do kontrolowania interwału
    let fetchInterval = null; // Globalna zmienna dla interwału

    function startFetchingMessages() {
        if (fetchInterval) return; // Jeśli interwał już działa, nie ustawiaj go ponownie

        fetchInterval = setInterval(() => {
            fetchNewMessages();
        }, 5000); // Odpytuj co 5 sekund
    }

    function stopFetchingMessages() {
        if (fetchInterval) {
            clearInterval(fetchInterval); // Zatrzymaj interwał
            fetchInterval = null; // Zresetuj zmienną
        }
    }

    // Automatyczne ładowanie ostatniej otwartej konwersacji po odświeżeniu
    const lastConversationId = $(".list-group-item.active").data("conversation-id");
    if (lastConversationId) {
        currentConversationId = lastConversationId;
        loadMessages(lastConversationId);
        startFetchingMessages();
    }

    // Obsługa wysyłania wiadomości
    $("#message-form").submit(function (e) {
        e.preventDefault();
        const content = $("#message-input").val().trim();
        if (!content) return;

        if (!currentConversationId) {
            alert("Nie wybrano konwersacji.");
            return;
        }

        $.ajax({
            url: `/messages/send/`,
            method: "POST",
            data: {
                conversation_id: currentConversationId,
                content: content,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function () {
                $("#message-input").val(""); // Wyczyść pole tekstowe
                fetchNewMessages(); // Natychmiastowe odświeżenie wiadomości z serwera
            },
            error: function () {
                alert("Nie udało się wysłać wiadomości.");
            },
        });
    });

    // Automatyczne ładowanie ostatniej otwartej konwersacji po odświeżeniu
    $(document).ready(function () {
        let currentConversationId = null;
        let lastMessageId = 0;

        const lastConversationElement = $(".list-group-item.active");
        if (lastConversationElement.length > 0) {
            currentConversationId = lastConversationElement.data("conversation-id");
            $("#chat-title").text(lastConversationElement.text());
            loadMessages(currentConversationId);
            startFetchingMessages();
        }
    });
});
