function sendMessage() {
    const input = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const toolUsage = document.getElementById('tool-usage').checked;
    const message = input.value;
    input.value = ''; // Clear input after sending

    if (message) {
        // Display the user's message
        chatBox.innerHTML += `<div class="user-message">User: ${message}</div>`;

        // Send the message to Flask with credentials included
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message, tool_usage: toolUsage }),
            credentials: 'include' // Include cookies with the request
        })
        .then(response => response.json())
        .then(data => {
            if (data.answer) {
                // Display the bot's response
                chatBox.innerHTML += `<div class="bot-message">Bot: ${data.answer}</div>`;
                // Scroll to the bottom
                chatBox.scrollTop = chatBox.scrollHeight;
            } else if (data.error) {
                console.error('Error:', data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

document.getElementById('clear-btn').addEventListener('click', function() {
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: 'clear' }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        // Clear the chat box
        document.getElementById('chat-box').innerHTML = '';
    });
});

document.getElementById('chat-input').addEventListener('keydown', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault(); // Prevents the default action (form submission)
        sendMessage();
    }
});

document.getElementById('change-background').addEventListener('click', function() {
    let currentImage = document.body.style.backgroundImage;
    currentImage = currentImage.replace('url("', '').replace('")', '').split('/').pop();

    // If currentImage is an empty string, set it to the name of the default background image
    if (!currentImage) {
        currentImage = '1.webp'; // Replace with the actual name of your default background image
    }

    fetch('/next_background_image?current_image=' + currentImage)
        .then(response => response.json())
        .then(data => {
            const nextImage = 'assets/backgrounds/' + data.image_name;
            document.body.style.backgroundImage = 'url(' + nextImage + ')';
        });
});

// Request notification permission
document.addEventListener('DOMContentLoaded', function () {
    if (!Notification) {
        alert('Desktop notifications not available in your browser.');
        return;
    }

    if (Notification.permission !== 'granted')
        Notification.requestPermission();
});

// Function to play notification sound
// Function to play a beep sound
function playSound() {
    let context = new (window.AudioContext || window.webkitAudioContext)();
    let oscillator = context.createOscillator();
    let gainNode = context.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(context.destination);

    gainNode.gain.value = 0.1; // volume
    oscillator.frequency.value = 1000; // frequency
    oscillator.type = 'sine'; // type of sound

    oscillator.start(context.currentTime); // play now
    oscillator.stop(context.currentTime + 0.3); // stop playing in 0.3 second
}
// Function to show browser notification
function showNotification(content) {
    if (Notification.permission !== 'granted')
        Notification.requestPermission();
    else {
        let notification = new Notification('New Reminder', {
            body: content,
        });

        notification.onclick = function () {
            window.focus();
        };
    }
}

// Modified fetchPendingMessages function
function fetchPendingMessages() {
    fetch('/get_pending_messages', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.messages && data.messages.length > 0) {
            const chatBox = document.getElementById('chat-box');
            data.messages.forEach(msg => {
                if (msg.role === 'assistant') {
                    chatBox.innerHTML += `<div class="bot-message">Bot: ${msg.content}</div>`;
                    playSound(); // Play notification sound
                    showNotification(msg.content); // Show browser notification
                }
                // You can handle other roles if needed
            });
            // Scroll to the bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    })
    .catch((error) => {
        console.error('Error fetching pending messages:', error);
    });
}

// Start polling every 30 seconds
setInterval(fetchPendingMessages, 30000); // Poll every 30,000 milliseconds (30 seconds)

// Optionally, fetch pending messages when the page loads
window.onload = function() {
    fetchPendingMessages();
};
