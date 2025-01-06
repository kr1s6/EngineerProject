$(document).ready(function () {
    let currentChatId = 1; // Aktualna konwersacja
    let lastMessageId = 0; // ID ostatniej wiadomości

    // Obsługa zmiany konwersacji
    $(".list-group-item").click(function () {
        $(".list-group-item").removeClass("active");
        $(this).addClass("active");

        currentChatId = $(this).data("chat-id");
        $("#chat-title").text($(this).text());
        loadMessages(currentChatId);
    });

    // Funkcja do ładowania wiadomości
    function loadMessages(chatId) {
        $.ajax({
            url: `/messages/${chatId}/`,
            method: "GET",
            success: function (data) {
                $("#chat-messages").empty();
                data.messages.forEach(function (message) {
                    const messageHtml = `
                        <div class="message ${message.sender === "user" ? "message-sent" : "message-received"}">
                            <p>${message.content}</p>
                            <span class="timestamp">${message.timestamp}</span>
                        </div>
                    `;
                    $("#chat-messages").append(messageHtml);
                    lastMessageId = message.id; // Aktualizuj ostatnie ID
                });
            },
            error: function () {
                alert("Nie udało się załadować wiadomości.");
            },
        });
    }

    // Funkcja do sprawdzania nowych wiadomości
    function fetchNewMessages() {
        $.ajax({
            url: `/messages/${currentChatId}/fetch-new/`,
            method: "GET",
            data: { last_message_id: lastMessageId },
            success: function (data) {
                if (data.new_messages && data.new_messages.length > 0) {
                    const chatMessages = $("#chat-messages");
                    data.new_messages.forEach(function (message) {
                        const messageHtml = `
                            <div class="message ${message.sender === "user" ? "message-sent" : "message-received"}">
                                <p>${message.content}</p>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>
                        `;
                        chatMessages.append(messageHtml);
                        lastMessageId = message.id; // Aktualizuj ostatnie ID
                    });

                    // Automatyczne przewinięcie do dołu
                    chatMessages.scrollTop(chatMessages[0].scrollHeight);
                }
            },
            error: function () {
                console.error("Błąd przy sprawdzaniu nowych wiadomości.");
            },
        });
        $("#loading-indicator").show();
        $.ajax({
            url: `/messages/${chatId}/`,
            method: "GET",
            success: function (data) {
                $("#loading-indicator").hide();
                // Aktualizacja wiadomości...
            },
            error: function () {
                $("#loading-indicator").hide();
                alert("Nie udało się załadować wiadomości.");
            },
        });
    }

    // Cykliczne sprawdzanie nowych wiadomości co 5 sekund
    setInterval(fetchNewMessages, 5000);

    // Obsługa wysyłania wiadomości
    $("#message-form").submit(function (e) {
        e.preventDefault();
        const content = $("#message-input").val().trim();
        if (!content) return;

        $.ajax({
            url: `/messages/send/`,
            method: "POST",
            data: {
                chat_id: currentChatId,
                content: content,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function () {
                $("#message-input").val("");
                fetchNewMessages(); // Sprawdź nowe wiadomości natychmiast po wysłaniu
            },
            error: function () {
                alert("Nie udało się wysłać wiadomości.");
            },
        });
    });

});
