document.getElementById("forgotPasswordForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const email = document.getElementById("email").value;
    const messageElement = document.getElementById("message");
    messageElement.textContent = "";

    try {
        const response = await fetch("/forgot_password/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            messageElement.style.color = "green";
            messageElement.textContent = data.message;
        } else {
            messageElement.style.color = "red";
            messageElement.textContent = data.error;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.textContent = "An error occurred. Please try again.";
    }
});