function sendMessage() {
    const input = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const message = input.value;
    input.value = ''; // Clear input after sending

    if (message) {
        // Display the user's message
        chatBox.innerHTML += `<div>User: ${message}</div>`;

        // Send the message to Flask with credentials included
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message }),
            credentials: 'include' // Include cookies with the request
        })
        .then(response => response.json())
        .then(data => {
            // Display the bot's response
            chatBox.innerHTML += `<div>Bot: ${data.answer}</div>`;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}


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