// Function to capture Navigation Bar items, Page Headings, and Form Labels
function getNavAndHeadingCriteria() {
  let extractedText = [];

  // 1. Grab Navigation Links / Menu Items
  document.querySelectorAll('nav a, header a, .menu a, ul.navbar a, [role="navigation"] a').forEach(el => {
    let text = el.innerText.trim();
    if (text && !extractedText.includes(text)) {
      extractedText.push(text);
    }
  });

  // 2. Grab Form Labels and Section Headings
  document.querySelectorAll('h1, h2, h3, label, legend').forEach(el => {
    let text = el.innerText.trim();
    if (text && !extractedText.includes(text)) {
      extractedText.push(text);
    }
  });

  // Join items with periods to create natural pauses during speech synthesis
  return extractedText.join(". ");
}

// Event listener: Triggers when the user clicks on the webpage
document.addEventListener('click', (event) => {
  // Check the extension storage to verify if audio is enabled
  chrome.storage.sync.get(['audioEnabled'], (result) => {
    // If explicitly toggled off, exit without making API calls
    if (result.audioEnabled === false) return;

    const pageText = getNavAndHeadingCriteria();
    if (!pageText) return;

    // Send extracted labels to the Python Flask backend
    fetch('http://localhost:5000/read-form', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({
        text: pageText,
        language: 'kn-IN',
        audio_enabled: true
      })
    })
    .then(response => response.json())
    .then(data => console.log('Server response:', data))
    .catch(error => console.error('Error connecting to backend:', error));
  });
});