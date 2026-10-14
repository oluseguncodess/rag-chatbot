import { useState } from "react";
import Querybar from "./query-bar";
import Chat from "./chat";
import { useChatMutation } from "../api/post-request";

export default function Chatapp() {
  const [messages, setMessages] = useState([]);

  const { mutate, isPending } = useChatMutation({
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: data.answer, sources: data.sources },
      ]);
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: error.message, isError: true },
      ]);
    },
  });

  function handleUserPrompt(question) {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    mutate(question);
  }

  return (
    <div className="w-full h-screen bg-[#A8BBA3] p-5 flex flex-col items-center">
        {messages.length === 0 && <p>Hey there!</p>}
      <Chat messages={messages} isLoading={isPending} />
      <Querybar onSubmitPrompt={handleUserPrompt} disabled={isPending} />
    </div>
  );
}
