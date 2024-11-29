document.getElementById("appointment-btn").onclick = function() {
    document.getElementById("modal").style.display = "flex";
  }
  
  // Close the modal when the close button is clicked
  function closeModal() {
    document.getElementById("modal").style.display = "none";
  }
  
  // Close the modal when clicking outside of the modal content
  window.onclick = function(event) {
    const modal = document.getElementById("modal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  }
  