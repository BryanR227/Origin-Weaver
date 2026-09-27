
        const chatContainer = document.getElementById("chatContainer");
        const messages = document.getElementById("messages");
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");
        const experienceOptions = document.getElementById("experienceOptions");
        const accountButton = document.getElementById("accountButton");
        const authDialog = document.getElementById("authDialog");
        const closeAuthButton = document.getElementById("closeAuthButton");
        const authModeButtons = document.querySelectorAll("[data-auth-mode]");
        const authTitle = document.getElementById("authTitle");
        const authForm = document.getElementById("authForm");
        const authEmail = document.getElementById("authEmail");
        const authPassword = document.getElementById("authPassword");
        const authConfirmField = document.getElementById("authConfirmField");
        const authConfirmPassword = document.getElementById("authConfirmPassword");
        const authSubmit = document.getElementById("authSubmit");
        const authStatus = document.getElementById("authStatus");

        let currentUser = null;

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

        function setAuthMode(mode) {
            const isSignUp = mode === "signup";
            authTitle.textContent = isSignUp ? "Create your account" : "Welcome back";
            authSubmit.textContent = isSignUp ? "Create account" : "Sign in";
            authPassword.autocomplete = isSignUp ? "new-password" : "current-password";
            authConfirmField.hidden = !isSignUp;
            authConfirmPassword.required = isSignUp;
            authForm.reset();
            authStatus.textContent = "";

            authModeButtons.forEach((button) => {
                button.setAttribute("aria-pressed", String(button.dataset.authMode === mode));
            });
        }

       function updateAccountButton() {
            accountButton.textContent = currentUser ? currentUser.email : "Sign in / Sign up";
        }

        async function checkSession() {
            try {
                const response = await fetch("/api/auth/me", { credentials: "same-origin" });
                const data = await response.json();
                currentUser = data.user || null;
            } catch {
                currentUser = null;
            }
            updateAccountButton();
        }

        accountButton.addEventListener("click", async () => {
            if (currentUser) {
                accountButton.disabled = true;
                try {
                    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
                } catch {
                    // Ignore network errors on logout; we clear local state regardless.
                }
                currentUser = null;
                updateAccountButton();
                accountButton.disabled = false;
                return;
            }

            setAuthMode("signin");
            authDialog.showModal();
            authEmail.focus();
        });

        closeAuthButton.addEventListener("click", () => authDialog.close());

        authModeButtons.forEach((button) => {
            button.addEventListener("click", () => setAuthMode(button.dataset.authMode));
        });

        authConfirmPassword.addEventListener("input", () => {
            authConfirmPassword.setCustomValidity("");
        });

        authForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const isSignUp = authConfirmField.hidden === false;
            if (isSignUp) {
                authConfirmPassword.setCustomValidity(
                    authConfirmPassword.value === authPassword.value ? "" : "Passwords must match."
                );
                if (!authForm.reportValidity()) {
                    return;
                }
            }

            const email = authEmail.value.trim();
            const password = authPassword.value;

            authSubmit.disabled = true;
            authStatus.textContent = isSignUp ? "Creating your account…" : "Signing in…";

            try {
                const endpoint = isSignUp ? "/api/auth/signup" : "/api/auth/login";
                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "same-origin",
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();

                if (!response.ok) {
                    authStatus.textContent = data.error || "Something went wrong. Please try again.";
                    return;
                }

                currentUser = data.user;
                updateAccountButton();
                authStatus.textContent = "Success!";
                setTimeout(() => authDialog.close(), 400);
            } catch (error) {
                authStatus.textContent = "Could not reach the server. Please try again.";
            } finally {
                authSubmit.disabled = false;
            }
        });

        authDialog.addEventListener("click", (event) => {
            if (event.target !== authDialog) {
                return;
            }

            const bounds = authDialog.getBoundingClientRect();
            const clickedOutside = event.clientX < bounds.left || event.clientX > bounds.right ||
                event.clientY < bounds.top || event.clientY > bounds.bottom;
            if (clickedOutside) {
                authDialog.close();
            }
        });

        checkSession();

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
                    requestReply(prompt, true);
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

        async function requestReply(message, generateSheet = false) {
            messageInput.disabled = true;
            sendButton.disabled = true;

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message, generate_sheet: generateSheet })
                });
                const contentType = response.headers.get("content-type") || "";
                if (!contentType.includes("application/json")) {
                    throw new Error(`The chat API returned a web page (HTTP ${response.status}) instead of JSON. Open this app at http://127.0.0.1:5000/ to use the Flask API.`);
                }
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Request failed.");
                }

                addMessage(data.reply || "Gemini returned an empty response.", "bot", data.pdf_url);
            } catch (error) {
                addMessage(`Could not get a reply: ${error.message}`, "bot");
            } finally {
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.placeholder = "Type your message...";
                messageInput.focus();
            }
        }


        function addMessage(text, sender, pdfUrl = null) {
            const row = document.createElement("div");
            row.classList.add("message-row", sender);

            const message = document.createElement("div");
            message.classList.add("message");

            if (sender === "bot") {
                const content = document.createElement("div");
                content.classList.add("message-content");
                renderMarkdown(content, text);
                message.appendChild(content);

                if (pdfUrl) {
                    const sheetUrl = new URL(pdfUrl, window.location.origin);
                    if (sheetUrl.origin === window.location.origin && sheetUrl.pathname.startsWith("/api/characters/")) {
                        message.classList.add("has-character-sheet");

                        const preview = document.createElement("iframe");
                        preview.className = "character-sheet-preview";
                        preview.title = "Generated D&D character sheet PDF";
                        preview.loading = "lazy";
                        preview.src = sheetUrl.href;
                        message.appendChild(preview);

                        const downloadLink = document.createElement("a");
                        downloadLink.className = "character-sheet-download";
                        downloadLink.href = sheetUrl.href;
                        downloadLink.target = "_blank";
                        downloadLink.rel = "noopener noreferrer";
                        downloadLink.textContent = "Open or download character sheet PDF";
                        message.appendChild(downloadLink);
                    }
                }
            } else {
                message.textContent = text;
            }

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

        function renderMarkdown(container, text) {
            const lines = text.replace(/\r\n?/g, "\n").split("\n");
            let index = 0;

            while (index < lines.length) {
                const line = lines[index].trim();
                if (!line) {
                    index += 1;
                    continue;
                }

                if (/^(?:-{3,}|\*{3,}|_{3,})$/.test(line)) {
                    container.appendChild(document.createElement("hr"));
                    index += 1;
                    continue;
                }

                const heading = line.match(/^(#{1,6})\s+(.+)$/);
                if (heading) {
                    const element = document.createElement(`h${Math.min(heading[1].length + 1, 6)}`);
                    appendInlineMarkdown(element, heading[2]);
                    container.appendChild(element);
                    index += 1;
                    continue;
                }

                if (index + 1 < lines.length && line.includes("|") && isTableSeparator(lines[index + 1])) {
                    const table = document.createElement("table");
                    const headerCells = splitTableRow(line);
                    const alignments = splitTableRow(lines[index + 1]).map(getTableAlignment);
                    const head = document.createElement("thead");
                    const headerRow = document.createElement("tr");
                    headerCells.forEach((cell, cellIndex) => {
                        const element = document.createElement("th");
                        setTableAlignment(element, alignments[cellIndex]);
                        appendInlineMarkdown(element, cell);
                        headerRow.appendChild(element);
                    });
                    head.appendChild(headerRow);
                    table.appendChild(head);

                    const body = document.createElement("tbody");
                    index += 2;
                    while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
                        const cells = splitTableRow(lines[index]);
                        const row = document.createElement("tr");
                        headerCells.forEach((_, cellIndex) => {
                            const element = document.createElement("td");
                            setTableAlignment(element, alignments[cellIndex]);
                            appendInlineMarkdown(element, cells[cellIndex] || "");
                            row.appendChild(element);
                        });
                        body.appendChild(row);
                        index += 1;
                    }
                    table.appendChild(body);
                    container.appendChild(table);
                    continue;
                }

                const orderedItem = line.match(/^\d+[.)]\s+(.+)$/);
                const unorderedItem = line.match(/^[-*+]\s+(.+)$/);
                if (orderedItem || unorderedItem) {
                    const ordered = Boolean(orderedItem);
                    const list = document.createElement(ordered ? "ol" : "ul");
                    while (index < lines.length) {
                        const currentLine = lines[index].trim();
                        const item = ordered
                            ? currentLine.match(/^\d+[.)]\s+(.+)$/)
                            : currentLine.match(/^[-*+]\s+(.+)$/);
                        if (!item) {
                            break;
                        }
                        const element = document.createElement("li");
                        appendInlineMarkdown(element, item[1]);
                        list.appendChild(element);
                        index += 1;
                    }
                    container.appendChild(list);
                    continue;
                }

                const paragraph = document.createElement("p");
                const paragraphLines = [];
                while (index < lines.length && lines[index].trim()) {
                    const currentLine = lines[index].trim();
                    if (/^(?:-{3,}|\*{3,}|_{3,})$/.test(currentLine)
                        || /^#{1,6}\s+/.test(currentLine)
                        || /^[-*+]\s+/.test(currentLine)
                        || /^\d+[.)]\s+/.test(currentLine)
                        || (index + 1 < lines.length && currentLine.includes("|") && isTableSeparator(lines[index + 1]))) {
                        break;
                    }
                    paragraphLines.push(currentLine);
                    index += 1;
                }
                appendInlineMarkdown(paragraph, paragraphLines.join(" "));
                container.appendChild(paragraph);
            }
        }

        function splitTableRow(line) {
            return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
        }

        function isTableSeparator(line) {
            const cells = splitTableRow(line);
            return cells.length > 1 && cells.every((cell) => /^:?-{3,}:?$/.test(cell));
        }

        function getTableAlignment(separator) {
            const left = separator.startsWith(":");
            const right = separator.endsWith(":");
            return left && right ? "center" : right ? "right" : left ? "left" : "";
        }

        function setTableAlignment(cell, alignment) {
            if (alignment) {
                cell.style.textAlign = alignment;
            }
        }

        function appendInlineMarkdown(container, text) {
            const tokenPattern = /(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|\*[^*\s][^*]*\*|_[^_\s][^_]*_)/g;
            let lastIndex = 0;

            for (const match of text.matchAll(tokenPattern)) {
                container.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
                const token = match[0];
                const isBold = token.startsWith("**") || token.startsWith("__");
                const isCode = token.startsWith("`");
                const markerLength = isBold ? 2 : 1;
                const element = document.createElement(isBold ? "strong" : isCode ? "code" : "em");
                element.textContent = token.slice(markerLength, -markerLength);
                container.appendChild(element);
                lastIndex = match.index + token.length;
            }

            container.appendChild(document.createTextNode(text.slice(lastIndex)));
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