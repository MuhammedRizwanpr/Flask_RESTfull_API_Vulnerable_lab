async function login_validate() {

    const username =
    document.getElementById("username").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch("/api/login",{
        method:"POST",

        headers: {
            "Content-Type": "application/json"
        },
        credentials: "same-origin", 
        body: JSON.stringify({

            username,
            password,
        
        })

    });
    const data = await response.json()

    if(response.ok){
        window.location.href="/";
    }
    else{
        alert(data.message);
    }

}

