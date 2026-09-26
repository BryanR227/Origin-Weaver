        const chatContainer = document.getElementById("chatContainer");
        const messages = document.getElementById("messages");
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");


        function sendMessage() {

            const text = messageInput.value.trim();

            // Don't send empty messages
            if (text === "") {
                return;
            }

            // Move welcome message to the top
            chatContainer.classList.add("started");

            // Add user's message
            addMessage(text, "user");

            // Clear input
            messageInput.value = "";

            // Temporary frontend-only chatbot response
            setTimeout(() => {
                addMessage(
                    "This is a frontend demo response.",
                    "bot"
                );
            }, 500);
        }


        function addMessage(text, sender) { 

            const row = document.createElement("div");
            row.classList.add("message-row", sender);

            const message = document.createElement("div");
            message.classList.add("message");

            message.textContent = text;

            row.appendChild(message);
            messages.appendChild(row);

            // Scroll to newest message
            messages.scrollTop = messages.scrollHeight;
        }


        // Send button
        sendButton.addEventListener("click", sendMessage);


        // Enter to send
        messageInput.addEventListener("keydown", function(event) {

            if (event.key === "Enter" && !event.shiftKey) {

                event.preventDefault();

                sendMessage();
            }

        });

