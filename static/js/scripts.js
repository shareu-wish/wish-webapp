function showContent(contentId) {
    const contents = document.querySelectorAll('.content');
    const buttons = document.querySelectorAll('.buttons button');

    contents.forEach(content => {
        content.classList.remove('active');
    });

    buttons.forEach(button => {
        button.classList.remove('active');
    });

    document.getElementById(contentId).classList.add('active');
    document.getElementById('btn-' + contentId).classList.add('active');
}

// Show the first content by default
document.addEventListener('DOMContentLoaded', () => {
    showContent('content1');
});
