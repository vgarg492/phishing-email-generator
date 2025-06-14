function sendPrompt() {
  const prompt = document.getElementById("prompt").value;
  const aggressionLevel = document.getElementById('aggressionRange').value;
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
    body: JSON.stringify({ prompt: prompt, aggression: aggressionLevel })
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
      // Show the typology box
      document.getElementById('typology-info').style.display = 'block';
      
      // Populate typology list
      const typologyList = document.getElementById('typologyList');
      typologyList.innerHTML = ''; // Clear existing typologies
      data.typologies.forEach(typology => {
        const li = document.createElement('li');
        li.textContent = typology;
        typologyList.appendChild(li);
      });
    } else {
      // Hide the typology box if no typologies were detected
      document.getElementById('typology-info').style.display = 'none';
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

