
        const chatContainer = document.getElementById("chatContainer");
        const messages = document.getElementById("messages");
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");
        const experienceOptions = document.getElementById("experienceOptions");

        const questionnaireByLevel = {
            new: [
                "What kind of character sounds fun to play? Think of a vibe, personality, or fantasy you enjoy.",
                "Would you rather fight up close, use magic, help the group, or keep it open for now?",
                "Is there anything you want your character to be especially good at, or anything you want to avoid?"
            ],
            some: [
                "What is your character concept, personality, or overall vibe?",
                "Do you have a class or playstyle in mind? For example, a sneaky rogue or a protective fighter.",
                "Any ancestry, background, party role, or story detail you want included?",
                "Should the build prioritize a theme, combat strength, or a balance of both?"
            ],
            experienced: [
                "What is the character concept and the fantasy you want the build to deliver?",
                "Which class and subclass are you considering? Include alternatives if you are undecided.",
                "What ancestry, background, level, and ability-score method should I use?",
                "Any required feats, spells, multiclass plans, sourcebooks, or party role?",
                "What matters most: optimization, a specific theme, or a balance? Include any restrictions."
            ]
        };

        let questionnaire = null;

        experienceOptions.addEventListener("click", (event) => {
            const button = event.target.closest("button[data-level]");
            if (!button) {
                return;
            }

            const level = button.dataset.level;
            chatContainer.classList.add("started");
            experienceOptions.hidden = true;

            if (level === "free") {
                addMessage("Chat freely", "user");
                addMessage("What would you like help creating?", "bot");
                return;
            }

            const levelLabels = {
                new: "New to D&D",
                some: "Some experience",
                experienced: "Experienced"
            };
            questionnaire = {
                level: levelLabels[level],
                questions: questionnaireByLevel[level],
                answers: [],
                index: 0
            };
            addMessage(levelLabels[level], "user");
            askQuestion();
        });

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (text === "") {
                return;
            }

            chatContainer.classList.add("started");
            addMessage(text, "user");
            messageInput.value = "";

            if (questionnaire) {
                questionnaire.answers.push(text);
                questionnaire.index += 1;
                if (questionnaire.index < questionnaire.questions.length) {
                    askQuestion();
                } else {
                    const prompt = buildCharacterBrief();
                    questionnaire = null;
                    requestReply(prompt);
                }
                return;
            }

            requestReply(text);
        }

        function askQuestion() {
            const question = questionnaire.questions[questionnaire.index];
            addMessage(question, "guide");
            messageInput.placeholder = "Your answer...";
            messageInput.focus();
        }

        function buildCharacterBrief() {
            const answers = questionnaire.answers
                .map((answer, index) => `${index + 1}. ${questionnaire.questions[index]}\n${answer}`)
                .join("\n\n");
            return `Help me create a D&D character using this questionnaire. Player experience: ${questionnaire.level}. Match the detail and terminology to that experience level. Treat unspecified details as open choices.\n\n${answers}`;
        }

        async function requestReply(message) {
            messageInput.disabled = true;
            sendButton.disabled = true;

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message })
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
                messageInput.placeholder = "Type your message...";
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

            if (sender === "bot") {
                const speechButton = document.createElement("button");
                speechButton.type = "button";
                speechButton.className = "speech-button";
                speechButton.textContent = "Listen";
                speechButton.setAttribute("aria-label", "Listen to this reply");
                speechButton.addEventListener("click", () => playReplyAudio(text, row, speechButton));
                row.appendChild(speechButton);
            }

            messages.appendChild(row);

            messages.scrollTop = messages.scrollHeight;
        }

        async function playReplyAudio(text, row, button) {
            const existingAudio = row.querySelector("audio");
            if (existingAudio) {
                existingAudio.currentTime = 0;
                existingAudio.play().catch(() => {});
                return;
            }

            button.disabled = true;
            button.textContent = "Preparing...";

            try {
                const response = await fetch("/api/speech", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });
                const data = response.headers.get("content-type")?.includes("application/json")
                    ? await response.json()
                    : null;

                if (!response.ok) {
                    throw new Error(data?.error || "Could not generate audio.");
                }

                const audio = document.createElement("audio");
                audio.controls = true;
                audio.preload = "metadata";
                audio.src = URL.createObjectURL(await response.blob());
                audio.setAttribute("aria-label", "Reply audio playback");
                row.appendChild(audio);
                button.textContent = "Replay";

                try {
                    await audio.play();
                } catch {
                    button.textContent = "Play audio";
                }
            } catch (error) {
                let status = row.querySelector(".speech-status");
                if (!status) {
                    status = document.createElement("span");
                    status.className = "speech-status";
                    status.setAttribute("role", "status");
                    row.appendChild(status);
                }
                status.textContent = error.message;
                button.textContent = "Retry audio";
            } finally {
                button.disabled = false;
            }
        }


        sendButton.addEventListener("click", sendMessage);

        messageInput.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });