document.addEventListener("DOMContentLoaded", function() {
    fetch("footer/footer.html")
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.text();
        })
        .then(data => {
            document.getElementById("footer-placeholder").innerHTML = data;
        })
        .catch(error => {
            console.error("Ошибка:", error);
        });
});
