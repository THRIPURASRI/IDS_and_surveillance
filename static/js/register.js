document.addEventListener("DOMContentLoaded", function(){
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');
    const capturedImageInput = document.getElementById('captured_image');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => { video.srcObject = stream; })
        .catch(err => { console.error("Error accessing webcam:", err); });

    captureButton.addEventListener('click', function(){
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/png');
        capturedImageInput.value = dataURL;
        document.getElementById('preview').src = dataURL;
    });
});
