document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('upload-form');
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');
  const progressContainer = document.getElementById('progress-container');
  const downloadLink = document.getElementById('download-link');
  const downloadButton = document.getElementById('download-button');

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      const percent = (event.loaded / event.total) * 100;
      progressBar.style.width = percent + '%';
      progressText.textContent = percent.toFixed(1) + '%';
    });

    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4 && xhr.status === 200) {
        // Handle the response, e.g., display a success message
        console.log('Upload successful');
        // Show the download link
        downloadLink.style.display = 'block';

        const responseObj = JSON.parse(xhr.responseText);
        // Modify the download link URL to point to the uploaded file
        downloadButton.href = `/download/${responseObj.filename}`;
      }
    };

    xhr.open('POST', form.action, true);
    xhr.send(formData);

    // Hide the form and display the progress bar
    form.style.display = 'none';
    progressContainer.style.display = 'block';
  });
});
