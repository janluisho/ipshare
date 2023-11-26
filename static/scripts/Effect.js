const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const numbers = "1234567890";

document.querySelectorAll('[data-letters], [data-numbers]').forEach(function (element) {
    element.inverval = null;

    element.onmouseover = event => {
        element.iteration = 0;
        clearInterval(element.inverval);

        element.inverval = setInterval(() => {
            let data;
            let chars;
            if (Object.hasOwn(event.target.dataset, 'letters')) {
                data = event.target.dataset.letters;
                chars = letters;
            } else {
                data = event.target.dataset.numbers;
                chars = numbers;
            }

            event.target.innerText = event.target.innerText
                .split("")
                .map((letter, index) => {
                    if(index < element.iteration) {
                        return data[index]
                    } else {
                        return chars[Math.floor(Math.random() * chars.length)]
                    }
                })
                .join("");

            if(element.iteration >= data.length){
                clearInterval(element.inverval);
            }

            element.iteration += 1 / 3;
        }, 18);
    }
})