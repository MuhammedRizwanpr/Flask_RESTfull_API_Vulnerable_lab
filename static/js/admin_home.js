function showEditUser(id, username, email, bio){

    document.getElementById("form-area").innerHTML = `

        <div class="edit-form">

        <h2>Edit User</h2>

        <label>Username</label>
        <input
            id="editUsername"
            class="edit-input"
            type="text"
            value="${username}">

        <label>Email</label>
        <input
            id="editEmail"
            class="edit-input"
            type="email"
            value="${email}">
        
        <label>Password</label>
        <input
            id="editPassword"
            class="edit-input"
            type="password"
            placeholder="New Password">

        <label>Bio</label>
        <textarea
            id="editBio"
            class="edit-textarea">${bio}</textarea>

        <button
            class="update-btn"
            onclick="editUser(${id})">

            Update User

        </button>

        </div>

    `;
}

async function editUser(id){

    const username = document.getElementById("editUsername").value;
    const email = document.getElementById("editEmail").value;
    const password = document.getElementById("editPassword").value;
    const bio = document.getElementById("editBio").value;

    const response = await fetch(`/api/user/${id}`, {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username,
            email,
            password,
            bio
        })

    });

    const data = await response.json();

    alert(data.message);

    loadUsers();
}

async function deleteUser(id){

    if(confirm("Are sure to delete this users account? ")){
        const response = await fetch(`/api/user/${id}`,{
            method: "DELETE"
        })
        const data = await response.json()

        alert(data.message);
        loadUsers()
    }

}

window.onload = loadUsers;

async function loadUsers(){

    const response = await fetch("/api/users");

    const users = await response.json();

    const table = document.getElementById("usersTable");

    table.innerHTML = "";

    users.forEach(user => {

        table.innerHTML += `
            <tr>

                <td>${user.username}</td>

                <td>${user.email}</td>

                <td>${user.bio}</td>

                <td>

                   <button onclick="showEditUser(
                        ${user.id},
                        '${user.username}',
                        '${user.email}',
                        '${user.bio}'
                    )">
                        Edit
                    </button>

                    <button onclick="deleteUser(${user.id})">
                        Delete
                    </button>

                </td>

            </tr>
        `;

    });

}
