document.addEventListener('DOMContentLoaded', () => {
    const major_cert_dropdown = document.getElementById('major_cert_dropdown');
    const add_major_cert_button = document.getElementById('add_major_cert_button');
    const liked_courses = document.getElementById('liked_courses');
    const sendButton = document.getElementById('sendButton');
    sendButton.addEventListener('click', () => {
        const inputField = document.querySelector('.chat-input input');
        const message = inputField.value.trim();
        if (message) {
            // Add the message to the chat
            const chatMessages = document.querySelector('.chat-messages');
            const newMessageDiv = document.createElement('div');
            newMessageDiv.textContent = message;
            chatMessages.appendChild(newMessageDiv);

            // Clear the input field
            inputField.value = '';

            // Scroll to the bottom of the chat
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });


    liked_courses.addEventListener('change', function () {
        const selected_course = this.value;

    });
    populate_dropdown();
    add_major_cert_button.addEventListener('click', () => {
        console.log('button clicked');
        add_major_cert(major_cert_dropdown.value);
    });
});


function get_chat_history(course_title) {
    fetch('/get_chat_history/' + course_title)
        .then(response => response.json())
        .then(data => {
            const chatbox = document.querySelector('.chatbox');
            data.forEach(chat => {
                const chat = document.createElement('a');
                chat.classList.add('chat');
                chat.classList.add('incoming');
                chat.innerHTML = `<p>${chat.message}</p>`;
                chatbox.appendChild(chat);
            });
        })
        .catch(error => {
            console.error('Error fetching chat history:', error);
        });
};



function like() {
    const liked_courses = document.getElementById('liked_courses');
    const match_body = document.getElementById('potential_matches_body');
    course_code = match_body.firstChild.textContent;
    match_body.removeChild(match_body.firstChild);
    option = document.createElement('option');
    option.value = course_code;
    option.textContent = course_code;
    liked_courses.appendChild(option);
};

function dislike() {
    const match_body = document.getElementById('potential_matches_body');
    course_code = match_body.firstChild.textContent;
    match_body.removeChild(match_body.firstChild);

    save_dislike(course_code);
};

function save_dislike(course_code) {
    fetch('/save_dislike/' + course_code)
        .then(response => response.json())
        .catch(error => {
            console.error('Error saving dislike:', error);
        });
};

function add_major_cert(major_cert) {
    const filled = document.getElementById('majors_and_certs');
    filled.innerHTML = filled.innerHTML.concat(major_cert);
};

function populate_dropdown() {
    const major_cert_dropdown = document.getElementById('major_cert_dropdown');
    fetch('/get_majors_and_certs/')
        .then(response => response.json())
        .then(data => {
            data.forEach(major => {
                const option = document.createElement('option');
                option.value = major;
                option.textContent = major;
                major_cert_dropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching majors:', error);
        });
}

function get_recommendations() {
    const filepath = document.getElementById('');
    const majors_and_certs = document.getElementById('majors_and_certs');

    const potential_matches_body = document.getElementById('potential_matches_body');
    fetch('/get_recommendations/' + majors_and_certs.innerHTML)
        .then(response => response.json())
        .then(data => add_recommendations(data))
        .catch(error => {
            console.error('Error fetching recommendations:', error);
        });
};

function add_recommendations(data) {
    tableBody = document.getElementById('potential_matches_body');
    data.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${course}</td>`;
        tableBody.appendChild(row);
    });
};

function chat() {
    fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            course_code: liked_courses.value,
            message: document.querySelector('.chat-input input').value
        })
    })
        .then(response => response.json())
        .then(data => {
            const chatbox = document.querySelector('.chatbox');
            const chat = document.createElement('a');
            chat.classList.add('chat');
            chat.classList.add('incoming');
            chat.innerHTML = `<p>${data.message}</p>`;
            chatbox.appendChild(chat);
        })
        .catch(error => {
            F
            console.error('Error sending message:', error);
        });
}