const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const numbers = "1234567890";

const scramble = (data, chars, element) => {
    return (letter, index) => {
        if (index < element.iteration) {
            return data[index]
        } else {
            return chars[Math.floor(Math.random() * chars.length)]
        }
    };
};


const scramble_intervall_handler = (target, element, data, chars) => {
    return () => {
        if (target.localName === "input") {
            target.value = target.value.split("").map(scramble(data, chars, element)).join("");
        } else {
            target.innerText = target.innerText.split("").map(scramble(data, chars, element)).join("");
        }

        if (element.iteration >= data.length) {
            clearInterval(element.inverval);
        }

        element.iteration += 1 / 3;
    }
};


document.querySelectorAll('[data-letters], [data-numbers]').forEach(function (element) {
    element.inverval = null;

    element.onmouseover = event => {
        element.iteration = 0;
        clearInterval(element.inverval);

        let data; // Was am Ende angezeigt wird
        let chars; // Mit welchen zufälligen Zeichen der Effect gemacht werden soll
        if (Object.hasOwn(event.target.dataset, 'letters')) {
            data = event.target.dataset.letters;
            chars = letters;
        } else { // Object.hasOwn(event.target.dataset, 'numbers')
            data = event.target.dataset.numbers;
            chars = numbers;
        }

        element.inverval = setInterval(scramble_intervall_handler(event.target, element, data, chars), 18);
    }
})