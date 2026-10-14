import { SendHorizonal } from "lucide-react";
import { useState } from "react";

export default function Querybar({ onSubmitPrompt, disabled }) {
  const [userPrompt, setUserPrompt] = useState("");
  
  function handleSubmit(e) {
    e.preventDefault();
    const question = userPrompt.trim();
    if (!question || disabled) return;

    onSubmitPrompt(question);
    setUserPrompt("");
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-full bg-[#FFF9D8] w-[90%] max-w-200 mt-5"
    >
      <div className="relative w-full h-full">
        <input
          className="py-4 px-5 w-full h-full placeholder:text-black rounded-full focus:border-2 focus:border-amber-200 focus:outline-none border-2 placeholder:opacity-80"          onChange={(e) => setUserPrompt(e.target.value)}
          value={userPrompt}
        />

        <button
          type="submit"
          disabled={disabled || !userPrompt.trim()}
          aria-label="Send question"
          className="absolute size-10 flex justify-center items-center bottom-0 right-2 top-1.5 bg-[#A8BBA3] rounded-full hover:bg-[#2A835F] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <SendHorizonal className="hover:text-white" />
        </button>
      </div>
    </form>
  );
}