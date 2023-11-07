document.getElementById('registerButton').addEventListener('click', async function () {
    await handleButtonClick('http://localhost:3000/register');
});
  
document.getElementById('loginButton').addEventListener('click', async function () {
    await handleButtonClick('http://localhost:3000/login');
});
  
async function handleButtonClick(apiUrl) {
    // Get the form data
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Prepare the data to send
    const data = {
        username: username,
        password: password
    };

    try {
        const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
        });

        // Handle the response success
        if (response.ok) {
        const jsonResponse = await response.json();
        console.log('Success:', jsonResponse);
        alert(jsonResponse.data.message);
        // Handle the response fail
        } else {
        const jsonResponse = await response.json();
        console.warn('Fail:', jsonResponse);
        alert(jsonResponse.data.message);
        // Handle errors based on the response status
        }
    } catch (error) {
        console.error('Error:', error);
        // Handle errors from the fetch call
    }
}