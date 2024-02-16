var socket = io();
var user_authenticated = false;

// -----  -----  ----- EDITING  -----  -----  -----
const ip_addr_div = document.getElementById("ip-addr");
const edit_qr_div = document.getElementById("edit-qr");
const main = document.querySelector("main");

const token_field = document.getElementById("token");
const qr_code = document.getElementById("qr");

const edit_save = document.getElementById("edit-save");
edit_save.onmouseover = () => { edit_save.src = "/static/share_hovered.svg"; }
edit_save.onmouseleave = () => { edit_save.src = "/static/share.svg"; }
edit_save.onclick = () => {
    socket.emit("save", {name: edit_name.value, addr: edit_addr.value});
    update_token_and_qr(edit_addr.value, edit_name.value);
}

const edit_name = document.getElementById("edit-name");
edit_name.onblur = () => {
    socket.emit("save", {name: edit_name.value, addr: edit_addr.value});
    update_token_and_qr(edit_addr.value, edit_name.value);
}

const edit_addr = document.getElementById("edit-addr");
edit_addr.oninput = () => { socket.emit("validate", {addr: edit_addr.value}); }
edit_addr.onblur = () => {
    socket.emit("save", {name: edit_name.value, addr: edit_addr.value});
    update_token_and_qr(edit_addr.value, edit_name.value);
}

const edit_valid = document.getElementById("edit-valid");
socket.on('validated', function (data) {edit_valid.src = data;});

const update_token_and_qr = (addr, name) => {
    const token_url = `/v1/token/` + encodeURI(name);
    fetch(token_url)
        .then(result => {
            if (!result.ok) {
                throw new Error("Couldn't get token.")
            }
            return result.text()
        })
        .then(text => {
            token_field.textContent = "API TOKEN: " + text.slice(0, 8) + "..." + text.slice(-9, -1);
            token_field.onclick = function () {
                navigator.clipboard.writeText(text);
            }
        })

    qr_code.src = `/qr/` + encodeURI(addr);
}

const edit_address = (edit, addr_info) => {
    return () => {
        if ("device_name" in addr_info) {
            edit_name.value = addr_info["device_name"]; // user's table so there is a name
        }

        edit_addr.value = addr_info["address"];
        update_token_and_qr(edit_addr.value, edit_name.value);

        document.documentElement.style.setProperty("--addr-width", "60rem");  // Address Tables on top of each other
        main.removeChild(ip_addr_div);
        main.appendChild(edit_qr_div);

        edit.onclick = function () {
            document.documentElement.style.setProperty("--addr-width", "130rem");  // Address Tables side by side
            main.removeChild(edit_qr_div);
            main.appendChild(ip_addr_div);
            edit.onclick = edit_address(edit, addr_info);
        }
    }
}

const edit_button = (addr_info) => {
    const edit = document.createElement("img");
    edit.src = "/static/edit.svg";
    edit.alt = "edit";
    edit.onmouseover = function () {
        edit.src = "/static/edit_hovered.svg";
    }
    edit.onmouseleave = function () {
        edit.src = "/static/edit.svg";
    }

    edit.onclick = edit_address(edit, addr_info);

    return edit
}

const delete_button = (addr_info) => {
    const del = document.createElement("img");
    del.src = "/static/delete.svg";
    del.alt = "delete";
    del.onmouseover = function () {
        del.src = "/static/delete_hovered.svg";
    }
    del.onmouseleave = function () {
        del.src = "/static/delete.svg";
    }

    del.onclick = function () {
        socket.emit("del", {name: addr_info["device_name"], addr: addr_info["address"]})
    }

    return del
}


// -----  -----  ----- FILLING TABLES VIA SOCKET  -----  -----  -----

// fill the given address table with the given address data.
const fill_addr_table = (table, tr_cls, data) => {
    table.replaceChildren(...data.map(addr_info => {
        const row = document.createElement("tr")
        row.classList.add(tr_cls)

        const name_cell = document.createElement("th");
        if ("device_name" in addr_info) {
            name_cell.textContent = addr_info["device_name"];
            name_cell.onclick = () => {
                navigator.clipboard.writeText(addr_info["device_name"]);
            }
        }
        name_cell.classList.add("device_name")
        row.appendChild(name_cell);


        if ("address" in addr_info) {
            const cell = document.createElement("th");
            cell.classList.add("address")
            cell.textContent = addr_info["address"];
            row.appendChild(cell);
            cell.onclick = () => {
                navigator.clipboard.writeText(addr_info["address"]);
            }
        }

        if ("last_updated" in addr_info) {
            const cell = document.createElement("th");
            cell.textContent = addr_info["last_updated"];
            row.appendChild(cell);
            // todo: show date on hover
        }

        if (user_authenticated) {
            const edit_cell = document.createElement("th");
            edit_cell.appendChild(edit_button(addr_info));
            row.appendChild(edit_cell);

            const delete_cell = document.createElement("th");
            if (tr_cls === "user_tr") {  // delete button only for deletable
                delete_cell.appendChild(delete_button(addr_info));
            }
            row.appendChild(delete_cell);
        }

        return row
    }))
};

socket.on('user authenticated', function () {
    user_authenticated = true;
});

socket.on('user table', function (data) {
    const user_table = document.querySelector("#user_addrs > table");
    fill_addr_table(user_table, "user_tr", JSON.parse(data));
});

socket.on('public table', function (data) {
    const user_table = document.querySelector("#public_addrs > table");
    fill_addr_table(user_table, "public_tr", JSON.parse(data));
});

// -----  -----  ----- IP BUTTON  -----  -----  -----
const addr_button = document.querySelector("#ip-addr > a");
addr_button.onclick = function () {
    if (user_authenticated) {
        socket.emit('now');
    } else if (confirm("Publicly Share IP-Address?")) {
        socket.emit('now');
    }
}

//  -----  -----  ----- Hide edit stuff at start  -----  -----  -----
document.documentElement.style.setProperty("--addr-width", "130rem");  // Address Tables Side by side
main.removeChild(edit_qr_div)
