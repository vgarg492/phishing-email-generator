window.onload = function() {
  loadEmails();
}

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
  const generateButton = document.getElementById('generate-button');
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
    //document.getElementById('aggressionLevel').textContent = data.aggression;
    loadEmailToEditor(data);
    requestAnimationFrame(() => {
      loadEmails();
    });
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


function increasePromptTextarea() {
  const promptTextarea = document.getElementById('prompt');
  promptTextarea.style.height = 'auto';
  promptTextarea.style.height = promptTextarea.scrollHeight + 'px';
}



// Function to fetch and display emails from database
function loadEmails() {
  fetch("/get_emails", {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || "Failed to fetch emails");
      });
    }
    return response.json();
  })
  .then(data => {
    displayEmails(data.emails);
  })
  .catch(error => {
    console.error("Error loading emails:", error);
    alert("Failed to load emails: " + error.message);
  });
}

// Function to display emails in the UI
function displayEmails(emails) {
  // You can customize this to display emails however you want
  console.log("Loaded emails:", emails);
  
  // Example: Display in a list or table
  const emailList = document.getElementById('email-list');
  
  emailList.innerHTML = ''; // Clear existing content
  
  if (emails.length === 0) {
    emailList.innerHTML = '<p>No emails found in database.</p>';
    return;
  }
  
  emails.reverse().forEach(email => {
    // Create a new button for each email
    const emailButton = document.createElement('button');
    emailButton.id = `email-${email.id}`;
    emailButton.textContent = email.subject;
    emailButton.onclick = () => loadEmail(email.id);
    emailButton.className = 'email-item';
    emailList.prepend(emailButton);
  });
}

function loadEmail(emailId){
  fetch(`/get_email/${emailId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json"
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.error || "Failed to fetch email");
      });
    }
    return response.json();
  })
  .then(data => {
    loadEmailToEditor(data.email);
  })
  .catch(error => {
    console.error("Error loading email:", error);
    alert("Failed to load email: " + error.message);
  });
}

function loadEmailToEditor(data){
  document.querySelector('.compose-editor').value = data.content;
  document.querySelector('.field-row .field-input[type="email"]').value = data.to;
  document.querySelector('.subject-row .field-input').value = data.subject;
  document.querySelector('.compose-title').textContent = data.subject;
  document.getElementById('prompt').value = data.prompt;
  // Display typologies if any were detected
  if (data.typologies && data.typologies !== '[]') {
    try {
      // Handle both array and string formats
      let typologies = data.typologies;
      if (typeof typologies === 'string') {
        // Parse string format like "['typology1', 'typology2']"
        typologies = JSON.parse(typologies.replace(/'/g, '"'));
      }
      
      if (typologies && typologies.length > 0) {
        // Show the typology box
        document.getElementById('typology-info').style.display = 'block';
        
        // Populate typology list
        const typologyList = document.getElementById('typologyList');
        typologyList.innerHTML = ''; // Clear existing typologies
        typologies.forEach(typology => {
          const li = document.createElement('li');
          li.textContent = typology;
          typologyList.appendChild(li);
        });
      } else {
        document.getElementById('typology-info').style.display = 'none';
      }
    } catch (e) {
      console.error("Error parsing typologies:", e);
      document.getElementById('typology-info').style.display = 'none';
    }
  } else {
    // Hide the typology box if no typologies were detected
    document.getElementById('typology-info').style.display = 'none';
  }
  document.getElementById('aggressionRange').value = data.aggression;
}
