document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const statusMessage = document.getElementById('status-message');

    contactForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Getting the values from the form input fields
        const formData = new FormData(contactForm);
        const object = {};
        formData.forEach((value, key) => object[key] = value);
        const json = JSON.stringify(object);

        // Sending the form data as JSON to the back-end
        fetch('http://localhost:5000/send-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: json
        })
        .then(response => response.json())
        .then(data => {
            // Handle response data
            console.log(data);
            // Clear the form
            contactForm.reset();
            // Display a success message to the user
            statusMessage.innerHTML = '<span style="font-weight: bold; font-style: italic;">Email sent successfully!</span>';
        })
        .catch((error) => {
            console.error('Error:', error);
            // Display the error message to the user
            statusMessage.textContent = 'Error sending email. Please try again.';
        });
    });
});
