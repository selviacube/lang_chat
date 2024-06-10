import { useState, useEffect } from "react";

type Props = {
  getCurrentSystemPrompt: () => Promise<string>; // Function to get the current system prompt
  updateSystemPrompt: (promptText: string) => void; // Function to update the system prompt
  onClose: () => void; // Function to close the modal
};

function  ManageSystemPrompt({ getCurrentSystemPrompt, updateSystemPrompt, onClose  }: Props) {

  const [promptText, setPromptText] = useState(""); // State to store the prompt text
  
  useEffect(() => {
    // Asynchronously fetch the current system prompt when the component mounts
    const fetchPrompt = async () => {
      const currentPrompt = await getCurrentSystemPrompt();
      console.log("useEffect|Current System Prompt: ", currentPrompt);
      setPromptText(currentPrompt);
    };

    fetchPrompt();
  }, [getCurrentSystemPrompt]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-4 rounded-lg shadow-lg">
        <h2 className="font-bold text-lg mb-4">Manage System Prompt</h2>
        <textarea 
          className="w-full h-96 border p-2 mb-4"
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)} 
        ></textarea>
        <button
          className="bg-blue-500 text-white rounded px-4 py-2 mr-2"
          onClick={() => {
            updateSystemPrompt(promptText); // call the function to update the prompt
            onClose(); // close the modal
          }}
        >
          Update System Prompt
        </button>
        <button
          className="bg-gray-500 text-white rounded px-4 py-2 mr-2"
          onClick={() => {
            updateSystemPrompt(""); // call the function to update the prompt
            onClose(); // close the modal
          }}
        >
          Restore Default Prompt
        </button>
        <button
          className="bg-red-500 text-white rounded px-4 py-2"
          onClick={onClose}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

export default ManageSystemPrompt;
