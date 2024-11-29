document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed");

    const calendarDays = document.getElementById("calendar-days");
    const currentMonth = document.getElementById("currentMonth");
    const prevMonthBtn = document.querySelector(".prev-month");
    const nextMonthBtn = document.querySelector(".next-month");

    let date = new Date(); // Initialize with current date

    // Function to render the calendar for the current date
    function renderCalendar() {
        calendarDays.innerHTML = ""; // Clear previous days
        const month = date.getMonth();
        const year = date.getFullYear();
        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Update the displayed month
        currentMonth.textContent = date.toLocaleDateString("en-US", {
            month: "long",
            year: "numeric"
        });

        // Create empty boxes for days before the first day of the month
        for (let i = 0; i < firstDayOfMonth; i++) {
            const emptyDiv = document.createElement("div");
            emptyDiv.classList.add("empty");
            calendarDays.appendChild(emptyDiv);
        }

        // Create day boxes for each day in the current month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayDiv = document.createElement("div");
            dayDiv.classList.add("day");
            dayDiv.textContent = day;

            // Highlight today's date
            if (
                day === new Date().getDate() &&
                month === new Date().getMonth() &&
                year === new Date().getFullYear()
            ) {
                dayDiv.classList.add("today");
            }

            calendarDays.appendChild(dayDiv);
        }
    }

    // Event listeners for navigating months
    prevMonthBtn.addEventListener("click", () => {
        date.setMonth(date.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener("click", () => {
        date.setMonth(date.getMonth() + 1);
        renderCalendar();
    });

    // Initial render
    renderCalendar();

    // Alert timeout logic
    setTimeout(function() {
        console.log("Timeout triggered"); 
        const alerts = document.querySelectorAll('.alert');
        if (alerts.length === 0) {
            console.log("No alerts found");
        }
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => {
                console.log("Removing alert:", alert); 
                alert.remove();
            }, 500); 
        });
    }, 3000); 
});
