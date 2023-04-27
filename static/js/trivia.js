const trivia = [
    {
        question: "Question 1 Which cocktail is known as the King of Cocktails?",
        answers: ["Answer 1A: Mojito", "Answer 1B: Martini", "Answer 1C: Old Fashioned", "Answer 1D: Margarita"],
        correctAnswer: 1,
    },
    {
        question: "Question 2 What is the main ingredient in a Piña Colada?",
        answers: ["Answer 2A Tequila", "Answer 2B Rum", "Answer 2C Vodka", "Answer 2D Gin"],
        correctAnswer: 1,
    },
    {
        question: "Question 3 What is the main alcohol in a traditional Moscow Mule?",
        answers: ["Answer 3A Vodka", "Answer 3B Whiskey", "Answer 3C Rum", "Answer 3D Tequila"],
        correctAnswer: 0,
    },
    {
        question: "Question 4 Which cocktail is traditionally garnished with a maraschino cherry and an orange slice?",
        answers: ["Answer 4A Mojito", "Answer 4B Margarita", "Answer 4C Old Fashioned", "Answer 4D Cosmopolitan"],
        correctAnswer: 2,
    },
    {
        question: "Question 5 In which country was the Margarita cocktail invented?",
        answers: ["Answer 5A Mexico", "Answer 5B United States", "Answer 5C Spain", "Answer 5D Cuba"],
        correctAnswer: 0,
    },
    // Add more trivia questions here
];

let currentQuestion = 0;

function showQuestion() {
    const question = trivia[currentQuestion];
    const triviaDiv = document.getElementById("trivia");

    triviaDiv.innerHTML = `
        <div class="question">${question.question}</div>
        <ul class="answers">
            ${question.answers
                .map(
                    (answer, index) =>
                        `<li data-answer="${index}">${answer}</li>`
                )
                .join("")}
        </ul>
    `;

    const answers = document.querySelectorAll(".answers li");
    answers.forEach((answer) => {
        answer.addEventListener("click", (event) => {
            const selectedIndex = parseInt(event.target.dataset.answer);
            if (selectedIndex === question.correctAnswer) {
                alert("Correct!");
            } else {
                alert(`Incorrect! The correct answer is: ${question.answers[question.correctAnswer]}`);
            }

            currentQuestion++;
            if (currentQuestion < trivia.length) {
                showQuestion();
            } else {
                triviaDiv.innerHTML = `<h2>Trivia complete!</h2>`;
            }
        });
    });
}

document.getElementById("next-question").addEventListener("click", showQuestion);
showQuestion();
