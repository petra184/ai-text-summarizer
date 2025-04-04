// Global variables
let activeTab = "text"
let uploadedFileName = ""

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  // Set default values
  const summaryLengthSelect = document.getElementById("summary-length");
  const summaryTypeSelect = document.getElementById("summary-type");
  
  if (summaryLengthSelect) {
    summaryLengthSelect.value = "medium";
  }
  
  if (summaryTypeSelect) {
    summaryTypeSelect.value = "extractive";
  }
})

// Switch between tabs
function switchTab(tab) {
  activeTab = tab

  // Update tab styling
  document.querySelectorAll(".tab").forEach((tabElement) => {
    tabElement.classList.remove("active")
  })
  document.getElementById(`${tab}-tab`).classList.add("active")

  // Show/hide content areas
  document.querySelectorAll(".input-area").forEach((area) => {
    area.classList.add("hidden")
  })
  document.getElementById(`${tab}-input`).classList.remove("hidden")
}

// Handle file upload
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  uploadedFileName = file.name;

  // Show the file name
  document.getElementById("uploaded-file-name").textContent = uploadedFileName;
  document.getElementById("file-name").classList.remove("hidden");

  // Hide the "Choose a file" button
  document.querySelector(".upload-button").classList.add("hidden");

  console.log(`File uploaded: ${uploadedFileName}`);
}



// Summarize the text
async function summarizeText() {
  let textToSummarize = ""

  if (activeTab === "text") {
    textToSummarize = document.getElementById("text-content").value.trim()
  } else {
    textToSummarize = uploadedFileName
  }

  if (!textToSummarize) {
    alert("Please enter text or upload a document first.")
    return
  }

  setLoading(true)

  try {
    // Get the selected options
    const summaryType = document.getElementById("summary-type").value;
    const summaryLength = document.getElementById("summary-length").value;

    // Send the text to Python backend
    const response = await fetch("http://127.0.0.1:5000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        text: textToSummarize,
        type: summaryType,
        length: summaryLength
      })
    })

    const data = await response.json()

    // Display the summary
    document.getElementById("summary-content").textContent = data.summary
    document.getElementById("summary-result").classList.remove("hidden")

    // Scroll to the summary
    document.getElementById("summary-result").scrollIntoView({ behavior: "smooth" })
  } catch (error) {
    console.error("Error summarizing text:", error)
    alert("An error occurred while summarizing the text. Please try again.")
  } finally {
    setLoading(false)
  }
}

// Set loading state
function setLoading(loading) {
  const button = document.getElementById("summarize-button")
  const buttonText = document.getElementById("button-text")
  const buttonIcon = document.getElementById("button-icon")
  const loadingIcon = document.getElementById("loading-icon")

  if (loading) {
    button.disabled = true
    buttonText.textContent = "Summarizing..."
    buttonIcon.classList.add("hidden")
    loadingIcon.classList.remove("hidden")
  } else {
    button.disabled = false
    buttonText.textContent = "Create AI Summary"
    buttonIcon.classList.remove("hidden")
    loadingIcon.classList.add("hidden")
  }
}