const imag = document.querySelector("#image");
const form = document.querySelector("form");
form.addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(form);
  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });

  const resultDiv = document.getElementById("result");
  const result = await response.json();

  if (result.error) {
    resultDiv.textContent = `Error: ${result.error}`;
  } else {
    // console.log(result);
    console.log(result[1]);

    console.log(result[1].track.share.subject);
    const imaglink = result[1].track.share.image;
    // const url = result[1].track.share.link;
    console.log(imaglink);
    songImage.src = imaglink;
    songImage.style.display = "block";

    const song = document.createElement("p");

    const resdiv = document.getElementById("result");

    song.innerHTML = result[1].track.share.subject;

    const sng = result[1].track.share.subject;

    //   resdiv.append(song_cover)

    resdiv.append(song);

    /*
     * Install the Generative AI SDK
     *
     * $ npm install @google/generative-ai
     */

    const API_KEY = "AIzaSyCFu6BynbPsa-kOupAlLZc21uTXCmaqjik";

    const {
      GoogleGenerativeAI,
      HarmCategory,
      HarmBlockThreshold,
    } = require("@google/generative-ai");

    const apiKey = API_KEY;
    const genAI = new GoogleGenerativeAI(apiKey);

    const model = genAI.getGenerativeModel({
      model: "gemini-1.5-flash",
      systemInstruction:
        "gives details about songs like name release dates url to play that song , genre etc when song name is given\n\n",
    });

    const generationConfig = {
      temperature: 1,
      topP: 0.95,
      topK: 64,
      maxOutputTokens: 8192,
      responseMimeType: "application/json",
    };

    async function run() {
      const chatSession = model.startChat({
        generationConfig,
        // safetySettings: Adjust safety settings
        // See https://ai.google.dev/gemini-api/docs/safety-settings
        history: [
          {
            role: "user",
            parts: [{ text: "beleiver\n" }],
          },
          {
            role: "model",
            parts: [
              {
                text: "Please provide more context!  \"Believer\" could refer to many different songs.  To help me find the information you're looking for, tell me:\n\n* **Who is the artist?** (e.g., Imagine Dragons, The Monkees, etc.)\n* **What is the song's genre?** (e.g., rock, pop, country, etc.)\n* **Is there anything else that you remember about the song?** (e.g., a specific lyric, a music video, etc.)\n\nOnce I have this information, I can find the album release date, album name, and a URL to play the song. \n",
              },
            ],
          },
          {
            role: "user",
            parts: [{ text: "all the stars" }],
          },
          {
            role: "model",
            parts: [
              {
                text: "You're likely thinking of \"All of the Stars\" by Ed Sheeran.  Here's some information:\n\n* **Artist:** Ed Sheeran\n* **Song Title:** All of the Stars\n* **Release Date:**  February 20, 2014 (as a single)\n* **Album:**  The Fault in Our Stars (soundtrack)\n* **Genre:** Pop \n* **URL to Play:**  [https://www.youtube.com/watch?v=G24_V7i3Qgc](https://www.youtube.com/watch?v=G24_V7i3Qgc)\n\n\nLet me know if you'd like to find information on another song! \n",
              },
            ],
          },
          {
            role: "user",
            parts: [{ text: "shotta\n" }],
          },
          {
            role: "model",
            parts: [
              {
                text: '```json\n{"artist": "Lil Baby", "song_title": "Shotta Flow", "release_date": "October 20, 2017", "album": "Harder Than Ever", "genre": "Hip Hop", "url_to_play": "https://www.youtube.com/watch?v=eN62F9a0Zt0"}\n\n```',
              },
            ],
          },
        ],
      });

      const result = await chatSession.sendMessage(sng);
      //   console.log(result.response.text());
      res = result.response.text();

      //   console.log(res);

      const songDetails = JSON.parse(res);

      // Extract the artist
      const artist = songDetails.artist;

      console.log("Artist:", artist);
      console.log(songDetails.url_to_play);
    }

    run();

    //   resultDiv.textContent = `Result: ${JSON.stringify(result)}`;
  }
});
