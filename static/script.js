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
  fetch("/generate_email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ prompt: prompt })
  })
  .then(response => response.json())
  .then(data => {
    document.querySelector('.compose-editor').value = data.content;
    document.querySelector('.field-row .field-input[type="email"]').value = data.to;
    document.querySelector('.subject-row .field-input').value = data.subject;
    document.querySelector('.compose-title').textContent = data.subject;
  });
}

