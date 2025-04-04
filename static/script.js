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

  document.getElementById("uploaded-file-name").textContent = file.name;
  document.getElementById("file-name").classList.remove("hidden");

  document.querySelector(".upload-button").classList.add("hidden");
}



// Summarize the text
async function summarizeText() {
  let formData = new FormData();

  const fileInput = document.getElementById("file-upload");
  const file = fileInput.files[0];

  const textContent = document.getElementById("text-content").value.trim();

  // Priority: If a file is uploaded, use that. Otherwise, fall back to text input.
  if (file) {
    formData.append("file", file);
    let documentTitle = file.name.split('.')[0]
    document.getElementById("doc-title").textContent = documentTitle;
  } else if (textContent) {
    let words = textContent.split(/\s+/);
    let documentTitle = words.slice(0, 3).join(" ");
    
    // If there are more than 3 words, add "..."
    if (words.length > 3) {
      documentTitle += " ...";
    }
    document.getElementById("doc-title").textContent = documentTitle;

    formData.append("text", textContent);
  } else {
    alert("Please enter text or upload a document first.");
    return;
  }

  setLoading(true);

  try {
    // Get the selected options
    const summaryType = document.getElementById("summary-type").value;
    const summaryLength = document.getElementById("summary-length").value;

    // Append settings to FormData
    formData.append("type", summaryType);
    formData.append("length", summaryLength);

    // Send the data to Python backend
    const response = await fetch("http://127.0.0.1:5000/summarize", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.summary) {
      document.getElementById("summary-content").textContent = data.summary;
      document.getElementById("summary-result").classList.remove("hidden");
      document.getElementById("summary-result").scrollIntoView({ behavior: "smooth" });
    } else {
      alert("No summary returned from the server.");
    }
  } catch (error) {
    console.error("Error summarizing:", error);
    alert("An error occurred while summarizing. Please try again.");
  } finally {
    setLoading(false);
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