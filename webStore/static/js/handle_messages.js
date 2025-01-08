$(document).ready(function () {
    let currentConversationId = null;
    let lastMessageId = 0;
    let fetchInterval = null;

    // Automatyczne ładowanie ostatniej otwartej konwersacji
    const lastConversationId = $("#your_messages .list-group-item.active").data("conversation-id");
    if (lastConversationId) {
        currentConversationId = lastConversationId;
        loadMessages(lastConversationId);
        startFetchingMessages();
    }

    // Obsługa zmiany konwersacji
    $(".list-group-item").click(function () {
        $(".list-group-item").removeClass("active");
        $(this).addClass("active");

        currentConversationId = $(this).attr("data-conversation-id");
        $("#chat-title").text($(this).text());

        // Załaduj wiadomości
        loadMessages(currentConversationId);

        // Rozpocznij odpytywanie nowych wiadomości
        stopFetchingMessages();
        startFetchingMessages();

        // Zapisz ostatnio otwartą konwersację
        saveLastOpenedConversation(currentConversationId);
    });

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
                        lastMessageId = message.id;
                    });

                    // Automatyczne przewinięcie na dół
                    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
                }
            },
            error: function () {
                console.error("Nie udało się pobrać nowych wiadomości.");
            },
        });
    }

    // Funkcja start/stop do odpytywania wiadomości
    function startFetchingMessages() {
        if (fetchInterval) return;

        fetchInterval = setInterval(() => {
            fetchNewMessages();
        }, 2000); // Odpytywanie co 50 sekundy
    }

    function stopFetchingMessages() {
        if (fetchInterval) {
            clearInterval(fetchInterval);
            fetchInterval = null;
        }
    }
});
