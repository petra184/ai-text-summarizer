// Global variables
let activeTab = "text"
const uploadedFileName = ""
let urlValidated = false

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  // Set default values
  const summaryLengthSelect = document.getElementById("summary-length")
  const summaryTypeSelect = document.getElementById("summary-type")

  if (summaryLengthSelect) {
    summaryLengthSelect.value = "medium"
  }

  if (summaryTypeSelect) {
    summaryTypeSelect.value = "extractive"
  }

  // Add event listener for URL validation
  const urlValidateButton = document.getElementById("url-validate")
  if (urlValidateButton) {
    urlValidateButton.addEventListener("click", validateUrl)
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
  const file = event.target.files[0]
  if (!file) return

  document.getElementById("uploaded-file-name").textContent = file.name
  document.getElementById("file-name").classList.remove("hidden")

  document.querySelector(".upload-button").classList.add("hidden")
}

// Validate URL
async function validateUrl() {
  const urlInput = document.getElementById("url-content")
  const url = urlInput.value.trim()
  const urlStatus = document.getElementById("url-status")
  const urlStatusText = document.getElementById("url-status-text")
  const validIcon = document.getElementById("url-valid-icon")
  const invalidIcon = document.getElementById("url-invalid-icon")

  // Reset status
  urlStatus.className = "url-status"
  validIcon.classList.add("hidden")
  invalidIcon.classList.add("hidden")
  urlValidated = false

  if (!url) {
    urlStatus.classList.remove("hidden")
    urlStatus.classList.add("invalid")
    invalidIcon.classList.remove("hidden")
    urlStatusText.textContent = "Please enter a URL"
    return
  }

  // Basic URL validation
  try {
    new URL(url)
  } catch (e) {
    urlStatus.classList.remove("hidden")
    urlStatus.classList.add("invalid")
    invalidIcon.classList.remove("hidden")
    urlStatusText.textContent = "Invalid URL format. Please include http:// or https:// at the beginning"
    return
  }

  // Show loading state
  urlStatus.classList.remove("hidden")
  urlStatusText.textContent = "Validating URL..."

  try {
    // Send validation request to backend
    const response = await fetch("http://127.0.0.1:5000/validate-url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    })

    const data = await response.json()

    if (data.valid) {
      urlStatus.classList.add("valid")
      validIcon.classList.remove("hidden")
      urlStatusText.textContent = "URL is valid"
      urlValidated = true
    } else {
      urlStatus.classList.add("invalid")
      invalidIcon.classList.remove("hidden")
      urlStatusText.textContent = data.message || "URL could not be accessed"
    }
  } catch (error) {
    console.error("Error validating URL:", error)
    urlStatus.classList.add("invalid")
    invalidIcon.classList.remove("hidden")
    urlStatusText.textContent = "Error validating URL. Please try again."
  }
}

// Summarize the text
async function summarizeText() {
  const formData = new FormData()

  // Get the selected options
  const summaryType = document.getElementById("summary-type").value
  const summaryLength = document.getElementById("summary-length").value

  // Append settings to FormData
  formData.append("type", summaryType)
  formData.append("length", summaryLength)

  // Handle different input types
  if (activeTab === "pdf") {
    const fileInput = document.getElementById("file-upload")
    const file = fileInput.files[0]

    if (!file) {
      alert("Please upload a document first.")
      return
    }

    formData.append("file", file)
    const documentTitle = file.name.split(".")[0]
    document.getElementById("doc-title").textContent = documentTitle
  } else if (activeTab === "text") {
    const textContent = document.getElementById("text-content").value.trim()

    if (!textContent) {
      alert("Please enter text first.")
      return
    }

    const words = textContent.split(/\s+/)
    let documentTitle = words.slice(0, 2).join(" ")

    // If there are more than 3 words, add "..."
    if (words.length > 2) {
      documentTitle += " ..."
    }
    document.getElementById("doc-title").textContent = documentTitle

    formData.append("text", textContent)
  } else if (activeTab === "url") {
    const urlContent = document.getElementById("url-content").value.trim()

    if (!urlContent) {
      alert("Please enter a URL first.")
      return
    }

    if (!urlValidated) {
      alert("Please validate the URL before summarizing.")
      return
    }

    formData.append("url", urlContent)

    // Extract domain name for the title
    try {
      const urlObj = new URL(urlContent)
      const documentTitle = urlObj.hostname.replace("www.", "")
      document.getElementById("doc-title").textContent = documentTitle
    } catch (e) {
      document.getElementById("doc-title").textContent = "Web Content"
    }
  } else {
    alert("Please select an input method.")
    return
  }

  setLoading(true)

  try {
    // Send the data to Python backend
    const response = await fetch("http://127.0.0.1:5000/summarize", {
      method: "POST",
      body: formData,
    })

    const data = await response.json()

    if (data.summary) {
      document.getElementById("summary-content").textContent = data.summary
      document.getElementById("summary-result").classList.remove("hidden")
      document.getElementById("summary-result").scrollIntoView({ behavior: "smooth" })
    } 
    else {
      alert("No summary returned from the server.")
    }
  } catch (error) {
    console.error("Error summarizing:", error)
    alert("An error occurred while summarizing. Please try again.")
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