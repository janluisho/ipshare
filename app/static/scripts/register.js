const desc_text = document.getElementById("desc_text");
desc_text.dataset.desc = desc_text.innerText

const typewriter_intervall_handler = (target, element, data) => {
    return () => {
        if (target.localName === "input") {
            target.value = data.slice(0, element.iteration);
        } else {
            target.innerText = data.slice(0, element.iteration);
        }

        if (element.iteration >= data.length) {
            clearInterval(element.inverval);
        }

        element.iteration += 1;
    }
};


document.querySelectorAll('#name, #password').forEach(function (element) {
    element.inverval = null;

    element.onfocus = event => {
        desc_text.iteration = 0;
        clearInterval(desc_text.inverval);
        desc_text.inverval = setInterval(typewriter_intervall_handler(
            desc_text, desc_text, event.target.dataset.desc
        ), 20);
    }
    element.onblur = event => {
        desc_text.iteration = 0;
        clearInterval(desc_text.inverval);
        desc_text.inverval = setInterval(typewriter_intervall_handler(
            desc_text, desc_text, desc_text.dataset.desc
        ), 20);
    }
})