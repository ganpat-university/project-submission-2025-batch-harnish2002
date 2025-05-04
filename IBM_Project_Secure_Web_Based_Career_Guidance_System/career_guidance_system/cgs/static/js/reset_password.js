document.getElementById("resetPasswordForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const token = document.getElementById("token").value;
    const new_password = document.getElementById("new_password").value;
    const confirm_password = document.getElementById("confirm_password").value;
    const messageElement = document.getElementById("message");
    messageElement.textContent = "";

    try {
        const response = await fetch("/reset_password/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify({ token, new_password, confirm_password })
        });

        const data = await response.json();

        if (response.ok) {
            messageElement.style.color = "green";
            messageElement.textContent = data.message;
            // Redirect to login after a few seconds
            setTimeout(() => {
                window.location.href = "/login/";
            }, 2000);
        } else {
            messageElement.style.color = "red";
            messageElement.textContent = data.error;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.textContent = "An error occurred. Please try again.";
    }
});