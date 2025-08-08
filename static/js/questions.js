document.addEventListener('DOMContentLoaded', function() {
    const filters = document.querySelectorAll('.difficulty-filter');
    const questions = document.querySelectorAll('.question-item');

    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            const difficulty = this.dataset.difficulty;
            
            filters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');

            questions.forEach(question => {
                if (difficulty === 'all' || question.dataset.difficulty === difficulty) {
                    question.style.display = 'block';
                } else {
                    question.style.display = 'none';
                }
            });
        });
    });
});
