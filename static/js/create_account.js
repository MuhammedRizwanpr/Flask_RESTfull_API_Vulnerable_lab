async function validatePassword(){

    const password = document.getElementById("password").value;
    const message = document.getElementById("passwordMessage");

    if(password.length === 0 ){
        message.textContent = "Your password must be (8 character and special symbol @#$% and must include uppercase, lowercase, and numbers)"
    }

    const response = await fetch("/api/validate_password",{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({password: password})
    });

    const data = await response.json();

    if(data.valid){
        message.textContent = "";
        return true;
    }
    else{
        message.textContent = "Your password must be (8 character and special symbol @#$% and must include uppercase, lowercase, and numbers)"
        return false;
    }
}

function confirmPassword(){
    const password1 = document.getElementById("password").value;
    const password2 = document.getElementById("confirm_password").value;
    const message = document.getElementById("check_password");

    if(password1 === password2){
        message.textContent = "";
        return true;
    }
    else{
        message.textContent = "Passwords do not match!";
        return false;
    }
}

async function validateForm(event) {

    event.preventDefault();

    const passwordValid = await validatePassword();

    if (!passwordValid) {
        return;
    }

    const confirmValid = confirmPassword();

    if (!confirmValid) {
        return;
    }

    event.target.submit();
}

function togglePassword() {

    const password = document.getElementById("password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }

}