function sendPrompt() {
  const prompt = document.getElementById("prompt").value;
  if(prompt.trim() === "") {
    alert("Please enter a prompt.");
    return;
  }
  if(prompt.length > 500) {
    alert("Prompt is too long. Please limit to 500 characters.");
    return;
  }

  // Show loading state
  const generateButton = document.querySelector('button');
  const originalText = generateButton.textContent;
  generateButton.textContent = "Generating...";
  generateButton.disabled = true;

  fetch("/generate_email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ prompt: prompt })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || "Failed to generate email");
      });
    }
    return response.json();
  })
  .then(data => {
    // Update email fields
    document.querySelector('.compose-editor').value = data.content;
    document.querySelector('.field-row .field-input[type="email"]').value = data.to;
    document.querySelector('.subject-row .field-input').value = data.subject;
    document.querySelector('.compose-title').textContent = data.subject;

    // Display typologies if any were detected
    if (data.typologies && data.typologies.length > 0) {
      const typologyDiv = document.createElement('div');
      typologyDiv.className = 'typology-info';
      typologyDiv.innerHTML = `
        <h4>Detected Phishing Typologies:</h4>
        <ul>
          ${data.typologies.map(t => `<li>${t}</li>`).join('')}
        </ul>
      `;
      
      // Remove any existing typology info
      const existingTypology = document.querySelector('.typology-info');
      if (existingTypology) {
        existingTypology.remove();
      }
      
      document.querySelector('.container').appendChild(typologyDiv);
    }
  })
  .catch(error => {
    alert(error.message);
  })
  .finally(() => {
    // Reset button state
    generateButton.textContent = originalText;
    generateButton.disabled = false;
  });
}

function toggleCcBcc() {
  const ccBccFields = document.getElementById('ccBccFields');
  ccBccFields.classList.toggle('active');
}

