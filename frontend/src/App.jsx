import React, { useState } from "react";
import Email from "./Email.jsx";
import Slack from "./slack.jsx";

const App = () => {
  const [view, setView] = useState("email");

  return (
    <div className="flex flex-col items-center p-4">
      <div className="mb-4 flex gap-4">
        <button 
          onClick={() => setView("email")} 
          className={`px-4 py-2 rounded-lg text-white ${view === "email" ? "bg-blue-500" : "bg-gray-500"}`}
        >
          Go to Email
        </button>
        <button 
          onClick={() => setView("slack")} 
          className={`px-4 py-2 rounded-lg text-white ${view === "slack" ? "bg-blue-500" : "bg-gray-500"}`}
        >
          Go to Slack
        </button>
      </div>
      <div className="w-full max-w-2xl">
        {view === "email" ? <Email /> : <Slack />}
      </div>
    </div>
  );
};

export default App;
