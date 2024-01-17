const ip_addr_div = document.getElementById("ip-addr");
var socket = io();
var user_authenticated = false;

const edit_addr = (addr_info) => {
    return () => {
        const name = document.createElement("input");
        name.placeholder = "DEVICE NAME";
        if ("device_name" in addr_info) {
            name.value = addr_info["device_name"]; // user's table so there is a name
        }

        const addr = document.createElement("input");
        addr.placeholder = "ADDRESS";
        addr.value = addr_info["address"];

        const save = document.createElement("img");
        save.src = "/static/share.svg";
        save.alt = "save";
        save.onclick = function () {
            socket.emit("save", {name: name.value, addr: addr.value})
        }
        save.onmouseover = function () {
            save.src = "/static/share_hovered.svg";
        }
        save.onmouseleave = function () {
            save.src = "/static/share.svg";
        }

        ip_addr_div.replaceChildren(name, addr, save);
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

    edit.onclick = edit_addr(addr_info);

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


// fill the given address table with the given address data.
const fill_addr_table = (table, tr_cls, data) => {
    table.replaceChildren(...data.map(addr_info => {
        const row = document.createElement("tr")
        row.classList.add(tr_cls)

        if ("device_name" in addr_info) {
            const cell = document.createElement("th");
            cell.textContent = addr_info["device_name"];
            row.appendChild(cell);
            // todo: navigator.clipboard.writeText(copyText.value);
        }

        if ("address" in addr_info) {
            const cell = document.createElement("th");
            cell.textContent = addr_info["address"];
            row.appendChild(cell);
            // todo: navigator.clipboard.writeText(copyText.value);
        }

        if ("last_updated" in addr_info) {
            const cell = document.createElement("th");
            cell.textContent = addr_info["last_updated"];
            row.appendChild(cell);
            // todo: show date on hover
        }

        if (user_authenticated) {
            const cell = document.createElement("th");
            cell.appendChild(edit_button(addr_info));
            row.appendChild(cell);
        }

        if (tr_cls === "user_tr") {  // delete button only for deletable
            const cell = document.createElement("th");
            cell.appendChild(delete_button(addr_info));
            row.appendChild(cell);
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

const addr_button = document.querySelector("#ip-addr > a");
addr_button.onclick = function () {
    if (user_authenticated) {
        socket.emit('now');
    } else if (confirm("Publicly Share IP-Address?")) {
        socket.emit('now');
    }
}
