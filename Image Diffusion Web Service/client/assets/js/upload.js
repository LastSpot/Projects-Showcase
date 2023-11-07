document.addEventListener("DOMContentLoaded", function() {
    // Get the upload button element
    const uploadBtn = document.getElementById("upload-btn");
    // font-end validation



    function validateForm(formData, requires) {
      for (const [key, value] of Object.entries(formData)) {
        if (requires.includes(key) && (value == null || value.trim() === "")) {
          alert(`Please fill the ${key} field.`);
          return false;
        }
      }
      return true;
    }

    // Add an event listener for the click event
    uploadBtn.addEventListener("click", async function() {

      const requires = ['name', "type", "tags","pictureLink", "fineTuneMethod", "baseModel", "downloadLink", "secret"];

      // Get the form data
      const formData = {
        'name': document.getElementById("name").value,
        'description': document.getElementById("description").value,
        'type': document.getElementById("type").value,
        'tags': document.getElementById("tags").value,
        'downloadLink': document.getElementById("download-link").value,
        'pictureLink': document.getElementById("picture-link").value,
        'fineTuneMethod': document.getElementById("fine-tuning-method").value,
        'baseModel': document.getElementById("base-model").value,
        'secret': document.getElementById("secret").value,
        'license': 'none'
      };
      

      console.log('is here');
      if (!validateForm(formData, requires)) return;
      try {
        // Send the POST request to the /api/createModel endpoint
        const response = await fetch("/api/createModel", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
          },
            body: JSON.stringify(formData),
        });
  
        // Check if the response is successful
        if (response.ok) {
            const jsonResponse = await response.json();
            console.log('Success:', jsonResponse);
            alert(jsonResponse.data.message);
        } else {
          const jsonResponse = await response.json();
          console.warn("Fail creating model:", jsonResponse.data.message);
          
          let errMsg = '';
          if(jsonResponse.data && Array.isArray(jsonResponse.data.message)) {
            jsonResponse.data.message.forEach(error => {
              errMsg += `${error.path}: ${error.msg}\n`;
            });
          } else {
            errMsg = jsonResponse.data.message;
          }
  
          alert(errMsg);
        }
      } catch (error) {
            console.error("Error creating model:", error);
      }
    });
  });