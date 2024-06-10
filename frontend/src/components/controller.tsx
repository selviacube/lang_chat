import { useState, useRef, useEffect } from "react";
import Title from "./title";
import RecordMessage from "./RecordMessage";
import axios from "axios";
import ManageSystemPrompt from "./ManageSystemPrompt";
// import { get } from "http";
// import { set } from "date-fns";


// const host = "http://localhost:8000
// const host = "http://18.217.98.102:80";
const host = import.meta.env.VITE_API_URL;
console.log("API URL:", host);

let introduction = "";

const getIntroduction = (): Promise<string> => {
  console.log("Getting introduction...");
  return axios
    .get(host + "/get-introduction", {
      headers: { "Content-Type": "application/json" },
      responseType: "json",
    })
    .then((res) => {
      console.log("Controller|getIntroduction|introduction: ", res.data["introduction"]);
      return res.data["introduction"]; // Correctly returning the data from the function
    })
    .catch((err) => {
      console.error("Error in getIntroduction:", err.message);
      return "Unable to Retrieve Current Introduction."; // Returning a default or error message
    });
}



function controller() {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [showSystemPromptModal, setShowSystemPromptModal] = useState(false);
  const [currentGradeValue, setCurrentGradeValue] = useState(0);
  const tempMessages: any[] = [];
  

  // Display the Introduction Message
  useEffect(() => {
    getIntroduction().then((result) => {
      introduction = result;
      console.log("Introduction Loaded: ", introduction);  // This will log the resolved value
      if (tempMessages.length === 0) {
        console.log("Controller|messages.length: ", messages.length);
        axios
        .post(
          host + "/get-TTS",
          { message_input: introduction },
          {
            headers: { "Content-Type": "application/json" },
            responseType: "arraybuffer",
          }
        )
        .then((res: any) => {
          const blob = res.data;
          const audio = new Audio();
          audio.src = createBlobUrl(blob);
          console.log("Generated Audio URL:" + audio.src);

          const myMessage = { sender: "Dot", blobUrl: audio.src, messageText: introduction };
          tempMessages.push(myMessage);
          console.log("Length Inside useEffect: ", tempMessages.length);
          
          setMessages([myMessage]);
          initiateDialog(tempMessages);
        })
      }
      });
    console.log('Component mounted'); // This runs only once, after the initial render
  }, []); // Empty dependency array
  

  let messageText = "";
  // let messageGradeJSON = "";

  const lastMessageRef = useRef<HTMLDivElement | null>(null);

  const toggleSystemPromptModal = () => {
    setShowSystemPromptModal(!showSystemPromptModal);
  };


  useEffect(() => {
    // Scroll the last message into view whenever the messages update
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]); // Dependency array ensures this runs only when messages update
  // const [blob, setBlob] = useState("");

  const createBlobUrl = (data: any) => {
    const blob = new Blob([data], { type: "audio/mpeg" });
    const url = window.URL.createObjectURL(blob);
    console.log("Generated Audio URL:" + url);
    return url;
  };

  const getSystemPrompt = (): Promise<string> => {
    console.log("Getting system prompt...");
    return axios
      .get(host + "/get-system-prompt", {
        headers: { "Content-Type": "application/json" },
        responseType: "json",
      })
      .then((res) => {
        console.log("Controller|getSystemPrompt|System Prompt: ", res.data["system_prompt"]);
        return res.data["system_prompt"]; // Correctly returning the data from the function
      })
      .catch((err) => {
        console.error("Error in getSystemPrompt:", err.message);
        return "Unable to Retrieve Current System Prompt."; // Returning a default or error message
      });
  }
  

  const updateSystemPrompt = async (newPrompt: string) => {
    console.log("Updating system prompt to: ", newPrompt);
    await axios
      .post(
        host + "/store-alternative-system-prompt",
        { system_prompt: newPrompt },
        {
          headers: { "Content-Type": "application/json" },
          responseType: "json",
        }
      )
      .then((res: any) => {
        console.log("System Prompt Updated: ", res.data["message"]);
      });
    // setSystemPrompt(newPrompt);
  };


  const initiateDialog = async (tempMessages: any[]) => {
    console.log("Temp Messages Length: ", tempMessages.length);
    console.log("Initiating Dialog...");
    console.log("Temp Messages: ", [...tempMessages]);
    console.log("Temp Messages Length: ", tempMessages.length);
    console.log("Temp Messages After Length: ", [...tempMessages]);
    console.log("Temp Messages Length: ", tempMessages.length);
    let starting_prompt = "";
  
    if (tempMessages.length === 1) {
      try {
        const res = await axios.get(host + "/get-starting-prompt", {
          headers: { "Content-Type": "application/json" },
          responseType: "json",
        });
  
        console.log("starting-prompt: ", res.data["starting_prompt"]);
        starting_prompt = res.data["starting_prompt"];
  
        let firstMessageText = starting_prompt;
        const firstMessage = {
          sender: "Me",
          blobUrl: "",
          messageText: firstMessageText,
        };
  
        // const messagesArr = [...tempMessages, firstMessage];
        // setMessages(messagesArr);
  
        const textResponse = await axios.post(
          host + "/get-text-response",
          { message_input: firstMessage.messageText },
          {
            headers: { "Content-Type": "application/json" },
            responseType: "json",
          }
        );
  
        console.log("AI Response: ", textResponse.data["message"]);
        let firstMessageResponse = textResponse.data["message"];
  
        const ttsResponse = await axios.post(
          host + "/get-TTS",
          { message_input: firstMessageResponse },
          {
            headers: { "Content-Type": "application/json" },
            responseType: "arraybuffer",
          }
        );
  
        const blob = ttsResponse.data;
        const audio = new Audio();
        audio.src = createBlobUrl(blob);
  
        const DotMessage = {
          sender: "Dot",
          blobUrl: audio.src,
          messageText: firstMessageResponse,
        };
  
        setMessages((prevMessages) => [...prevMessages, DotMessage]);
        // setMessages((prevMessages) => [
        //   ...prevMessages.slice(0, -1),
        //   DotMessage,
        // ]);
        
        audio.play();
      } catch (err: any) {
        console.error("Error:", err.message);
        starting_prompt = "";
        return "Unable to Retrieve Current System Prompt.";
      }
    }
  };
  
  // ATTENTION: This function could be used to restart the dialog after a reset.
  // Without this function, you must reload the page to restart the dialog.
  // const restartDialog = async () => {
  //   try {
  //     const introduction = await getIntroduction();
  //     console.log("Introduction Loaded: ", introduction); // This will log the resolved value
  
  //     if (tempMessages.length === 0) {
  //       console.log("Controller | messages.length: ", messages.length);
  
  //       const res = await axios.post(
  //         host + "/get-TTS",
  //         { message_input: introduction },
  //         {
  //           headers: { "Content-Type": "application/json" },
  //           responseType: "arraybuffer",
  //         }
  //       );
  
  //       const blob = res.data;
  //       const audio = new Audio();
  //       audio.src = createBlobUrl(blob);
  //       console.log("Generated Audio URL: " + audio.src);
  
  //       const myMessage = { sender: "Dot", blobUrl: audio.src, messageText: introduction };
  //       tempMessages.push(myMessage);
  //       console.log("Length Inside useEffect: ", tempMessages.length);
  
  //       setMessages([myMessage]);
  //       initiateDialog(tempMessages);
  //     }
  //   } catch (err) {
  //     console.error("Error in restartDialog:", err.message);
  //   }
  // };
    

  const handleStop = async (blobUrl: string) => {
    setIsLoading(true);
    // setBlob(blobUrl);

    // Convert blob url to blob object
    fetch(blobUrl)
      .then((res) => res.blob())
      .then(async (blob) => {
        //Construct audio to send file
        const formData = new FormData();
        formData.append("file", blob, "myFile.wav");
        console.log("Sending audio to AI to ", host + "/transcribe-audio");
        await axios
          .post(host + "/transcribe-audio", formData, {
            headers: { "Content-Type": "audio/mpeg" },
            responseType: "json",
          })
          .then((res: any) => {
            console.log("Transcription: ", res.data["message"]);
            // const myMessage = { sender: "me", blobUrl, text: res.data.message };
            // const messagesArr = [...messages, myMessage];
            messageText = res.data["message"];

            // Append recorded message to messages array
            const myMessage = { sender: "Me", blobUrl, messageText };
            console.log("My Message: ", myMessage);
            const messagesArr = [...messages, myMessage];
            setMessages(messagesArr);

            // Convert blob url to blob object
            fetch(blobUrl)
              .then((res) => res.blob())
              .then(async (blob) => {
                //Construct audio to send file
                const formData = new FormData();
                formData.append("file", blob, "myFile.wav");
                console.log("Sending text to AI...");
                console.log("Message Text: ", messageText);
                // Get AI text response
                await axios
                  .post(
                    host + "/get-text-response",
                    { message_input: messageText },
                    {
                      headers: { "Content-Type": "application/json" },
                      responseType: "json",
                    }
                  )
                  .then(async (res: any) => {
                    console.log("AI Response: ", res.data["message"]);
                    messageText = res.data["message"];
                    // Get current grading evaluation
                    await axios
                      .post(
                        host + "/get-grade-response",
                        { message_input: messageText },
                        {
                          headers: { "Content-Type": "application/json" },
                          responseType: "json",
                        }
                      )
                      .then(async (res: any) => {
                        console.log("Grading Evaluation: ", res.data["grade"]);
                        // messageGradeJSON = res.data["grade"];
                        setCurrentGradeValue(res.data["grade"]);
                        // Get current system prompt
                        // await axios
                        //   .get(host + "/get-system-prompt", {
                        //     headers: { "Content-Type": "application/json" },
                        //     responseType: "json",
                        //   })
                        //   .then(async (res: any) => {
                        //     console.log("System Prompt: ", res.data["system_prompt"]);
                        //     messageText = res.data["system_prompt"];
                        //   });
                      });
                    // Convert response to audio speech
                    await axios
                      .post(
                        host + "/get-TTS",
                        { message_input: messageText },
                        {
                          headers: { "Content-Type": "application/json" },
                          responseType: "arraybuffer",
                        }
                      )
                      .then((res: any) => {
                        const blob = res.data;
                        const audio = new Audio();
                        audio.src = createBlobUrl(blob);

                        // Append to audio
                        const DotMessage = {
                          sender: "Dot",
                          blobUrl: audio.src,
                          messageText,
                        };
                        messagesArr.push(DotMessage);
                        setMessages(messagesArr);

                        // Play audio
                        setIsLoading(false);
                        audio.play();
                      })
                      .catch((err) => {
                        console.error(err.message);
                        setIsLoading(false);
                      });
                  });
              });
            // setIsLoading(false);
          });
      });
  };

  return (
    <div className="flex flex-col h-screen">
      <div>
        <Title
          messages={messages}
          setMessages={setMessages}
          displaySystemPromptModal={toggleSystemPromptModal}
          currentGrade={currentGradeValue.toString()}
        />
      </div>
      {/* Main content area needs to shrink/grow with available space */}
      <div className="flex-1 overflow-auto">
        <div className="p-2">
        {messages.map((audio, index) => (
            <div
              key={index + audio.sender}
              className={`mb-4 ${audio.sender === "Dot" ? "text-right" : ""}`}
            >
              <p
                className={`text-sm italic ${
                  audio.sender === "Dot"
                    ? "text-green-500 text-right mr-2"
                    : "text-blue-500 ml-2"
                }`}
              >
                {audio.sender}
              </p>

              <p dangerouslySetInnerHTML={{ __html: audio.messageText }} />

              <p>
                <div
                  className={`flex ${
                    audio.sender === "Dot" ? "justify-end" : ""
                  }`}
                >
                  {/* This div wraps the audio control to push it to the right */}
                  <audio
                    src={audio.blobUrl}
                    controls
                    className="flex-grow appearance-none max-w-xs"
                  />
                </div>
              </p>
            </div>
          ))}
          {messages.length === 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">
              Send Dot a message...
            </div>
          )}
          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Give me a second, please...
            </div>
          )}
          <div className="text-center" ref={lastMessageRef}>
            End of Dialog
          </div>
        </div>
      </div>

      {/* Footer: remains fixed at the bottom */}
      <div className="bg-gradient-to-r from-[#b6af64] to-[#629cd1] py-2 w-full">
        <div className="flex justify-center items-center">
          <RecordMessage handleStop={handleStop} />
        </div>
      </div>
      {showSystemPromptModal && (
        <ManageSystemPrompt
          getCurrentSystemPrompt={getSystemPrompt}
          updateSystemPrompt={updateSystemPrompt}
          onClose={toggleSystemPromptModal}
        />
      )}
    </div>
  );
}

export default controller;
