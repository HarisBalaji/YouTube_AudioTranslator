import { useState } from 'react';
import './styles.css';

function App() {
  const languages = {'af': 'Afrikaans', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'bs': 'Bosnian', 'ca': 'Catalan', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French', 'gu': 'Gujarati', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew', 'ja': 'Japanese', 'jw': 'Javanese', 'km': 'Khmer', 'kn': 'Kannada', 'ko': 'Korean', 'la': 'Latin', 'lv': 'Latvian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ms': 'Malay', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'nl': 'Dutch', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'si': 'Sinhala', 'sk': 'Slovak', 'sq': 'Albanian', 'sr': 'Serbian', 'su': 'Sundanese', 'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Mandarin/Taiwan)', 'zh': 'Chinese (Mandarin)'}
  const [targetLang, setTargetLang] = useState('ta');
  const [link, setLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [success, setSuccess] = useState(false);
  const [videoName, setVideoName] = useState('');
  const [progressBar,setProgressBar] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setProgressBar(true);
    setMessage('Processing video...');
    const request = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ link : link, target_lang: targetLang })
    }
    
    try {
      const response =await fetch('/', request);
      console.log(response)
      if (response.ok) {
        setProgressBar(false);
        setSuccess(true);
        setLoading(false);
      }else{
        setProgressBar(false);
        setMessage('Error occured... Please try again.');
        setSuccess(false);
      }
      const data = await response.json();
      setVideoName(data.video_name);
    } catch (error) {
      setSuccess(false);
      setProgressBar(false);
      setMessage('Internal server error... Please try again.');
    }
  };
  const handleViewVideo = () => {
     window.open(`http://127.0.0.1:5000/video/${videoName}`, '_blank');
  };

  return (
    <>
    <h1>YouTube Audio Generator</h1>
    <div className="container">
      <form onSubmit={handleSubmit}>
            {loading && <p>{message}</p>}
            {progressBar && !success && <progress />}
            <label htmlFor="link">Enter the YouTube link:</label>
            <input type="text" id="link" name="link" value={link} onChange={(e) => setLink(e.target.value)} required />
            <br/>
            <label htmlFor="target_lang">Select the target language:</label>
            <select id="target_lang" name="target_lang" value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
              {Object.entries(languages).map(([langCode, langName]) => (
                <option key={langCode} value={langCode}>
                  {langName}
                </option>
              ))}
            </select>
            <br/>
            <button type="submit">Generate Audio</button>
        </form>
        {success && <button onClick={handleViewVideo}>View Video</button>}
    </div>
    </>
  );
}

export default App;
