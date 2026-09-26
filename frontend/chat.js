        const chatContainer = document.getElementById("chatContainer");
        const messages = document.getElementById("messages");
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");


        async function sendMessage() {

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

            messageInput.disabled = true;
            sendButton.disabled = true;

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Request failed.");
                }

                addMessage(data.reply || "Gemini returned an empty response.", "bot");
            } catch (error) {
                addMessage(`Could not get a reply: ${error.message}`, "bot");
            } finally {
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();
            }
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

