async function updateProfile() {

    const username = document.getElementById("editUsername").value;
    const email = document.getElementById("editEmail").value;
    const password = document.getElementById("editPassword").value;
    const bio = document.getElementById("editBio").value;

    const response = await fetch("/api/user", {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        credentials: "same-origin",

        body: JSON.stringify({

            username,
            email,
            password,
            bio

        })

    });

    const data = await response.json();

    if(response.ok){

        alert(data.message);

        window.location.href = "/";

    }
    else{

        alert(data.message);

    }

}no