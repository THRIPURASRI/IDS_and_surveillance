document.addEventListener("DOMContentLoaded", function(){
    const liveVideo = document.getElementById('liveVideo');
    const frameCanvas = document.getElementById('frameCanvas');
    const intrusionCountDisplay = document.getElementById('intrusionCount');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => { liveVideo.srcObject = stream; })
        .catch(err => { console.error("Error accessing webcam:", err); });

    let intrusionCount = 0;

    setInterval(function(){
        const context = frameCanvas.getContext('2d');
        context.drawImage(liveVideo, 0, 0, frameCanvas.width, frameCanvas.height);
        const frameData = frameCanvas.toDataURL('image/jpeg');

        fetch('/process_frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frame: frameData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.intrusion) {
                intrusionCount++;
                intrusionCountDisplay.textContent = intrusionCount;
            }
        })
        .catch(error => { console.error("Error processing frame:", error); });
    }, 2000);
});
