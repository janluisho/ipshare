const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const numbers = "1234567890";

let letters_interval = null;
let numbers_interval = null;

document.querySelectorAll('.letters').forEach(function (element) {
    element.onmouseover = event => {
        let iteration = 0;

        clearInterval(letters_interval);

        letters_interval = setInterval(() => {
            event.target.innerText = event.target.innerText
                .split("")
                .map((letter, index) => {
                    if(index < iteration) {
                        return event.target.dataset.value[index];
                    }

                    return letters[Math.floor(Math.random() * letters.length)]
                })
                .join("");

            if(iteration >= event.target.dataset.value.length){
                clearInterval(letters_interval);
            }

            iteration += 1 / 3;
        }, 18);
    }
})

document.querySelectorAll('.numbers').forEach(function (element) {
    element.onmouseover = event => {
      let iteration = 0;

      clearInterval(numbers_interval);

      numbers_interval = setInterval(() => {
        event.target.innerText = event.target.innerText
          .split("")
          .map((letter, index) => {
            if(index < iteration) {
              return event.target.dataset.value[index];
            }

            return numbers[Math.floor(Math.random() * numbers.length)]
          })
          .join("");

        if(iteration >= event.target.dataset.value.length){
          clearInterval(numbers_interval);
        }

        iteration += 1 / 3;
      }, 18);
    }
})
