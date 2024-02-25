var socket = io();
var user_authenticated = false;

// -----  -----  ----- HOVER AND HINT  -----  -----  -----
const hint = document.getElementById("hint");
hint.parentNode.removeChild(hint);

function hover_and_hint (element, src_over, src_leave, hint_text) {
    element.src = src_leave;
    element.alt = hint_text;

    element.onmouseover = () => {
        element.src = src_over;
        hint.textContent = hint_text;
        hint.style.cssText = "--chars: " + hint_text.length.toString() + "rem;"
        element.style.cssText = "--chars: " + hint_text.length.toString() + "rem; z-index: 3;"
        element.parentNode.appendChild(hint);
    }
    element.onmouseleave = () => {
        element.src = src_leave;
        element.style.cssText = "z-index: 1;"
        hint.parentNode.removeChild(hint);
    }
}

// -----  -----  ----- EDITING  -----  -----  -----
const ip_addr_div = document.getElementById("ip-addr");
const edit_qr_div = document.getElementById("edit-qr");
const main = document.querySelector("main");

const qr_code = document.getElementById("qr");

const token_field = document.getElementById("token");
const token_copy = document.getElementById("copy-token");
hover_and_hint(token_copy, "/static/copy_hovered.svg", "/static/copy.svg", "COPY TOKEN");

const edit_save = document.getElementById("edit-save");
hover_and_hint(edit_save, "/static/share_hovered.svg", "/static/share.svg", "SAVE");
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
socket.on('validated', function (data) {
    hover_and_hint(edit_valid, data["src"], data["src"], data["alt"]);
});

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
            token_field.textContent = text.split(".")[1];
            token_field.onclick = function () {
                navigator.clipboard.writeText(text);
            }
            token_copy.onclick = function () {
                navigator.clipboard.writeText(text);
            }
        })

    qr_code.src = `/qr/` + encodeURI(addr);
}

const edit_address = (edit, addr_info) => {
    return () => {
        if ("name" in addr_info) {
            edit_name.value = addr_info["name"]; // user's table so there is a name
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

const pen_button = (addr_info) => {
    const pen_button = document.createElement("img");
    hover_and_hint(pen_button, "/static/edit_hovered.svg", "/static/edit.svg", "EDIT");
    pen_button.onclick = edit_address(pen_button, addr_info);

    const container = document.createElement("div");
    container.classList.add("img-with-hint-container")
    container.appendChild(pen_button)

    return container
}

const delete_button = (addr_info) => {
    const del = document.createElement("img");
    hover_and_hint(del, "/static/delete_hovered.svg", "/static/delete.svg", "DELETE");
    del.onclick = function () {
        socket.emit("del", {name: addr_info["name"], addr: addr_info["address"]})
    }

    const container = document.createElement("div");
    container.classList.add("img-with-hint-container")
    container.appendChild(del)

    return container
}


// -----  -----  ----- FILLING TABLES VIA SOCKET  -----  -----  -----

// fill the given address table with the given address data.
const fill_addr_table = (table, tr_cls, data) => {
    table.replaceChildren(...data.map(addr_info => {
        const row = document.createElement("tr")
        row.classList.add(tr_cls)

        const name_cell = document.createElement("th");
        if ("name" in addr_info) {
            if ("img" in addr_info) {
                const img = document.createElement("img");
                img.src = addr_info["img"];
                img.classList.add("flag")
                name_cell.appendChild(img);
            } else {
                name_cell.textContent = addr_info["name"];
            }
            name_cell.onclick = () => {
                navigator.clipboard.writeText(addr_info["name"]);
            }
        }
        name_cell.classList.add("name")
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
            edit_cell.appendChild(pen_button(addr_info));
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
