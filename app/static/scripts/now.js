const desc_heading = document.getElementById("desc_heading");
const desc_text = document.getElementById("desc_text");
desc_text.dataset.desc = desc_text.innerText
desc_heading.dataset.desc = desc_heading.innerText

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


document.querySelectorAll('#risks, #now-container').forEach(function (element) {
    element.inverval = null;

    element.onfocus = event => {
        desc_heading.iteration = 0;
        clearInterval(desc_heading.inverval);
        desc_heading.inverval = setInterval(typewriter_intervall_handler(
            desc_heading, desc_heading, event.target.dataset.heading
        ), 20);

        desc_text.iteration = 0;
        clearInterval(desc_text.inverval);
            desc_text.inverval = setInterval(typewriter_intervall_handler(
                desc_text, desc_text, event.target.dataset.desc
            ), 20);
    }
    element.onblur = event => {
        desc_heading.iteration = 0;
        clearInterval(desc_heading.inverval);
        desc_heading.inverval = setInterval(typewriter_intervall_handler(
            desc_heading, desc_heading, desc_heading.dataset.desc
        ), 20);

        desc_text.iteration = 0;
        desc_text.innerText = "";
        clearInterval(desc_text.inverval);
        desc_text.inverval = setInterval(typewriter_intervall_handler(
            desc_text, desc_text, desc_text.dataset.desc
        ), 20);
    }
})