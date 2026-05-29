document.addEventListener('DOMContentLoaded', () => {
    if (typeof wpNativeTTSData === 'undefined' || !('speechSynthesis' in window)) {
        console.warn('WP Native TTS: Web Speech API is not supported in this browser or data is missing.');
        return;
    }

    const playBtns = document.querySelectorAll('.tts-play');
    const pauseBtns = document.querySelectorAll('.tts-pause');
    const stopBtns = document.querySelectorAll('.tts-stop');
    const statusTexts = document.querySelectorAll('.tts-status');

    let chunks = [];
    let currentChunkIndex = 0;
    let isPlaying = false;
    let isPaused = false;
    let synth = window.speechSynthesis;
    let currentUtterance = null;

    // Helper: update UI across all potential player instances on the page
    const updateUI = (state) => {
        playBtns.forEach(btn => btn.style.display = (state === 'playing') ? 'none' : 'inline-flex');
        pauseBtns.forEach(btn => btn.style.display = (state === 'playing') ? 'inline-flex' : 'none');
        stopBtns.forEach(btn => btn.style.display = (state === 'playing' || state === 'paused') ? 'inline-flex' : 'none');

        statusTexts.forEach(text => {
            if (state === 'playing') text.textContent = 'Lecture en cours...';
            else if (state === 'paused') text.textContent = 'En pause';
            else text.textContent = 'Écouter l\'article';
        });
    };

    // Chunking text to avoid API limits (split by punctuation)
    const prepareTextChunks = (text) => {
        // Split by major punctuation marks ensuring we don't break mid-word, or end of string
        const regex = /[^.?!]+(?:[.?!]+|$)/g;
        let matches = text.match(regex);

        if (!matches) {
            // Fallback if no punctuation
            matches = [text];
        }

        return matches.map(chunk => chunk.trim()).filter(chunk => chunk.length > 0);
    };

    const speakNextChunk = () => {
        if (currentChunkIndex >= chunks.length) {
            stopTTS();
            return;
        }

        const textToSpeak = chunks[currentChunkIndex];
        currentUtterance = new SpeechSynthesisUtterance(textToSpeak);

        currentUtterance.lang = wpNativeTTSData.language || 'fr-FR';
        currentUtterance.rate = parseFloat(wpNativeTTSData.rate) || 1;
        currentUtterance.pitch = parseFloat(wpNativeTTSData.pitch) || 1;

        // Try to find the best voice for the language
        const voices = synth.getVoices();
        const langVoice = voices.find(voice => voice.lang.startsWith(wpNativeTTSData.language));
        if (langVoice) {
            currentUtterance.voice = langVoice;
        }

        currentUtterance.onend = () => {
            if (!isPaused && isPlaying) {
                currentChunkIndex++;
                speakNextChunk();
            }
        };

        currentUtterance.onerror = (e) => {
            console.error('WP Native TTS Error:', e);
            stopTTS();
        };

        synth.speak(currentUtterance);
    };

    const playTTS = () => {
        if (isPaused) {
            synth.resume();
            isPaused = false;
            isPlaying = true;
            updateUI('playing');
        } else {
            // First time play
            if (chunks.length === 0) {
                chunks = prepareTextChunks(wpNativeTTSData.text);
            }
            if (chunks.length > 0) {
                synth.cancel(); // Clear any existing queue
                currentChunkIndex = 0;
                isPlaying = true;
                isPaused = false;
                updateUI('playing');
                speakNextChunk();
            }
        }
    };

    const pauseTTS = () => {
        if (isPlaying && !isPaused) {
            synth.pause();
            isPaused = true;
            isPlaying = false;
            updateUI('paused');
        }
    };

    const stopTTS = () => {
        synth.cancel();
        isPlaying = false;
        isPaused = false;
        currentChunkIndex = 0;
        updateUI('stopped');
    };

    // Ensure voices are loaded (some browsers load them asynchronously)
    if (synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = () => synth.getVoices();
    }

    // Attach Event Listeners
    playBtns.forEach(btn => btn.addEventListener('click', playTTS));
    pauseBtns.forEach(btn => btn.addEventListener('click', pauseTTS));
    stopBtns.forEach(btn => btn.addEventListener('click', stopTTS));

    // Stop TTS if user leaves the page
    window.addEventListener('beforeunload', stopTTS);
});
