const recordBtn = document.getElementById('recordBtn');
const statusText = document.getElementById('statusText');
const resultCard = document.getElementById('resultCard');
const resultTitle = document.getElementById('resultTitle');
const resultConfidence = document.getElementById('resultConfidence');
const resultDetails = document.getElementById('resultDetails');

const BACKEND_URL = 'http://localhost:8000';

let mediaRecorder;
let recordedChunks = [];
let recordingTimeout;

function setStatus(message) {
  statusText.textContent = message;
}

function showResult(data) {
  resultCard.style.display = 'block';
  resultCard.classList.remove('sober', 'intoxicated');
  resultCard.classList.add(data.state);

  const title = data.state === 'sober' ? 'Likely Sober' : 'Possible Impairment Detected';
  resultTitle.textContent = title;
  resultConfidence.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
  resultDetails.textContent = `Duration: ${data.details.duration_seconds.toFixed(2)}s`;
}

async function sendAudio(blob) {
  setStatus('Processing...');
  const formData = new FormData();
  formData.append('file', blob, 'recording.webm');

  try {
    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    const data = await response.json();
    showResult(data);
    setStatus('Ready');
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}

function stopRecording() {
  if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
  clearTimeout(recordingTimeout);
  mediaRecorder.stop();
  recordBtn.textContent = 'Start voice check';
  recordBtn.classList.remove('recording');
  setStatus('Uploading...');
}

function startRecording(stream) {
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: 'audio/webm' });
    sendAudio(blob);
  };

  mediaRecorder.start();
  setStatus('Recording...');
  recordBtn.textContent = 'Stop';
  recordBtn.classList.add('recording');

  // Stop after 5 seconds automatically
  recordingTimeout = setTimeout(stopRecording, 5000);
}

recordBtn.addEventListener('click', async () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    stopRecording();
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    startRecording(stream);
  } catch (err) {
    setStatus('Microphone permission is required to record.');
  }
});
