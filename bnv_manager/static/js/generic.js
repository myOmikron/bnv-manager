function generatePassword(id) {
    let pw = Array(32)
        .fill('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@-#$')
        .map(x => x[Math.floor(crypto.getRandomValues(new Uint32Array(1))[0] / (0xffffffff + 1) * x.length)])
        .join('');
    let inputField = document.getElementById(id);
    inputField.setAttribute("type", "");
    inputField.value = pw;
}

function constructUsername(id_username, id_firstname, id_lastname, users) {
    let username = document.getElementById(id_username);
    let firstname = document.getElementById(id_firstname);
    let lastname = document.getElementById(id_lastname);

    let tmp = firstname.value.toLowerCase() + "." + lastname.value.toLowerCase();

    while(users.includes(tmp)) {
        if (tmp.match("\d+$")) {
            let number = Number(tmp.match("\d+$"));
            number += 1;
            tmp.replace("\d+$", String(number))
        } else {
            tmp += "1";
        }
    }
    username.value = tmp;
}

function resetPassword(id_modal, id_form, username) {
    let modal = document.getElementById(id_modal);
    modal.style.display = "block";
    let form = document.getElementById(id_form);
    form.setAttribute("action", "/administration/accounts/resetPassword/" + username);
}

function closeModal(id_modal) {
    let modal = document.getElementById(id_modal);
    modal.style.display = "none";
}