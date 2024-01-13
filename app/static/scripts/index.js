var socket = io();

// socket.on('connect', function () {
//     socket.emit('my event', {data: 'I\'m connected!'});
// });

// fill the given address table with the given address data.
const fill_addr_table = (table, tr_cls, data) => {
    table.replaceChildren(...data.map(addr_info => {
        const row = document.createElement("tr")
        row.classList.add(tr_cls)

        for (var info of addr_info) {
            const cell = document.createElement("th");
            cell.textContent = info;
            row.appendChild(cell);
        }

        return row
    }))
};


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
    socket.emit('now');
}
